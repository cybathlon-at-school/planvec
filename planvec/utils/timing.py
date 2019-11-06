import operator
import numpy as np
from time import time


TIMEIT_RECORD = {}


def timeit(method, print_out=False):
    """Decorator to time any function."""
    method_name = method.__name__

    def timed(*args, **kw):
        start_time = time()
        result = method(*args, **kw)
        elapsed_time = round(time() - start_time, 5)
        if method_name in TIMEIT_RECORD:
            TIMEIT_RECORD[method_name].append(elapsed_time)
        else:
            TIMEIT_RECORD[method_name] = [elapsed_time]
        if print_out:
            print(f'Timeit: {method_name:>40} --- {elapsed_time:<7} sec.')
        return result
    return timed


def get_timeit_record():
    """Access the TIMEIT_RECORD container which stores all timed functions."""
    return TIMEIT_RECORD


def get_avg_timings():
    """Go through function calls in timeit record and sort them according to mean execution time."""
    record = get_timeit_record()
    average_timings = {}
    for func in record:
        average_timings[func] = sum(record[func]) / len(record[func])
    return average_timings


def print_avg_timings_sorted(round_places=3):
    avg_timings = get_avg_timings()
    sorted_funcs = sorted(avg_timings, key=avg_timings.get, reverse=True)
    print(f'{60 * "="}')
    for func in sorted_funcs:
        timing = round(avg_timings[func], 3)
        print(f'{func:>45} --- {timing:<30}')
    print(f'{60 * "="}')
