import os
from datetime import datetime, timedelta, timezone


def make_dir(dir_path):
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)


def current_datetime(fmt=None):
    # 現在時刻を文字列で返す
    if fmt is None:
        fmt = '%Y-%m-%dT%H:%M:%S'
    tz_jst = timezone(timedelta(hours=+9), 'JST')
    return datetime.now(tz_jst).strftime(fmt)