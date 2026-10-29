from __future__ import annotations
from typing import TYPE_CHECKING
from prettytable import PrettyTable

from .record import Record


if TYPE_CHECKING:
    from .api import NamesiloAPI


class Domain:
    def __init__(self, api: NamesiloAPI, domain: str) -> None:
        self.api = api
        self.domain = domain
        self.records = []
        self.update_record_list()

    def get_data_as_table(self) -> PrettyTable:
        table = PrettyTable()
        table.align = "l"
        table.field_names = ["ID", "Type", "Host", "TTL", "Distance", "Value"]
        for record in self.records:
            table.add_row(record.get_table_row())
        table_str = table.get_string(sortby="Type")
        print(f"{table_str}")

    def update_record_list(self) -> None:
        self.records = []
        response = self.api.send_request(
            "dnsListRecords",
            f"&domain={self.domain}"
        )
        if (
            isinstance(response, str)
            and response == "No DNS records associated with this domain"
        ):
            return None
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

    def remove_record(self, host: str, rtype: str) -> None:
        for record in self.records:
            if record.host == host and record.type == rtype:
                record.remove()
                self.records.remove(record)
                return None
        return None

    def remove_record_by_id(self, rid: str) -> None:
        for record in self.records:
            if rid == record.id:
                record.remove()
                self.records.remove(record)
                return None
        return None

    def update_record(self, rid: str, **kwargs) -> None:
        if not kwargs:
            return None
        for record in self.records:
            if rid != record.id:
                continue
            if (
                (
                    "host" in kwargs
                    and kwargs["host"] != record.host
                ) or (
                    "rtype" in kwargs
                    and kwargs["rtype"] != record.type
                )
            ):
                self.remove_record_by_id(record.id)
                ttl = kwargs["ttl"] if "ttl" in kwargs else 3600
                distance = kwargs["distance"] if "distance" in kwargs else 0
                self.add_record(
                    kwargs["host"], kwargs["rtype"], kwargs["value"], int(ttl),
                    int(distance)
                )
            if "value" in kwargs and kwargs["value"] != record.value:
                record.value = kwargs["value"]
            if "ttl" in kwargs and int(kwargs["ttl"]) != int(record.ttl):
                record.ttl = int(kwargs["ttl"])
            if (
                "distance" in kwargs
                and int(kwargs["distance"]) != int(record.distance)
            ):
                record.distance = int(kwargs["distance"])
            record.update()
