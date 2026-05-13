from errno import ENOENT
from requests import get
from requests.exceptions import ConnectionError
from yaml import safe_load
from os import path, strerror
from loguru import logger

from api import Domain, NamesiloAPI


class DynDNS:
    def __init__(self):
        self.config = self._get_config()

    def _get_my_ip(self, server: str) -> str:
        try:
            return get(server).json()["ip"]
        except ConnectionError:
            return None

    def _set_record(self, domain_obj: Domain, rtype: str, ip: str) -> None:
        pass

    def _get_config(self) -> dict:
        location = "/etc/namesilo_dyndns/config.yaml"
        user_config_file = path.join(
            path.expanduser("~"), ".config", "namesilo_dyndns.yaml"
        )
        if path.exists(user_config_file):
            location = user_config_file
        elif not path.exists(location):
            raise FileNotFoundError(ENOENT, strerror(ENOENT), location)
        with open(location, "r") as yamlfile:
            config = safe_load(yamlfile)
        if "key" not in config:
            raise KeyError("Key 'key' missing")
        if "domains" not in config:
            raise KeyError("Key 'domains' missing")
        if "ipv4_server" not in config:
            config["ipv4_server"] = "https://ip.dhoessl.de"
            logger.warning(
                f"ipv4_server not configured. Using {config['ipv4_server']}"
            )
        if "ipv6_server" not in config:
            config["ipv6_server"] = "https://ipv6.dhoessl.de"
            logger.warning(
                f"ipv6_server not configured. Using {config['ipv6_server']}"
            )
        for domain in config["domains"]:
            domain_config = config["domains"][domain]
            if (
                (
                    "ipv4" not in domain_config or not domain_config["ipv4"]
                ) and (
                    "ipv6" not in domain_config or not domain_config["ipv6"]
                )
            ):
                raise KeyError(f"Key 'ipv4' or 'ipv6' missing for {domain}")
            if "subdomain" not in domain_config:
                raise KeyError(f"Key 'subdomain' missing for {domain}")
            if "ipv4" not in domain_config:
                config["domains"][domain]["ipv4"] = False
            if "ipv6" not in domain_config:
                config["domains"][domain]["ipv6"] = False
        return config

    def run(self) -> None:
        logger.info("Starting Update")
        for domain in self.config["domains"]:
            domain_config = self.config["domains"][domain]
            api_key = domain_config["key"] if "key" in domain_config else self.config["key"]  # noqa: E501
            records = []
            if domain_config["ipv4"]:
                my_ip_v4 = self._get_my_ip(self.config["ipv4_server"])
                if my_ip_v4:
                    records.append({
                        "host": domain_config["subdomain"],
                        "type": "A",
                        "value": my_ip_v4,
                        "ttl": "3600"
                    })
            if domain_config["ipv6"]:
                my_ip_v6 = self._get_my_ip(self.config["ipv6_server"])
                if my_ip_v6:
                    records.append({
                        "host": domain_config["subdomain"],
                        "type": "AAAA",
                        "value": my_ip_v6,
                        "ttl": "3600"
                    })
            if not records:
                logger.warning(f"Could not fetch any IP for {domain}")
                exit(0)
            logger.debug(f"Updates for {domain} with {records}")
            ns_domain = Domain(domain, NamesiloAPI(api_key), records)
            for record in ns_domain.records:
                logger.debug(f"Records: {record}")
                if record["state"] == "updated" or record["state"] == "added":
                    logger.info(
                        f"Record changed. domain: {ns_domain.domain} - "
                        f"subdomain: {record['host']} - type: {record['type']}"
                        f"ip: {record['value']}"
                    )
        logger.info("Update Finished")
