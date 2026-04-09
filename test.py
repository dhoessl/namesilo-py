from __future__ import annotations
from requests import get


class NamesiloAPI:
    def __init__(self, key: str) -> None:
        # self.key = key
        self.api_uri = "https://www.namesilo.com/api/"
        self.api_options = f"?version=1&type=json&key={key}"

    def list_records(self, domain: str) -> list:
        response = get(
            f"{self.api_uri}dnsListRecords{self.api_options}&domain={domain}"
        )
        if response.json()["reply"]["code"] != 300:
            raise RuntimeError(
                f"Error {response.json()['reply']['code']} in Response on "
                f"listing Records! Error: {response.json()['reply']['detail']}"
            )
        return response.json()["reply"]["resource_record"]

    def add_or_update_record(self, record: Record) -> str:
        record_exists = self.record_exists(record.id, record.domain)
        if record_exists:
            operation = "dnsUpdateRecord"
        else:
            operation = "dnsAddRecord"
        request = (
            f"{self.api_uri}{operation}{self.api_options}"
            f"&domain={record.domain}&rrhost={record.host}"
            f"&rrvalue={record.value}&rrttl={record.ttl}"
        )
        if record.type == "MX":
            request += f"&distance={record.distance}"
        if record_exists:
            request += "&rrid={record.id}"
        else:
            request += f"&rrtype={record.rtype}"
        response = get(request)
        if response.json()["reply"]["code"] != 300:
            raise RuntimeError(
                f"Error {response.json()['reply']['code']} in Response on "
                f"{operation}! Error: {response.json()['reply']['detail']}"
            )
        return response.json()["reply"]["record_id"]

    def delete_record(self, record: Record) -> bool:
        if not self.record_exists(record.id, record.domain):
            return True
        response = get(
            f"{self.api_uri}dnsDeleteRecord{self.api_options}"
            f"&domain={record.domain}&rrid={record.id}"
        )
        if response.json()["reply"]["code"] != 300:
            raise RuntimeError(
                f"Error {response.json()['reply']['code']} in Response on "
                f"dnsDeleteRecord! Error: {response.json()['reply']['detail']}"
            )
        return True

    def record_exists(self, record_id: str, domain: str) -> bool:
        records = self.list_records(domain)
        for record in records:
            if record.id == record_id:
                return True
        return False


class Record:
    ALLOWED_RESOURCE_TYPES = ["A", "AAAA", "CNAME", "MX", "TXT", "SRV", "CCA"]

    def __init__(
        self, rid: str, rtype: str, host: str, value: str, domain: str,
        ttl: str = "7207", distance: str = "10"
    ) -> None:
        self.id = rid
        self.type = rtype
        self.host = host
        self.value = value
        self.domain = domain
        self.ttl = ttl
        self.distance = distance
        self._validate_type()

    def _validate_type(self) -> bool:
        """ Checks if self.type is a valid value """
        if self.type in self.ALLOWED_RESOURCE_TYPES:
            return True
        # Raise ValueError if self.type is not a valid value
        allowed_types_str = ", ".join(self.ALLOWED_RESOURCE_TYPES)
        raise ValueError(f"Record Type must be one of {allowed_types_str}")

    def add_or_update(self, api: NamesiloAPI) -> bool:
        if self.id:
            raise ValueError("Record ID should be None for new records")
        self._validate_type()
        try:
            self.id = api.add_or_update_record(self)
            return True
        except RuntimeError:
            return False

    def delete(self, api: NamesiloAPI) -> bool:
        try:
            return api.delete_record(self)
        except RuntimeError:
            return False


class DomainRecords:
    def __init__(self, domain: str, api: NamesiloAPI) -> None:
        self.api = api
        self.domain = domain
        self.records = self.get_records()

    def get_records(self) -> list:
        records = self.api.list_records(self.domain)
        formated_records = []
        for record in records:
            formated_records.append(
                Record(
                    record["record_id"], record["type"], record["host"],
                    record["value"], self.domain, record["ttl"],
                    record["distance"]
                )
            )
        return formated_records

    def create_record(
        self, rtype: str, host: str, value: str, ttl: str = "7207",
        distance: str = "10"
    ) -> bool:
        record = Record(None, rtype, host, value, self.domain, ttl, distance)
        if record.add_or_update(self.api):
            self.records.append(record)
            return True
        return False
