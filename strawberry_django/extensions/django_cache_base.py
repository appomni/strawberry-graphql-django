from functools import _make_key

from django.core.cache import caches
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from strawberry.extensions.base_extension import Extension


class DjangoCacheBase(Extension):
    """
    Base for a Cache that uses Django built in cache instead of an in memory cache

    Arguements:

    `cache_name: Optional[str]`
        Name of the Django Cache to use, defaults to 'default'

    `timeout: Optional[int]`
        How long to hold items in the cache. See the Django Cache docs for details
        https://docs.djangoproject.com/en/4.0/topics/cache/

    `hash_fn: Callable[..., str]`
        A function to use to generate the cache keys
        Defaults to the same key generator as functools.lru_cache
        WARNING! The default function does NOT work with memcached
        and will generate warnings
    """

    def __init__(self, cache_name="default", timeout=DEFAULT_TIMEOUT, hash_fn=None):
        self.cache = caches[cache_name]
        self.timeout = timeout
        # Use same key generating function as functools.lru_cache as default
        self.hash_fn = hash_fn or _make_key

    def execute_cached(self, func, *args, **kwargs):
        hash_key = self.hash_fn(args, kwargs, False)
        cache_result = self.cache.get(hash_key)
        if cache_result is not None:
            return cache_result
        func_result = func(*args, **kwargs)
        self.cache.set(hash_key, func_result, timeout=self.timeout)
        return func_result
