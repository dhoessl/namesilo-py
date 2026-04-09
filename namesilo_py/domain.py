from .api import NamesiloAPI
from .record import Record


class Domain:
    def __init__(
        self, domain: str, api: NamesiloAPI, records: list
    ) -> None:
        self.api = api
        self.domain = domain
        self.records = records
        self.update_dns()

    def update_dns(self) -> None:
        for record in self.records:
            record["ttl"] = record["ttl"] if "ttl" in record else "7207"
            if record["type"] == "MX" and "distance" not in record:
                record["distance"] = "10"
            else:
                record["distance"] = None
            new_record = Record(
                None, record["type"], record["host"], record["value"],
                self.domain, self.api, record["ttl"], record["distance"]
            )
            if "state" not in record or record["state"] == "present":
                if new_record.exists():
                    if new_record.update():
                        record["state"] = "updated"
                    else:
                        record["state"] = "present"
                    continue
                else:
                    if new_record.add():
                        record["state"] = "added"
                    else:
                        record["state"] = "present"
                    continue
            elif "state" in record and record["state"] == "absent":
                if new_record.exists():
                    if new_record.delete():
                        record["state"] = "removed"
                    else:
                        record["state"] = "absent"
                    continue
            else:
                raise ValueError(
                    "state must either be 'present' or 'absent'"
                )

    def list(self) -> list:
        records = []
        api_records = self.api.list(self.domain)
        for record in api_records:
            records.append(Record(
                record["record_id"], record["type"], record["host"],
                record["value"], self.domain, self.api, record["ttl"],
                record["distance"]
            ))
        return records
