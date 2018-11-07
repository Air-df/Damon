import re


def check_num(text):
    """
    检测微博，收藏，转发，评论，点赞数是否为空
    :return: 对应数字，若为空则返回0
    """
    num = re.findall('\d+', text)
    if not num:
        num = 0
    else:
        num = num[0]
    return num


if __name__ == '__main__':
    print(check_num('转发'))
