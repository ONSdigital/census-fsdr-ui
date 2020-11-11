from dateutil import parser as date_parser


def tab_generation(tab_name, tab_data):
    generic_tab = '<div id="accordion" class="accordion">' \
                  '<details id="accordion-1" class="details js-collapsible details--accordion" ' \
                  'open data-btn-close="Hide" data-group="accordion">' \
                  '<summary class="details__summary js-collapsible-summary"><div class="details__heading">' \
                  '<span class="details__title u-fs-r--b">' + tab_name + '</span></div></summary>'

    for information in tab_data:
        generic_tab = generic_tab + '<div id="accordion-1-content" class="details__content js-collapsible-content">' \
                                    '<dl class="metadata metadata__list grid grid--gutterless u-cf ' \
                                    'u-mb-l"><dt class="metadata__term grid__col col-4@m">' + information + '</dt>' \
                                    '<dd class="metadata__value grid__col col-8@m">' + str( tab_data[information]) + \
                                    '</dd></dl></div>'

    generic_tab = generic_tab + '</details></div>'

    return generic_tab


def table_generation(tab_data):
    add_headers = []
    tds_data = []
    add_data = []

    for headers in tab_data:
        for header in headers:
            add_headers.append({
                'value': header,
                'aria_sort': 'none'
            }, )
        break

    for all_data in tab_data:
        for data in all_data:
            tds_data.append({
                'value': all_data[data]
            })

        add_data.append({'tds':
                             tds_data
                         })
        tds_data = []

    table_data = [{'headers': add_headers}, {'tds': add_data}]

    return table_data


def format_to_uk_dates(date):
    try:
        return date_parser.parse(date).date().strftime('%d/%m/%Y')
    except date_parser.ParserError:
        # If it is not a date (such as '-'), return as-is
        return date
