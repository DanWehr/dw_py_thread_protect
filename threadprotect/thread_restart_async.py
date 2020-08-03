import asyncio
from functools import wraps


def thread_restart_async(rerun_delay, rerun_max=-1, before_func=None, after_func=None, exc_func=None, print_func=print):
    """Add restart-on-crash behavior to an async function.

    Wraps a funtion such that it will be re-ran if it ends due to an
    exception. If no exception is raised, the function will complete normally.

    before/after/exc parameters allow you to set functions that should be called
    before the first function run, after the last function run, or be called if
    the wrapped function raises an exception.

    Input paramters are reused between each run, and so if the exception is
    due to the parameters the function will repeatedly fail. If a limited number
    of restarts is desired it can be set through rerun_max.

    Decorators:
        wraps

    Keyword Arguments:
        rerun_delay {number} -- Number of seconds to wait after an exception
            before starting the function again.
        rerun_max {int} -- Number of times the function should be attempted
            before it is not run again and crash_restart will return None. A
            negative rerun_max value indicates unlimited runs. (default: {-1})
        before_func {func()} -- Func to call before wrapped func (default: {None})
        after_func {func()} -- Func to call after wrapped func (default: {None})
        exc_func {func(exc)} -- Func to call on exception (default: {None})
        print_func {func(string)} -- Function to send before/after/exception
            strings to if respective funcs are not provided. Set none for
            no printouts. (default: {print})

    Returns:
        Object -- Wrapped function
    """
    def inner(original_func):
        @wraps(original_func)
        async def wrapper(*args, **kwargs):
            orig_name = original_func.__name__
            _rerun_max = int(rerun_max)
            if _rerun_max < 0:
                rerun_count = _rerun_max
            else:
                rerun_count = 0

            if before_func is not None:
                before_func()
            elif print_func is not None:
                print_func("Starting func: " + orig_name)

            func_future = original_func(*args, **kwargs)
            while func_future is not None:
                try:
                    if _rerun_max < 0 or rerun_count < _rerun_max:
                        if rerun_count != _rerun_max:
                            rerun_count += 1
                        result = await func_future
                    func_future = None
                except Exception as e:
                    result = None
                    if exc_func is not None:
                        exc_func(e)
                    elif print_func is not None:
                        print_func("Caught exception in func " + orig_name + ": " + str(e))
                    await asyncio.sleep(rerun_delay)
                    func_future = original_func(*args, **kwargs)

            if after_func is not None:
                after_func()
            elif print_func is not None:
                print_func("Ending func: " + orig_name)

            return result
        return wrapper
    return inner
