from time import time


class TimeitRecord:
    record = {}


def timeit(method, print_out=False):
    """Decorator to time any function."""
    method_name = method.__name__

    def timed(*args, **kw):
        start_time = time()
        result = method(*args, **kw)
        elapsed_time = round(time() - start_time, 5)
        if method_name in TimeitRecord.record:
            TimeitRecord.record[method_name].append(elapsed_time)
        else:
            TimeitRecord.record[method_name] = [elapsed_time]
        if print_out:
            print(f'Timeit: {method_name:>40} --- {elapsed_time:<7} sec.')
        return result
    return timed


def reset_timing():
    """Resets the recording. All function calls after calling this function are averaged irrespectively from precious
    ones."""
    TimeitRecord.record = {}


def get_timeit_record():
    """Access the TIMEIT_RECORD container which stores all timed functions."""
    return TimeitRecord.record


def get_avg_timings():
    """Go through function calls in timeit record and sort them according to mean execution time."""
    record = get_timeit_record()
    average_timings = {}
    for func in record:
        average_timings[func] = sum(record[func]) / len(record[func])
    return average_timings


def print_avg_timings_sorted(round_places=3):
    """Print a summary of @timeit-decorated function calls."""
    avg_timings = get_avg_timings()
    sorted_funcs = sorted(avg_timings, key=avg_timings.get, reverse=True)
    print(f'{60 * "="}')
    total_time = 0
    for func in sorted_funcs:
        timing = round(avg_timings[func], round_places)
        total_time += timing
        print(f'{func:>45} --- {timing:<5} s')
    print(f'{"Total time recorded":>45} --- \033[1m{round(total_time, round_places)} s\033[0m')
    print(f'{60 * "="}')
