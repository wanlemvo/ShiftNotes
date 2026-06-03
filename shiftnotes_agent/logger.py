import logging
import json
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Console handler — shows logs in terminal
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)

        # Structured JSON formatter
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def log_node_entry(logger: logging.Logger, node_name: str, run_id: str):
    logger.info(f"NODE_ENTRY | run_id={run_id} | node={node_name}")


def log_node_exit(logger: logging.Logger, node_name: str, run_id: str, result: str):
    logger.info(f"NODE_EXIT | run_id={run_id} | node={node_name} | result={result}")


def log_signal_detected(logger: logging.Logger, signal: str, method: str, run_id: str):
    logger.info(f"SIGNAL | run_id={run_id} | signal={signal} | detected_by={method}")


def log_error(logger: logging.Logger, node_name: str, run_id: str, error: str):
    logger.error(f"ERROR | run_id={run_id} | node={node_name} | error={error}")