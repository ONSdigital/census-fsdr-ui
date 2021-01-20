from typing import Tuple
from math import ceil

def page_bounds(employee_sum: int, page_number: int) -> Tuple[int, int, int]:
    if page_number < 1:
        raise ValueError(f'page_number must be 1 or greater, but was {page_number}')

    records_per_page = 50   

    last_record  = records_per_page * page_number 
    first_record = last_record - records_per_page
    
    max_page = ceil((employee_sum / records_per_page) - 1)

    return (last_record, first_record, max_page)


