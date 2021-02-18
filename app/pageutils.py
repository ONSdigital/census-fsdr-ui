from typing import Tuple
from math import ceil


def page_bounds(page_number: int) -> Tuple[int, int]:
  if page_number < 1:
    raise ValueError(
        f'page_number must be 1 or greater, but was {page_number}')

  records_per_page = 50

  last_record = records_per_page * page_number
  first_record = last_record - records_per_page

  search_range = {'rangeHigh': last_record, 'rangeLow': first_record}

  return (search_range, records_per_page)


def get_page(request):
  if 'page' in request.query:
    page_number = int(request.query['page'])
  else:
    page_number = 1

  return (page_number)


def result_message(search_range, total, title):
  """Construct a result message for a microservice called `title`."""

  range_high = search_range.get('rangeHigh', 0)
  range_low = search_range.get('rangeLow', 0)
  max_i = max(total, range_high)
  min_i = min(total, range_low)
  return f'{title} Showing {min_i} to {max_i} of total {total} results'
