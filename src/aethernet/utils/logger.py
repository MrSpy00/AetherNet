import sys
import traceback
import logging
from pathlib import Path
from loguru import logger
from aethernet.utils.session_manager import SessionManager

class InterceptHandler(logging.Handler):
    """Intercept standard logging messages and redirect them to Loguru."""

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logger(log_dir: Path = Path("logs")):
    """Comprehensive Loguru & Session Logger with Global Exception Hooks"""
    session_mgr = SessionManager(logs_dir=log_dir)

    logger.remove()

    # 1. Console Output (Colorized) - only if stdout is available
    if sys.stdout is not None:
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:7}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO",
            colorize=True
        )

    # 2. Individual Session Log File
    logger.add(
        session_mgr.session_log_path,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:7} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        encoding="utf-8",
        backtrace=True,
        diagnose=True
    )

    # 3. Latest Session Pointer File
    latest_log_path = log_dir / "latest.log"
    logger.add(
        latest_log_path,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:7} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        encoding="utf-8",
        mode="w"
    )

    # Intercept standard library logs (scapy, urllib3, pyqtgraph, etc.)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Setup Global Exception Hooks
    def global_excepthook(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.opt(exception=True).critical(f"UNHANDLED EXCEPTION: {exc_value}\n{tb_str}")
        session_mgr.record_crash(exc_type, exc_value, tb_str)

    def global_unraisablehook(unraisable):
        tb_str = "".join(traceback.format_exception(unraisable.exc_type, unraisable.exc_value, unraisable.exc_traceback))
        logger.error(f"UNRAISABLE EXCEPTION in {unraisable.object}: {unraisable.exc_value}\n{tb_str}")
        session_mgr.record_error(is_warning=False)

    sys.excepthook = global_excepthook
    sys.unraisablehook = global_unraisablehook

    logger.info(f"⚡ AetherNet Logger System initialized. Session ID: {session_mgr.session_id}")
    return logger
