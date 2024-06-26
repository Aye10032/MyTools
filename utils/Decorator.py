import time
from functools import wraps
from typing import Callable, Any
from loguru import logger


def retry(retries: int = 3, delay: float = 1) -> Callable:
    """
    为函数提供重试逻辑的装饰器。

    参数:
    retries (int): 最大重试次数，默认为3。
    delay (float): 两次重试之间的延迟时间（秒），默认为1。

    返回:
    Callable: 被装饰的函数。

    异常:
    ValueError: 如果retries小于1或delay小于等于0，则抛出此异常。
    """
    if retries < 1 or delay <= 0:
        raise ValueError('Wrong param')

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for i in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == retries:
                        logger.error(f'Error: {repr(e)}.')
                        logger.error(f'"{func.__name__}()" failed after {retries} retries.')
                        break
                    else:
                        logger.debug(f'Error: {repr(e)} -> Retrying...')
                        time.sleep(delay)

        return wrapper

    return decorator
