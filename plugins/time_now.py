import re
import time
import datetime


def now():
    return int(time.time() * 1000)


def make_time(create_time):
    """
    时间转换 -- wap微博
    :param create_time:
    :return: 时间
    """
    num = int(re.findall('\d+', create_time)[0])
    now = datetime.datetime.now()
    date = str(now.date()).split('-')
    time_now = str(now.time()).split('.')[0].split(':')
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    hour = int(time_now[0])
    miu = int(time_now[1])
    sec = time_now[2]
    if '分' in create_time:
        result = miu - num
        if result < 0:
            miu = 60 + result
            hour = hour - 1
            if hour < 0:
                hour = 23
                day = day - 1
        else:
            miu = result
    if '时' in create_time:
        result = hour - num
        if result < 0:
            day = day - 1
            hour = 24 + result
        else:
            hour = result
    if '天' in create_time:
        hour = create_time.split()[-1].split(':')[0]
        miu = create_time.split()[-1].split(':')[1]
        result = day - 1
        if result == 0:
            if month in [2, 4, 6, 8, 9, 11, ]:
                day = 31
                month -= 1
            if month in [5, 7, 10]:
                day = 30
                month -= 1
            if month == 1:
                year -= 1
                month = 12
                day = 31
            if month == 3:
                day = 29
                month = 2
            else:
                day = 29 + result
                month -= 1
            pass
        else:
            day = day - 1
    lst = [month, day, hour, miu]
    new_lst = []
    for i in range(len(lst)):
        if (0 < int(lst[i]) < 10) and (len(str(lst[i])) == 1):
            x = '0{}'.format(str(lst[i]))
            # print(x)
        else:
            x = lst[i]
        new_lst.append(x)
    create_time = '{}-{}-{} {}:{}:{}'.format(year, new_lst[0], new_lst[1], new_lst[2], new_lst[3], sec)
    # print(create_time)
    return create_time


def make_time_for_pc(create_time):
    """
    新浪微博使用
    :param create_time:
    :return:
    """
    num = int(re.findall('\d+', create_time)[0])
    now = datetime.datetime.now()
    date = str(now.date()).split('-')
    time_now = str(now.time()).split('.')[0].split(':')
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    hour = int(time_now[0])
    miu = int(time_now[1])
    sec = time_now[2]
    if '分' in create_time:
        result = miu - num
        if result < 0:
            miu = 60 + result
            hour = hour - 1
            if hour < 0:
                hour = 23
                day = day - 1
                if day == 0:
                    day = 12
                    year -= 1
        else:
            miu = result
        create_time = '{}-{}-{} {}:{}'.format(year, month, day, hour, miu)
    if '时' in create_time:
        result = hour - num
        if result < 0:
            day = day - 1
            if day == 0:
                day = 12
                year -= 1
            hour = 24 + result
        else:
            hour = result
        create_time = '{}-{}-{} {}:{}'.format(year, month, day, hour, miu)
    if '天' in create_time:
        create_time = create_time.replace('今天', '{}-{}-{} '.format(year, month, day))
        return create_time
    lst = [month, day, hour, miu]
    new_lst = []
    for i in range(len(lst)):
        if (0 < int(lst[i]) < 10) and (len(str(lst[i])) == 1):
            x = '0{}'.format(str(lst[i]))
        else:
            x = lst[i]
        new_lst.append(x)
    create_time = '{}-{}-{} {}:{}'.format(year, new_lst[0], new_lst[1], new_lst[2], new_lst[3])
    return create_time


def make_time_for_website(create_time):

    pass



def transform_unix(num):
    """
    unix时间转换 -- 微信使用
    :param num:
    :return: 日期
    """
    format = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(int(num))
    dt = time.strftime(format, value)
    return dt


def check_date(create_time, start_time, dead_time):
    now = datetime.datetime.now()
    time_now = str(now.time()).split('.')[0].split(':')
    hour = int(time_now[0])
    miu = int(time_now[1])
    sec = time_now[2]
    if ('前' in create_time) or ('天' in create_time):
        create_time = make_time(create_time).split()[0]
    create_date = [int(x) for x in create_time.split('-')]
    start_date = [int(x) for x in start_time.split('-')]
    start_year = start_date[0]
    start_month = start_date[1]
    start_day = start_date[2]
    dead_date = [int(x) for x in dead_time.split('-')]
    dead_year = dead_date[0]
    dead_month = dead_date[1]
    dead_day = dead_date[2]
    if len(create_date) == 2:
        create_year = dead_year
        create_month = create_date[0]
        create_day = create_date[1]
        if (create_month < start_month) or (create_month > dead_month) or (create_day < start_day) or \
                (create_day > dead_day):
            return False
        return '{}-{}-{} {}:{}:{}'.format(create_year, create_month, create_day, hour, miu, sec)
    else:
        create_year = create_date[0]
        create_month = create_date[1]
        create_day = create_date[2]
        if (create_year < start_year) or (create_year > dead_year) or (create_month < start_month) or \
                (create_month > dead_month) or (create_day < start_day) or (create_day > dead_day):
            return False
        return '{}-{}-{} {}:{}:{}'.format(create_year, create_month, create_day, hour, miu, sec)


if __name__ == '__main__':
    # print(now())
    # make_time('昨天 05:00')
    # print(transform_unix(1541253097))
    # print(check_date('2018-12-3', '2018-11-3'))
    # print(datetime.datetime.now().year)
    print(make_time_for_pc('1小时前'))
    # print('今天08:56'.replace('今天', ''))