import logging
import os


def get_logger(log_file_name, level=logging.INFO):
    log_dir_name = 'Log'
    if not os.path.exists(log_dir_name):
        os.makedirs(log_dir_name)
    logger_return = logging.getLogger()  # 不加名称设置root logger
    logger_return.setLevel(level=level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s: - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    # 使用FileHandler输出到文件, 文件默认level:ERROR
    fh = logging.FileHandler('%s/%s' % (log_dir_name, log_file_name))
    fh.setLevel(level=logging.ERROR)
    fh.setFormatter(formatter)
    # 使用StreamHandler输出到屏幕
    ch = logging.StreamHandler()
    ch.setLevel(level=level)
    ch.setFormatter(formatter)
    logger_return.addHandler(ch)
    logger_return.addHandler(fh)
    return logger_return
