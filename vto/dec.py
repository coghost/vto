from functools import wraps
import inspect
import time
import sgr_ansi


def fmt_help(*args, show_more=True, opt_hint='[OPT] '):
    desc = sgr_ansi.Bg(args[0], show=False)
    if show_more:
        if len(args) > 1:
            args = list(args[1:])
            args.insert(0, opt_hint)
            usage = ''.join([sgr_ansi.Ic_(x) for x in args])
            desc = '{}\n{}'.format(desc, usage)
    return desc


def __parse_func_directly(fn):
    dat = {
        'filename': fn.__code__.co_filename.split('/')[-1].split('.')[0],
        'lineno': fn.__code__.co_firstlineno,
        'method': fn.__name__,
        'function': '',
    }
    return dat


def __parse_func_in_stack(prefix):
    try:
        dat = {}
        for _stack in inspect.stack():
            _file_name = _stack.filename.split('/')[-1].split('.')[0]
            lineno = _stack.lineno
            method_name = _stack.code_context[0].strip().replace('self.', '')
            if prefix in method_name:
                # we will go through until the deepest matched method in stack
                # at class level
                dat['filename'] = _file_name
                dat['function'] = _stack.function
                dat['lineno'] = lineno
                dat['method'] = method_name
        return dat
    except:
        pass


def parse_func_info(fn, prefix=''):
    """
    parse function information, for log purpose

    Args:
        fn (): the function or method
        prefix (str): only parse function/methods startswith prefix

    Returns:
        func_info (str):
    """
    # fallback name: in case all following way failed, the minimum info we can get.
    func_info = fn.__name__
    dat = {}

    if prefix:
        # class level have prefix
        dat = __parse_func_in_stack(prefix)

    # if get info by stack in class failed, or run with function level will try to get info directly
    if not dat:
        dat = __parse_func_directly(fn)

    if dat:
        # caller is typically used when 'func_a(func_b())'
        _caller = dat.get('function', '')
        _caller = sgr_ansi.Iy_(_caller) if _caller else ''
        func_info = '{}({}) {}{}'.format(
            sgr_ansi.Bc_(dat.get('filename', '')),
            sgr_ansi.Bc_(dat.get('lineno', 0)),
            _caller + '.' if _caller else '',
            sgr_ansi.Iy_(dat.get('method', '')),
        )

    return func_info


def prt(do_prt=True, hints='cost', prt_args=False, prt_return_value=False, cb=None):
    """ function/method level decorator, more complex output

    Args:
        do_prt (bool): default with ATS_GUIDE_MODE is enough to use, but let you can manually set it to True/False
        hints (str): a brief hint
        prt_args (bool): if set to True, will print the args
        prt_return_value (bool): if set to True, will print the return value
    """

    def dec(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not do_prt:
                return fn(*args, **kwargs)

            st = time.time()
            func_name = parse_func_info(fn)
            extra_info = ''
            if prt_args:
                extra_info += f'*{args}, **{kwargs}'

            # INFO: paired method detail entered-log with step-out-log when debug
            _enter_info = '{0} {1} entered'.format(sgr_ansi.Bc_('↘'), func_name)
            if cb:
                cb(_enter_info)
            else:
                print(_enter_info)

            result = fn(*args, **kwargs)

            cost_time = round(time.time() - st, 2)
            # just set a minimum cost time to filter out some unnecessary output
            if do_prt and cost_time > 0.0009:
                if prt_return_value:
                    extra_info += '' if result is None else result

                _step_out = '{}{}{}{} {}s'.format(
                    sgr_ansi.Bb_('✔ '),
                    func_name,
                    ' {} '.format(extra_info) if extra_info else ' ',
                    hints,
                    sgr_ansi.Bb_(cost_time))
                if cb:
                    cb(_step_out)
                else:
                    print(_step_out)

            return result

        return wrapper

    return dec
