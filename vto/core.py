from pathlib import Path
import base64
import datetime
import os
import subprocess

import requests
from clint import textui
import click
import sgr_ansi

ICONS = [sgr_ansi.m_(f'{x} ') for x in '❶❷❸❹❺❻❼❽❾❿']


def now(fmt='%Y-%m-%d %H:%M:%S') -> str:
    return datetime.datetime.now().strftime(fmt)


def gen_separator(separator='') -> tuple:
    _header, _footer = '', ''
    if not separator:
        separator = []
    if not isinstance(separator, list):
        separator = [separator]
    if len(separator) == 1:
        _header = _footer = separator[0]
    elif len(separator) == 2:
        _header, _footer = separator
    return _header, _footer


def num_choice(choices, default='1', valid_keys='', depth=1, icons='', sn_info=None,
               indent=4, fg_color='green', separator='',
               with_img=6, img_list=None, img_cache_dir='/tmp/vto', use_cache=False,
               extra_hints='', clear_previous=False, quit_app=True,
               ):
    """
        传入数组, 生成待选择列表, 如果启用图片支持, 需要额外传入与数组排序一致的图片列表,
        - 图片在 iterms 中显示速度较慢, 不推荐使用

        .. note: 图片在 iterms 中显示速度较慢, 如果数组长度大于10, 不推荐使用

        .. code:: python

            sn_info = {
                'align': '-', # 左右对齐
                'length': 2, # 显示长度
            }

    :param use_cache:
    :type use_cache:
    :param default:
    :type default:
    :param indent: ``左侧空白``
    :type indent:
    :param fg_color: ``前景色``
    :type fg_color:
    :param choices: 备选选项
    :type choices: list
    :param depth: ``如果是嵌套数组, 显示当前层级``
    :type depth: int
    :param icons: ``默认展示的icons:  '❶❷❸❹❺❻❼❽❾❿'``
    :type icons: any
    :param sn_info: ``需要展示的序号的信息长度对齐方式, 默认2个字符/右对齐``
    :type sn_info: dict
    :param valid_keys: ``可以输入的有效 key, 使用 ',' 分隔``
    :type valid_keys: str
    :param separator: 分隔符 header/footer, 默认无, 如果不为空, 则显示
    :type separator:
    :param img_cache_dir:  ``图片缓存目录``
    :type img_cache_dir: str
    :param with_img: ``是否使用图片, 如果值大于0, 则以实际值大小来作为终端显示行数``
    :type with_img: int
    :param img_list: ``图片原始 url ``
    :type img_list: list
    :param extra_hints: ``n-next,p-prev,s-skip``
    :type extra_hints: any
    :param clear_previous: ``clear previous output``
    :type clear_previous:
    :return:
    :rtype:
    """
    icons = icons or ICONS
    if not choices:
        return None

    if default is not None:
        default = '{}'.format(default)

    sn_info = sn_info or {}
    _header, _footer = gen_separator(separator=separator)

    with textui.indent(indent, quote=' {}'.format(icons[depth - 1])):
        if _header:
            textui.puts(getattr(textui.colored, fg_color)(_header))

        for i, choice in enumerate(choices, start=1):
            if with_img > 0 and img_list:
                cat_net_img(img_list[i - 1],
                            indent=indent,
                            img_height=with_img,
                            img_cache_dir=img_cache_dir,
                            use_cache=use_cache)

            _align = '{}{}'.format(sn_info.get('align', ''), sn_info.get('length', 2))
            # _hint = '%{}s. %s'.format(_align) % (i, choice)
            _hint_num = '%{}s.'.format(_align) % i
            _hint = '[{}]'.format(_hint_num)
            _hint = textui.colored.magenta(_hint)
            _hint += getattr(textui.colored, fg_color)(' %s' % choice)
            textui.puts(_hint)

        if _footer:
            textui.puts(getattr(textui.colored, fg_color)(_footer))

    _valid = [str(x + 1) for x in range(0, len(choices))]
    default_prompt = 'Your Choice'
    valid_choices = ['q-quit', 'b-back']
    if extra_hints:
        if isinstance(extra_hints, str):
            extra_hints = extra_hints.split(',')
        valid_choices += extra_hints

    default_prompt = '{}({})?'.format(default_prompt, '/'.join(valid_choices))
    c = click.prompt(
        # click.style('[Depth: ({})]Your Choice(q-quit/b-back)?', fg='cyan').format(depth),
        click.style(default_prompt, fg='cyan'),
        type=str,
        default=default
    )

    if str(c) in 'qQ':
        if quit_app:
            os._exit(0)
        else:
            if clear_previous:
                click.clear()
            return str(c)
    if valid_keys == 'all':
        return c
    elif str(c) in 'bB':
        if clear_previous:
            click.clear()
        return str(c)
    elif valid_keys and str(c) in valid_keys.split(','):
        return str(c)
    elif c not in _valid:
        textui.puts(textui.colored.red('  😭 ✘ Invalid input[{}]'.format(c)))
        return num_choice(
            choices, default, valid_keys, depth, icons, sn_info, indent, fg_color, separator, with_img, img_list,
            img_cache_dir, use_cache, extra_hints, clear_previous, quit_app,
        )
    else:
        return int(c) - 1


