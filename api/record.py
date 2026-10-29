from __future__ import annotations
from typing import TYPE_CHECKING
from .errors import RecordExistsError

# from loguru import logger


if TYPE_CHECKING:
    from .domain import Domain
    from .api import NamesiloAPI


class Record:
    def __init__(
        self, api: NamesiloAPI, domain: Domain, rtype: str, host: str,
        value: str, ttl: int = 7207, distance: int = 10, rid: str = None
    ) -> None:
        self.api = api
        self.id = rid
        self.domain = domain
        self.type = rtype
        self.host = host
        self.value = value
        self.ttl = ttl
        self.distance = distance

    def add(self) -> None:
        if self.id:
            raise RecordExistsError(self.id, self.host, self.type)
        request_options = (
            f"&domain={self.domain}&rrhost={self.host}&rrvalue={self.value}"
            f"&rrttl={self.ttl}&rrtype={self.type}"
        )
        if self.type == "MX":
            request_options += f"&distance={self.distance}"
        self.id = self.api.send_request("dnsAddRecord", request_options)

    def remove(self) -> None:
        self.api.send_request(
            "dnsDeleteRecord", f"&domain={self.domain}&rrid={self.id}"
        )

    def update(self) -> None:
        request_options = (
            f"&domain={self.domain}&rrhost={self.host}"
            f"&rrvalue={self.value}&rrttl={self.ttl}"
            f"&rrid={self.id}"
        )
        if self.type == "MX":
            request_options += f"&distance={self.distance}"
        self.id = self.api.send_request(
            "dnsUpdateRecord", request_options
        )["record_id"]
