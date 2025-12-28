import sys
from termios import tcflush, TCIFLUSH
from gennet.lib.ansi_colors import re, cyan, red, white, green


def get_input(expression=r'\w+', message='Please input: ', err_message='invalid value.', default_value=None):
    while True:
        tcflush(sys.stdin, TCIFLUSH)
        user_input = input(message)
        if user_input == '' and default_value is not None:
            return default_value
        elif re.match(expression, user_input):
            return user_input
        print(red(err_message))


def get_ipv4_address(default_value=None):
    ipv4_expression = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    if default_value:
        return get_input(ipv4_expression, f'Please input ipv4(default:{default_value}): ', default_value=default_value)
    else:
        return get_input(ipv4_expression, 'Please input ipv4: ')


def get_y_n(message, default=False):
    y_n = lambda bool: '[Y/n]?: ' if bool else '[y/N]?: '
    user_input = get_input('y|n|Y|N|', message + y_n(default), 'input y or n')
    if re.match('y|Y', user_input):
        return True
    elif re.match('n|N', user_input):
        return False
    else:
        return default


def getlist(li):
    menu = []
    for i, l in enumerate(li):
        index = i+1
        if index < 10:
            head = ' '+str(index)+', '
        else:
            head = str(index)+', '
        pad = 10 - len(l)
        l += ' ' * pad
        menu += [head + cyan(l)]
        if index % 5 == 0:
            print(' '.join(menu))
            menu = []

    print(' '.join(menu))


def getvlist(li):
    for i, l in enumerate(li):
        print(str(i + 1) + ', ' + cyan(l))


def choose_num(menu_list, message=green('Please select number.'), vertical=True):
    print(message)
    while True:
        if vertical:
            getvlist(menu_list)
        else:
            getlist(menu_list)
        tcflush(sys.stdin, TCIFLUSH)
        num = input('>> ')
        try:
            if re.match(r'\d+', num):
                index = int(num) - 1
                if isinstance(index, int):
                    if len(menu_list) > index >= 0:
                        print(white('Selected : ') + cyan(menu_list[index]))
                        return index
        except:
            print(red('Please input number!'))
        print(red('Please input existing number!!'))
