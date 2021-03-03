from dataclasses import dataclass, field
import time
from typing import Optional


class TimerError(Exception):
  pass


@dataclass
class Timer:
  name: Optional[str] = None
  _start_time: Optional[float] = field(default=None, init=False, repr=False)

  def start(self) -> None:
    if self._start_time is not None:
      raise TimerError(f"Timer is running. Use .stop() to stop it")

    self._start_time = time.perf_counter()

  def stop(self) -> float:
    if self._start_time is None:
      raise TimerError(f"Timer is not running. Use .start() to start it")

    # Calculate elapsed time
    elapsed_time = time.perf_counter() - self._start_time
    self._start_time = None

    # TODO use elapsed time here

    return elapsed_time

  def __enter__(self):
    self.start()
    return self

  def __exit__(self, *exc_info):
    self.stop()


class Metrics:
  def __init__(self):
    self.config_rolling_count = 10
    self.time_hists = {
        'preamble': [],
        'postamble': [],
        'query_jobroles': [],
        'query_?': [],
    }
    self.time_avgs = {
        'preamble': 0,
        'postamble': 0,
        'query_jobroles': 0,
        'query_?': 0,
    }

  def _mean(self, hist):
    return sum(hist) / len(hist)

  def new_request(self):
    return RequestMetrics(self)


class RequestMetrics:
  def __init__(self, manager):
    self.manager = manager
    self.time_preamble = None
    self.time_query1 = None
    self.time_query2 = None
    self.time_postamble = None

  def log_preamble():
    pass

  def log_query_jobroles():
    pass

  def log_postamble():
    pass
