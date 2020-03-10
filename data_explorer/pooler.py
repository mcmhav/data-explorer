import logging
import resource
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class PoolResponse():
    """PoolResponse."""

    results: List
    errors: List
    time: float
    max_memory: int


@dataclass
class PoolResult():
    """PoolResult."""

    iterable_value: Any
    result: Any = None
    error: Any = None
    function_params: Optional[Dict] = None


def pooler(
        function: Any,
        iterable: Any,
        function_params: Dict = None,
        max_workers: int = 10,
        timeout: int = None,
        pool: Any = ThreadPoolExecutor,
) -> PoolResponse:
    """
    Pooler.

    Parameters
    ----------
    function : Any
        function to pool
    iterable : [type]
        list to pool
    function_params : Dict, optional
        extra parameters to function, by default None
    max_workers : int, optional
        max workers, by default 10
    timeout : int, optional
        timeout, by default None
    pool : Any, optional
        pool function, by default ThreadPoolExecutor

    Returns
    -------
    PoolResponse
        response of pool run
    """
    start = time.time()

    if not function_params:
        function_params = {}

    results = []
    errors = []
    with pool(max_workers=max_workers) as p:
        futures = {
            p.submit(function, iterable_value, **function_params):
            iterable_value
            for iterable_value in iterable
        }
        for index, future in enumerate(as_completed(futures, timeout=timeout)):
            iterable_value = futures[future]
            try:
                logging.info('Handling %s', index)
                result = future.result()
                results.append(
                    PoolResult(
                        iterable_value,
                        result=result,
                        function_params=function_params,
                    ))
            except Exception as e: # pylint: disable=broad-except
                errors.append(
                    PoolResult(
                        iterable_value,
                        error=e,
                        function_params=function_params,
                    ))
                logging.exception(f"Exception occurred for {iterable_value}")

    end = time.time()

    return PoolResponse(
        results=results,
        errors=errors,
        time=end - start,
        max_memory=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    )


def run_with_retry(
        function: Any,
        iterable: Any,
        retries: int = 5,
        **kwargs: Any,
) -> PoolResponse:
    results: List = []
    errors: List = iterable
    start = time.time()

    retry_count = 0
    while retry_count < retries and errors:
        pool_response = pooler(function, errors, **kwargs)
        results += pool_response.results
        errors = [error.iterable_value for error in pool_response.errors]
        retry_count += 1

    end = time.time()
    return PoolResponse(
        results=results,
        errors=errors,
        time=end - start,
        max_memory=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    )


@dataclass
class PoolList():
    """PoolList."""

    iterable: Any

    @staticmethod
    def _handle_attr(attr: str, iterable: Any) -> Any:
        if isinstance(attr, list):
            iterable += attr
        else:
            iterable.append(attr)

        return iterable

    def chain(self, attr: str) -> 'PoolList':
        iterable: List = []
        for iterable_value in self.iterable:
            if hasattr(iterable_value, attr):
                iterable = self._handle_attr(
                    getattr(iterable_value, attr),
                    iterable,
                )
            elif attr in iterable_value:
                iterable = self._handle_attr(iterable_value[attr], iterable)
        return PoolList(iterable)

    def pool_run(self, function, **kwargs) -> PoolResponse:
        return pooler(function, self.iterable, **kwargs)

    def pool_run_with_error_retry(self, function, **kwargs) -> PoolResponse:
        return run_with_retry(function, self.iterable, **kwargs)
