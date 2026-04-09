from .api import NamesiloAPI
from .record import Record
from .errors import (
    DomainRecordStateError, RecordNotFoundError, RecordExistsError
)


class Domain:
    def __init__(
        self, domain: str, api: NamesiloAPI, records: list
    ) -> None:
        self.api = api
        self.domain = domain
        self.records = records
        self.update_dns()

    def _records_equal(self, record: dict, new_record: Record) -> bool:
        if (
            record["type"] == new_record.type
            and record["host"] == new_record.host
            and record["value"] == new_record.value
            and str(record["ttl"]) == new_record.ttl
        ):
            if record["type"] == "MX" and new_record.type == "MX":
                if str(record["distance"]) == new_record.distance:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False

    def update_dns(self) -> None:
        for record in self.records:
            record["ttl"] = record["ttl"] if "ttl" in record else "7207"
            if record["type"] == "MX" and "distance" not in record:
                record["distance"] = "10"
            else:
                record["distance"] = None
            new_record = Record(
                None, record["type"], record["host"], record["value"],
                self.domain, self.api, str(record["ttl"]),
                str(record["distance"])
            )
            if "state" not in record or record["state"] == "present":
                try:
                    # new_record.exists() will raise RecordNotFound Error if
                    # it does not exist
                    new_record.exists()
                    if (
                        not self._records_equal(record, new_record)
                        and new_record.update()
                    ):
                        record["state"] = "updated"
                    else:
                        record["state"] = "present"
                except RecordNotFoundError:
                    try:
                        new_record.add()
                        record["state"] = "added"
                    except RecordExistsError:
                        record["state"] = "present"
                continue
            elif "state" in record and record["state"] == "absent":
                try:
                    new_record.exists()
                    if new_record.delete():
                        record["state"] = "removed"
                    else:
                        record["state"] = "absent"
                    continue
                except RecordNotFoundError:
                    record["state"] = "absent"
            else:
                raise DomainRecordStateError(
                    self.domain, record["host"], record["type"],
                    record["state"]
                )

    def list(self) -> list:
        records = []
        api_records = self.api.send_request(
            "dnsListRecords", "&domain={self.domain}"
        )["resource_record"]
        for record in api_records:
            records.append(Record(
                record["record_id"], record["type"], record["host"],
                record["value"], self.domain, self.api, record["ttl"],
                record["distance"]
            ))
        return records
