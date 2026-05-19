from .api import NamesiloAPI
from .errors import (
    RecordExistsError, RecordNotFoundError,
    RecordIdNotFoundError, RecordInvalidTypeError
)

from loguru import logger


class Record:
    def __init__(
        self, rid: str, rtype: str, host: str, value: str, domain: str,
        api: NamesiloAPI, ttl: str = "7207", distance: str = "10"
    ) -> None:
        self.api = api
        self.id = rid
        self.domain = domain
        self.type = rtype
        self.host = host
        self.value = value
        self.ttl = ttl
        self.distance = distance
        self._validate_type()

    def _validate_type(self) -> bool:
        """ Checks if self.type is a valid value """
        if self.type not in RecordInvalidTypeError.ALLOWED_TYPES:
            raise RecordInvalidTypeError(
                self.id, self.type, self.host, self.domain
            )
        return True

    def _list_api(self) -> list:
        return self.api.send_request(
            "dnsListRecords", f"&domain={self.domain}"
        )["resource_record"]

    def _add_api(self) -> str:
        request_options = (
            f"&domain={self.domain}&rrhost={self.host}"
            f"&rrvalue={self.value}&rrttl={self.ttl}"
            f"&rrtype={self.type}"
        )
        if self.type == "MX":
            request_options += f"&distance={self.distance}"
        return self.api.send_request(
            "dnsAddRecord", request_options
        )["record_id"]

    def _update_api(self) -> str:
        request_options = (
            f"&domain={self.domain}&rrhost={self.host}"
            f"&rrvalue={self.value}&rrttl={self.ttl}"
            f"&rrid={self.id}"
        )
        if self.type == "MX":
            request_options += f"&distance={self.distance}"
        return self.api.send_request(
            "dnsUpdateRecord", request_options
        )["record_id"]

    def _delete_api(self) -> bool:
        self.api.send_request(
            "dnsDeleteRecord", f"&domain={self.domain}&rrid={self.id}"
        )
        return True

    def _record_id_exists(self) -> bool:
        reply_records = self._list_api()
        for record in reply_records:
            if record["record_id"] == self.id:
                return True
        raise RecordIdNotFoundError(self.id)

    def _type_change(self) -> bool:
        reply_records = self._list_api()
        for record in reply_records:
            if record["record_id"] != self.id:
                continue
            if record["type"] == self.type:
                return False
            else:
                return True
        return False

    def _record_exists(self, record: dict) -> bool:
        if (
            self.type == record["type"]
            and self.host == record["host"]
        ):
            self.id = record["record_id"]
            return True
        elif (
            self.type == record["type"]
            and (self.host == "" or self.host is None)
            and record["host"] == "@"
        ):
            self.id = record["record_id"]
            return True
        return False

    def exists(self) -> bool:
        reply_records = self._list_api()
        if type(reply_records) is dict:
            if self._record_exists(reply_records):
                return True
        elif type(reply_records) is list:
            for record in reply_records:
                if self._record_exists(record):
                    return True
        raise RecordNotFoundError(self.id, self.host, self.type)

    def add(self) -> str:
        try:
            self.exists()
            raise RecordExistsError(self.id, self.host, self.type)
        except RecordNotFoundError:
            self.id = self._add_api()
            return True

    def update(self) -> bool:
        try:
            self._record_id_exists()
            self._validate_type()
            if self._type_change():
                self._delete_api()
                self.id = self._add_api()
            else:
                self.id = self._update_api()
            return True
        except RecordIdNotFoundError:
            logger.debug(f"Record {self.id} not found")
            return False
        except RecordInvalidTypeError:
            logger.warning(f"Record {self.id} invalid Type")
            return False

    def delete(self) -> bool:
        try:
            self._record_id_exists()
            if self._delete_api():
                self.id = None
                return True
            else:
                return False
        except RecordIdNotFoundError:
            return False

    def show(self) -> dict:
        """ Shows record data """
        return {
            "id": self.id,
            "domain": self.domain,
            "host": self.host,
            "type": self.type,
            "value": self.value,
            "ttl": self.ttl,
            "distance": self.distance
        }
