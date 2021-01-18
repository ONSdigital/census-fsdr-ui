def pagehighlow(totalNumberOfEmployees, currentPageNumber):
    # current_page_number is min of 1
    split = 50              # 50 items per page

    highValue = split * currentPageNumber 
    lowValue =  highValue - split 
    
    maxPage = ((int(totalNumberOfEmployees.text) / 50) - 1).ceil()

    return (highValue, lowValue)

    max_page = 
    if page_number >= max_page > 1:
        page_number = int(math.floor(max_page))
    else:
        if max_page < 1:
            max_page = 1
        if page_number > 1:
            low_value = 50 * page_number
            high_value = low_value + 50
        else:
            low_value = page_number
            high_value = 50

