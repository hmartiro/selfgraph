from timeit import timeit


def time_function(func, *args, **kwargs):
    """
    Time the execution of a single function, and print out
    the result. The function is invoked exactly once, and all
    arguments are forwarded. Forwards the return value.
    
    """

    MAX_PRINT = 30

    def format_arg(arg):
        s = repr(arg)
        if len(s) > MAX_PRINT:
            s = s[:int(MAX_PRINT/2)] + '...' + s[-int(MAX_PRINT/2):]
        return s

    ret = None

    def run():
        nonlocal ret
        ret = func(*args, **kwargs)

    t = timeit(run, number=1)
    print('{}({}{}), t = {:.6f}s'.format(
        func.__name__,
        ', '.join(format_arg(arg) for arg in args),
        ''.join(', {}={}'.format(k, format_arg(v)) for k, v in kwargs.items()),
        t
    ))

    return ret

if __name__ == '__main__':
    
    def factorial(n):
        if n == 1:
            return 1
        return n * factorial(n-1)

    a = time_function(factorial, 5)
    b = time_function(factorial, 100)
    c = time_function(factorial, 500)

    print('5!={}, 100!={}, 500!={}'.format(a, b, c))
