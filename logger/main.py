from loguru import logger
from sys import stderr


def define_logger(
    loglevel: str = "INFO", to_file: bool = False,
    logfile: str = "/var/log/namesiloapi.log"
) -> None:
    allowed_levels = [
        "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"
    ]
    logger.remove()
    logger.add(
        stderr, level=loglevel if loglevel in allowed_levels else "INFO",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}:{function}</cyan>:<cyan>{line}</cyan> "
            "- <level>{message}</level>"
        ),
        colorize=True
    )
    if loglevel not in allowed_levels:
        logger.warning(
            f"loglevel {loglevel} not in allowed levels. default to 'INFO'. "
            f"allowed levels: {allowed_levels}"
        )
    if to_file:
        try:
            logger.add(
                logfile,
                level=loglevel if loglevel in allowed_levels else "INFO",
                colorize=False,
                format=(
                    "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
                    "{name}:{function} | {message}"
                )
            )
        except PermissionError:
            logger.error(f"Could not open {logfile} as logfile to write to")
    logger.debug("Logger setup completed")
