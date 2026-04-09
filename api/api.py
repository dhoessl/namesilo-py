from requests import get
from .errors import NamesiloApiReturnError


class NamesiloAPI:
    def __init__(self, key: str) -> None:
        self.uri = "https://www.namesilo.com/api/"
        self.options = f"?version=1&type=json&key={key}"

    def send_request(self, operation: str, request_options: str) -> dict:
        response = get(f"{self.uri}{operation}{self.options}{request_options}")
        response = response.json()
        if response["reply"]["code"] != 300:
            raise NamesiloApiReturnError(
                operation, request_options, response["reply"]["code"],
                response["reply"]["detail"]
            )
        return response["reply"]
