from yaml import safe_load
from pathlib import Path
from errno import ENOENT
from os import strerror
from loguru import logger


def get_config(config_path: str = "/etc/namesilo_dyndns/config.yaml") -> dict:
    if Path("~/.config/namesilo_dyndns.yaml").expanduser().is_file():
        config_path = Path("~/.config/namesilo_dyndns.yaml").expanduser()
    elif Path(config_path).is_file():
        config_path = Path(config_path)
    else:
        raise FileNotFoundError(ENOENT, strerror(ENOENT), config_path)
    with open(config_path, "r") as yamlfile:
        config = safe_load(yamlfile)
        if "key" not in config:
            raise KeyError("Key 'key' missing")
        if "domains" not in config:
            raise KeyError("Key 'domains' missing")
        if "ipv4_server" not in config:
            config["ipv4_server"] = "https://ip.dhoessl.de"
            logger.warning(
                "ipv4_server not configured. "
                f"Default to {config['ipv4_server']}"
            )
        if "ipv6_server" not in config:
            config["ipv6_server"] = "https://ip.dhoessl.de"
            logger.warning(
                "ipv6_server not configured. "
                f"Default to {config['ipv4_server']}"
            )
        for domain in config["domains"]:
            domain_config = config["domains"][domain]
            if (
                ("ipv4" not in domain_config or not domain_config["ipv4"])
                and ("ipv6" not in domain_config or not domain_config["ipv6"])
            ):
                raise KeyError(f"Missing Key 'ipv4' or 'ipv6' for {domain}")
            if "subdomain" not in domain_config:
                raise KeyError(f"Missing Key 'subdomain' for {domain}")
            if "ipv4" not in domain_config:
                config["domains"][domain]["ipv4"] = False
            if "ipv6" not in domain_config:
                config["domains"][domain]["ipv6"] = False
        return config
