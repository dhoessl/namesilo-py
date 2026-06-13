from requests import get
from .errors import NamesiloApiReturnError
from time import sleep

# Reponse Code 429 too many requests (max 60 in a minute)


class NamesiloAPI:
    def __init__(self, key: str) -> None:
        self.uri = "https://www.namesilo.com/api/"
        self.options = f"?version=1&type=json&key={key}"
        self.max_retries = 3
        self.timeout = 65

    def send_request(self, operation: str, request_options: str) -> dict:
        retry = 0
        while True:
            response = get(
                f"{self.uri}{operation}{self.options}{request_options}",
                headers={"User-Agent": "dhoessl-namesilo-py (python-requests)"}
            )
            retry += 1
            if response.status_code not in [429]:
                break
            if retry > self.max_retries:
                raise RuntimeError(
                    f"Max retires for {operation} on {request_options} exceded"
                )
            sleep(self.timeout)
        response = response.json()
        if response["reply"]["code"] != 300:
            raise NamesiloApiReturnError(
                operation, request_options, response["reply"]["code"],
                response["reply"]["detail"]
            )
        return response["reply"]
