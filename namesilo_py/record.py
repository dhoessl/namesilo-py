from .api import NamesiloAPI


class Record:
    ALLOWED_RESOURCE_TYPES = ["A", "AAAA", "CNAME", "MX", "TXT", "SRV", "CCA"]

    def __init__(
        self, rid: str, rtype: str, host: str, value: str, domain: str,
        api: NamesiloAPI, ttl: str = "7207", distance: str = "10"
    ) -> None:
        self.api = api
        self.id = rid
        self.type = rtype
        self.host = host
        self.value = value
        self.domain = domain
        self.ttl = ttl
        self.distance = distance
        self._validate_type()

    def _list_api(self) -> list:
        reply = self.api.send_request(
            f"{self.api.get_url('dnsListRecords')}&domain={self.domain}"
        )
        return reply["resource_record"]

    def _add_api(self) -> str:
        request = (
            f"{self.api.get_url('dnsAddRecord')}&domain={self.domain}"
            f"&rrhost={self.host}&rrvalue={self.value}&rrttl={self.ttl}"
            f"&rrtype={self.rtype}"
        )
        if self.type == "MX":
            request += f"&distance={self.distance}"
        return self.api.send_request(request)["record_id"]

    def _update_api(self) -> str:
        request = (
            f"{self.api.get_url('dnsUpdateRecord')}&domain={self.domain}"
            f"&domain={self.domain}&rrhost={self.host}"
            f"&rrvalue={self.value}&rrttl={self.ttl}"
            f"&rrid={self.id}"
        )
        if self.type == "MX":
            request += f"&distance={self.distance}"
        return self.api.send_request(request)["record_id"]

    def _delete_api(self) -> bool:
        self.api.send_request(
            f"{self.api.get_url('dnsDeleteRecord')}"
            f"&domain={self.domain}&rrid={self.id}"
        )
        return True

    def _validate_type(self) -> bool:
        """ Checks if self.type is a valid value """
        if self.type in self.ALLOWED_RESOURCE_TYPES:
            return True
        return False

    def _record_id_exists(self, api: NamesiloAPI) -> bool:
        reply_records = self._list_api()
        for record in reply_records:
            if record["record_id"] == self.id:
                return True
        return False

    def exists(self) -> bool:
        reply_records = self._list_api()
        for record in reply_records:
            if (
                self.type == record["type"]
                and self.host == record["host"]
                and self.value == record["value"]
            ):
                self.id = record["record_id"]
                return True
        return False

    def add(self) -> bool:
        if self.exists():
            return False
        return self._add_api()

    def update(self) -> bool:
        if not self._record_id_exists():
            return False
        return self._update_api()

    def delete(self) -> bool:
        if not self._record_id_exists():
            return False
        return self._delete_api()