def yn_choice(msg, indent=4, fg_color='cyan', separator=''):
    """
        传入 msg , 返回 True/False

    :param separator:
    :type separator:
    :param fg_color:
    :type fg_color:
    :param indent:
    :type indent:
    :param msg:
    :type msg:
    :return:
    :rtype:
    """
    _header, _footer = gen_separator(separator=separator)
    if _header:
        textui.puts(getattr(textui.colored, fg_color)(_header))
    with textui.indent(indent, quote=' {}'.format(' ')):
        textui.puts(textui.colored.green(msg))
    if _footer:
        textui.puts(getattr(textui.colored, fg_color)(_footer))

    c = click.confirm(
        click.style('Your Choice?[yn] (q-quit/b-back)?', fg='cyan'),
        default=True,
    )
    return c


def pause_choice(msg, indent=4, fg_color='green', separator=''):
    _header, _footer = gen_separator(separator=separator)

    if _header:
        textui.puts(getattr(textui.colored, fg_color)(_header))
    with textui.indent(indent, quote=' {}'.format(' ')):
        textui.puts(getattr(textui.colored, fg_color)(msg))

    if _footer:
        textui.puts(getattr(textui.colored, fg_color)(_footer))

    c = click.prompt(click.style('Press Any Key to Continue...(q-quit)', fg='cyan'), default='.')
    if str(c) in 'qQ':
        os._exit(-1)
    return c


def copy_to_clipboard(dat):
    """
        复制 ``dat`` 内容到 剪切板中

    :return: None
    """
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(to_bytes(dat))
    p.stdin.close()
    p.communicate()


def cat_net_img(url='', indent=4, img_height=0, img_cache_dir='/tmp/vto', use_cache=False):
    """
        - 优先 从缓存目录读取图片
        - 如果失败, 再从相应的url读取照片

    :param use_cache: ``使用缓存``
    :type use_cache:
    :param img_cache_dir:
    :type img_cache_dir:
    :param url:
    :type url:
    :param indent:
    :type indent:
    :param img_height:
    :type img_height:
    :return:
    :rtype:
    """
    name = url.split('/')[-1]
    pth = Path(img_cache_dir) / name

    # 如果不使用缓存 或者 文件不存在, 则先下载到本地, 然后再读取
    if not use_cache or not pth.stat().st_size:
        raw = requests.get(url)
        pth.write_bytes(raw.content)

    with textui.indent(indent, quote=' {}'.format(' ')):
        textui.puts(cat_img_by_path(pth, img_height))


def cat_img_by_path(pth, img_height=0):
    mar = to_str(base64.b64encode(pth.read_bytes()))
    return cat_img_cnt(mar, img_height)


def cat_img_cnt(cnt_in='', img_height=0):
    """
       展示图片内容

    :param cnt_in:
    :type cnt_in:
    :param img_height:  照片占用的终端行数
    :type img_height: int
    :return:
    :rtype:
    """
    if not img_height:
        img_height = 6
    _head = '\x1b]1337;'
    _file = 'File=name={}'.format(to_str(base64.b64encode(to_bytes(now()))))
    _attr = ';inline=1;height={}:'.format(img_height)
    _tail = '\x07'
    cnt = '{}{}{}{}{}'.format(
        _head, _file, _attr, cnt_in, _tail
    )
    return cnt


def color_print(msg, indent=4, color='green'):
    with textui.indent(indent, quote=' {}'.format(' ')):
        textui.puts(getattr(textui.colored, color)(msg))


def to_str(str_or_bytes, charset='utf-8'):
    return str_or_bytes.decode(charset) if hasattr(str_or_bytes, 'decode') else str_or_bytes


def to_bytes(str_or_bytes):
    return str_or_bytes.encode() if hasattr(str_or_bytes, 'encode') else str_or_bytes


def read_file(pth, use_str=False) -> str:
    cont = None
    try:
        with open(u'' + pth, 'rb') as fp:
            cont = fp.read()

        if use_str:
            cont = to_str(cont)
    except Exception as err:
        print(err)
    return cont
