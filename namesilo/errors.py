class GenericRecordError(Exception):
    def __init__(self, msg: str = "Generic Record Error") -> None:
        super().__init__(msg)


class RecordValueError(GenericRecordError):
    def __init__(self, rid: str, value: str) -> None:
        super().__init__(f"Record: {rid} => Value {value} is not set!")
        self.value = value
        self.id = rid


class RecordExistsError(GenericRecordError):
    def __init__(self, rid: str, host: str, rtype: str) -> None:
        super().__init__(
            f"Record with host {host} and type {rtype} already exists!"
        )
        self.id = rid
        self.host = host
        self.type = rtype


class RecordNotFoundError(GenericRecordError):
    def __init__(self, rid: str, host: str, rtype: str) -> None:
        super().__init__(f"Record host {host} and type {rtype} was not found!")
        self.id = rid
        self.host = host
        self.type = rtype


class RecordIdNotFoundError(GenericRecordError):
    def __init__(self, rid: str) -> None:
        super().__init__(f"Record with ID {rid} was not found!")
        self.id = rid


class RecordInvalidTypeError(GenericRecordError):
    ALLOWED_TYPES = ["A", "AAAA", "CNAME", "MX", "TXT", "SRV", "CCA"]

    def __init__(self, rid: str, rtype: str, host: str, domain: str) -> None:
        super().__init__(
            f"Type {rtype} is Invalid. Must be one of {self.ALLOWED_TYPES}"
        )
        self.id = rid
        self.type = rtype
        self.host = host
        self.domain = domain


class RecordListEmptyError(GenericRecordError):
    def __init__(self, domain: str) -> None:
        super().__init__(f"Domain {domain} record list is empty!")
        self.domain = domain


class GenericDomainError(Exception):
    def __init__(self, msg: str = "Generic Domain Error") -> None:
        super().__init__(msg)


class DomainRecordStateError(GenericDomainError):
    def __init__(self, domain: str, host: str, rtype: str, state: str) -> None:
        super().__init__(
            f"state must be either 'present' or 'absent'. given {state}"
        )
        self.domain = domain
        self.host = host
        self.type = rtype
        self.state = state


class GenericNamesiloApiError(Exception):
    def __init__(self, msg: str = "Generic Namesilo API Error") -> None:
        super().__init__(msg)


class NamesiloApiReturnError(GenericNamesiloApiError):
    def __init__(
        self, operation: str, request_options: str, code: str, detail: str
    ) -> None:
        super().__init__(
            f"Call on Endpoint {operation} failed with Code {code}. "
            f"Details: {detail}"
        )
        self.operation = operation
        self.code = code
        self.detail = detail
        self.request_options = request_options
