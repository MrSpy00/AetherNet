import sys
from pathlib import Path
from loguru import logger

def setup_logger(log_dir: Path = Path("logs")):
    """Loguru rotating log yapılandırması"""
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "aethernet.log"

    logger.remove()
    # Console output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:7}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    # File output (rotating 5MB, keep 10 files)
    logger.add(
        log_file,
        rotation="5 MB",
        retention="10 days",
        level="DEBUG",
        encoding="utf-8"
    )
    logger.info("AetherNet Loglama sistemi başlatıldı.")
    return logger
