import config
import secrets
import logging

logger = logging.getLogger(__name__)
logger.setLevel(config.log_lvl)
logger.addHandler(config.ch)
logger.propagate = False

def get_tmp_path(prefix):
    """Method generate path in /tmp/ with random sufix"""
    logging.debug(f"Generating temp path with prefix '{prefix}'")
    random_dir_sufix = secrets.token_urlsafe(10)
    return f'/tmp/{prefix}{random_dir_sufix}'