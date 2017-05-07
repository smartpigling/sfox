import datetime


def get_now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def today():
    day = datetime.datetime.today().date()
    return str(day)


def from_now_days(day):
    date = datetime.datetime.now() + datetime.timedelta(day)
    return date.strftime('%Y-%m-%d')


def delay_days(date, day=1):
    _date = datetime.datetime.strptime(date, '%Y-%m-%d') + datetime.timedelta(day)
    return _date.strftime('%Y-%m-%d')


def get_year():
    year = datetime.datetime.today().year
    return year


def get_month():
    month = datetime.datetime.today().month
    return month


def get_hour():
    return datetime.datetime.today().hour


def diff_day(start=None, end=None):
    d1 = datetime.datetime.strptime(end, '%Y-%m-%d')
    d2 = datetime.datetime.strptime(start, '%Y-%m-%d')
    delta = d1 - d2
    return delta.days