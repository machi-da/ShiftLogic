import os
from logging import DEBUG, FileHandler, Formatter, StreamHandler, getLogger

from utils import make_dir


def setup_logger(log_dir_path, log_file_name):
    make_dir(log_dir_path)
    logger = getLogger(log_file_name)
    logger.setLevel(DEBUG)
    formatter = Formatter('%(asctime)s %(levelname)s - %(funcName)s - %(lineno)d - %(message)s',
                          datefmt='%Y-%m-%dT%H:%M:%S')

    sh = StreamHandler()
    sh.setLevel(DEBUG)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    fh = FileHandler(os.path.join(log_dir_path, log_file_name), encoding='utf-8')
    fh.setLevel(DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger
