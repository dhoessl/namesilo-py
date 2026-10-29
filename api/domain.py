from __future__ import annotations
from typing import TYPE_CHECKING
from .record import Record


if TYPE_CHECKING:
    from .api import NamesiloAPI


class Domain:
    def __init__(self, api: NamesiloAPI, domain: str) -> None:
        self.api = api
        self.domain = domain
        self.records = []
        self.update_record_list()

    def update_record_list(self) -> None:
        self.records = []
        response = self.api.send_request(
            "dnsListRecords",
            f"domain={self.domain}"
        )
        self._parse_records(response["resource_record"])

    def _parse_records(self, records: list | dict) -> None:
        if isinstance(records, dict):
            records = [records]
        for record in records:
            self.records.append(
                Record(
                    self.api, self.domain, record["type"], record["host"],
                    record["value"], int(record["ttl"]),
                    int(record["distance"]), record["record_id"]
                )
            )

    def add_record(
        self, host: str, rtype: str, value: str, ttl: int = 3600,
        distance: int = 10, rid: str = None
    ) -> None:
        new_record = Record(
            self.api, self.domain, rtype, host, value, int(ttl), int(distance)
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
