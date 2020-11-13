from datetime import datetime

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


def check_if_timestamp_or_parse(dt):
    if isinstance(dt, datetime):
        return datetime.timestamp(dt) * 1000
    elif isinstance(dt, str):
        dtime = parsing_dtime(dt, parsing_dtime_options)
        return datetime.timestamp(dtime) * 1000


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
    return blocks_time


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
