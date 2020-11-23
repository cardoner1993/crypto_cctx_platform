from datetime import datetime
import yaml
import logging
import os
from pathlib import Path

from src import config_file

parsing_dtime_options = ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d']


def parsing_dtime(time, format):
    format_copy = format.copy()
    for fmt in format_copy:
        try:
            format_time = datetime.strptime(time, fmt)
            return format_time
        except ValueError:
            print(f"Format {fmt} doesn't match. Next fmt")
    raise ValueError("The specified formats to check didn't match add others")


# def check_if_timestamp_or_parse(dt):
#     if isinstance(dt, datetime):
#         return int(datetime.timestamp(dt) * 1000)
#     elif isinstance(dt, str):
#         dtime = parsing_dtime(dt, parsing_dtime_options)
#         return int(datetime.timestamp(dtime) * 1000)


def get_obs_in_time_range(start, end=None, format='h'):
    if not isinstance(start, datetime):
        start = parsing_dtime(start, parsing_dtime_options)
    if end is None:
        print("End is none. Setting it to now")
        end = datetime.now().replace(minute=0, second=0, microsecond=0)
    elif not isinstance(end, datetime):
        end = parsing_dtime(end, parsing_dtime_options)
    # Get time difference
    time_diff = end - start
    blocks_time = check_cases_in_time(format, time_diff)
    return int(blocks_time)


def check_cases_in_time(format, duration):
    total_sec = duration.total_seconds()
    if 'h' in format:
        return total_sec // 3600
    elif 'd' in format:
        return total_sec // (3600*24)
    elif 'm' in format:
        return total_sec // 60
    elif 's' in format:
        return total_sec


def build_request_url(url, **kwargs):
    """
    Build request URL for Darksky API

    Parameters
    ----------
    url: datetime.date
        Time to request
    **kwargs: dict
        API key, latitude and longitude

    Returns
    -------
    str
        Request URL
    """
    url_parameters = '&'.join('{}={}'.format(key, value) for key, value in kwargs.items())
    return f"{url}?{url_parameters}"


def define_path_file(file_name, path=None):
    """
    Define the path of a file
    :param path: default None or str path of root directory (top level directory)
    :param file_name: str name of the file
    :return: str path + file name
    """
    if path is not None:
        print(f"Path is {path} and file is {file_name}")
        root_path = path
    else:
        root_path = config_file.root_path
    for root, dirs, files in os.walk(root_path):
        for file in files:
            # change the extension from '.mp3' to
            # the one of your choice.
            if file == file_name:
                print("File found in open yaml")
                return Path(root) / str(file)


def load_config(config_name='config.yaml', path=None, env='default'):
    """
    Load configuration from config.yml file.

    Parameters
    ----------
    env: str
        Environment to load (e.g. 'dev'). Default is 'default'.
    config_name: str
        config file name
    path: None or str with path
    Returns
    -------
    dict
        Config file content.
    """
    if path is not None:
        return open_yaml(define_path_file(path=path, file_name=config_name))[env]
    else:
        return open_yaml(define_path_file(config_name))[env]  # if config is placed in src


def open_yaml(path):
    """
    Load yaml file.

    Parameters
    ----------
    path: pathlib.PosixPath or str
        Path to yaml file

    Returns
    -------
    Dictionary
        Dictionary with yaml file content
    """
    with open(str(path)) as stream:
        try:
            yaml_dict = yaml.safe_load(stream)
        except yaml.YAMLError:
            logging.error('Error when opening YAML file.', exc_info=1)
    return yaml_dict


