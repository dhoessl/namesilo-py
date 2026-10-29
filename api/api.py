from requests import get
from .errors import NamesiloApiReturnError
from time import sleep
from .domain import Domain

# NOTE: Reponse Code 429 too many requests (max 60 in a minute)


class NamesiloAPI:
    def __init__(self, key: str, domains: list[str]) -> None:
        self.uri = "https://www.namesilo.com/api/"
        self.options = f"?version=1&type=json&key={key}"
        self.max_retries = 3
        self.timeout = 65
        self.domains = self.get_domains(domains)

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

    def get_domains(self, domains: list[str]) -> Domain:
        domain_list = []
        for domain in domains:
            response = self.send_request(
                "dnsListRecords", f"&domain={domain}"
            )
            domain_list.append(
                Domain(self, domain, response["resource_record"])
            )
        return domain_list
