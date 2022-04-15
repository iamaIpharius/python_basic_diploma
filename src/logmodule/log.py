from loguru import logger
import pathlib

def do_log(msg):
    log_path = pathlib.PurePath(f"logs/{str(msg.chat.id)}.log")
    logger.add(log_path, format="{time} {level} {message}")
    logger.info(f"{msg.text}")