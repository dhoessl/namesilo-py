from socket import AF_INET, AF_INET6
import urllib3.util.connection
from requests import get
from requests.exceptions import ConnectionError
from loguru import logger
from .config import get_config

from namesilo import NamesiloAPI


class DynDNS:
    def __init__(self):
        self.config = get_config()

    def _get_my_ip(self, server: str) -> str:
        try:
            urllib3.util.connection.allowed_gai_family = lambda: AF_INET
            return get(server).json()["ip"]
        except ConnectionError:
            return None

    def _get_my_ipv6(self, server: str) -> str:
        try:
            urllib3.util.connection.allowed_gai_family = lambda: AF_INET6
            return get(server).json()["ip"]
        except ConnectionError:
            return None

    def run(self) -> None:
        logger.info("Starting Update...")
        for domain in self.config["domains"]:
            domain_config = self.config["domains"][domain]
            if "key" in domain_config:
                api_key = domain_config["key"]
            else:
                api_key = self.config["key"]
            if domain_config["ipv4"]:
                ipv4 = self._get_my_ip(self.config["ipv4_server"])
            else:
                ipv4 = None
            if domain_config["ipv6"]:
                ipv6 = self._get_my_ipv6(self.config["ipv6_server"])
            else:
                ipv6 = None
            urllib3.util.connection.allowed_gai_family = lambda: AF_INET
            api = NamesiloAPI(api_key, [domain])
            record_v4_found = False
            record_v6_found = False
            for record in api.get_domain(domain).records:
                if (
                    ipv4
                    and record.type == "A"
                    and record.host == domain_config["subdomain"]
                ):
                    record_v4_found = True
                    if record.value != ipv4:
                        record.value = ipv4
                        record.ttl = 3600
                        record.update()
                        logger.info(
                            f"Ipv4 Record Update to {ipv4} for "
                            f"{domain_config['subdomain']}.{domain}"
                        )
                elif (
                    ipv6
                    and record.type == "AAAA"
                    and record.host == domain_config["subdomain"]
                ):
                    record_v6_found = True
                    if record.value != ipv6:
                        record.value = ipv6
                        record.ttl = 3600
                        record.update()
                        logger.info(
                            f"Ipv6 Record Update to {ipv6} for "
                            f"{domain_config['subdomain']}.{domain}"
                        )
            if not record_v4_found and ipv4:
                api.get_domain(domain).add_record(
                    domain_config["subdomain"], "A", ipv4, 3600
                )
                logger.info(
                    f"Ipv4 Record created with {ipv4} for "
                    f"{domain_config['subdomain']}.{domain}"
                )
            if not record_v6_found and ipv6:
                api.get_domain(domain).add_record(
                    domain_config["subdomain"], "AAAA", ipv6, 3600
                )
                logger.info(
                    f"Ipv6 Record created with {ipv6} for "
                    f"{domain_config['subdomain']}.{domain}"
                )
        logger.info("Update completed!")
