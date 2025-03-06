from datetime import datetime, timedelta
import functools

# This is called with the values for lru_cache and timedelta.  For example:
# @timed_cache(maxsize=10, type=True, days=3)
#
# lru_cache parameters: maxsize, type
# timedelta parameters: days - or seconds, microseconds, milliseconds, minutes, hours, weeks

def timed_cache(**timedelta_kwargs):

    def _wrapper(f):
        maxsize = timedelta_kwargs.pop('maxsize', 128)
        typed = timedelta_kwargs.pop('typed', False)
        update_delta = timedelta(**timedelta_kwargs)
        next_update = datetime.datetime.now(datetime.UTC) - update_delta

        # Apply @lru_cache to f
        f = functools.lru_cache(maxsize=maxsize, typed=typed)(f)

        @functools.wraps(f)
        def _wrapped(*args, **kwargs):
            nonlocal next_update
            now = datetime.datetime.now(datetime.UTC)
            if now >= next_update:
                f.cache_clear()
                next_update = now + update_delta
            return f(*args, **kwargs)
        return _wrapped
    return _wrapper
