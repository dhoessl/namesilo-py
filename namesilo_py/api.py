from requests import get


class NamesiloAPI:
    def __init__(self, key: str) -> None:
        self.uri = "https://www.namesilo.com/api/"
        self.options = f"?version=1&type=json&key={key}"

    def get_url(self, operation: str) -> str:
        return f"{self.uri}{operation}{self.options}"

    def send_request(self, request: str) -> dict:
        response = get(request)
        response = response.json()
        if response["reply"]["code"] != 300:
            raise RuntimeError(
                f"Error {response['reply']['code']} in Response on "
                f"{response['request']['operation']}!"
                f"Error: {response['reply']['detail']}"
            )
        return response["reply"]

    def list(self, domain: str) -> dict:
        reply = self.send_request(
            f"{self.get_url('dnsListRecords')}&domain={domain}"
        )
        return reply["resource_record"]
