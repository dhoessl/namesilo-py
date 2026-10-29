from .api import NamesiloAPI
from .record import Record


class Domain:
    def __init__(self, api: NamesiloAPI, domain: str, records: list) -> None:
        self.api = api
        self.domain = domain
        self.records = []
        self.add_records(records)

    def update_record_list(self) -> None:
        self.records = []
        response = self.api.send_request(
            "dnsListRecords",
            f"domain={self.domain}"
        )
        self._create_records(response["resource_record"])

    def add_records(self, records: list | dict) -> None:
        if isinstance(records, dict):
            records = [records]
        for record in records:
            self.add_record(
                record["host"], record["type"], record["value"],
                int(record["ttl"]), int(record["distance"]), record["id"]
            )

    def add_record(
        self, host: str, rtype: str, value: str, ttl: int = 3600,
        distance: int = 10, rid: str = None
    ) -> None:
        new_record = Record(
            api=self.api, domain=self, rtype=rtype, host=host, value=value,
            ttl=int(ttl), distance=int(distance)
        )
        new_record.add()
        self.records.append(new_record)

    def remove_record(self, host: str, rtype: str, rid: str = None) -> None:
        for record in self.records:
            if (
                (
                    rid
                    and record.id == rid
                ) or (
                    not rid
                    and record.host == host
                    and record.type == rtype
                )
            ):
                record.remove()
                self.records.remove(record)
                return None

    def update_record(
        self, host: str, rtype: str, value: str, ttl: int = 3600,
        distance: int = 10, rid: str = None
    ) -> None:
        for record in self.records:
            if record.id == rid:
                if (
                    record.host != host or
                    record.type != rtype
                ):
                    record.remove()
                    record.host = host
                    record.type = rtype
                    record.value = value
                    record.ttl = int(ttl)
                    record.distance = int(distance)
                    record.add()
                    return None
                elif (
                    record.value != value
                    or record.ttl != int(ttl)
                    or (
                        record.type == "MX"
                        and record.distance != int(distance)
                    )
                ):
                    record.value = value
                    record.ttl = int(ttl)
                    if record.type == "MX":
                        record.distance = int(distance)
                    record.update()
                    return None
                else:
                    return None
            if (
                record.id != rid
                and record.host == host
                and record.type == rtype
            ):
                if (
                    record.value != value
                    or record.ttl != int(ttl)
                    or (
                        record.type == "MX"
                        and record.distance != int(distance)
                    )
                ):
                    record.value = value
                    record.ttl = int(ttl)
                    if record.type == "MX":
                        record.distance = int(distance)
                    record.update()
                return None
        return None
