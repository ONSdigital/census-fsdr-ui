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


def acc_generation(content):
    acc_gen = []

    acc_gen.append("""<div id="accordion" class="accordion">""")
    acc_gen.append("""<details id="accordion-1" class="details js-collapsible details--accordion details--initialised" data-btn-close="Hide" data-group="accordion" role="group">""")
    acc_gen.append("""<summary class="details__summary js-collapsible-summary" role="link" aria-controls="accordion-1" aria-expanded="false" data-ga-action="Close panel">""")
    acc_gen.append("""<div class="details__heading"><span class="details__title u-fs-r--b">Expand for ID</span></div></summary>""")
    acc_gen.append("""<div id="accordion-1-content" class="details__content js-collapsible-content" aria-hidden="true">""")
    acc_gen.append("""<dl class="metadata metadata__list grid grid--gutterless u-cf u-mb-l">""")
    acc_gen.append("""<dt class="metadata__term grid__col col-18@m">""" + str(content) + """</dt>""")
    acc_gen.append("""<dd class="metadata__value grid__col col-1@m"></dd></dl></div>""")
    acc_gen.append("""</details>""")
    acc_gen.append("""</div>""")

    acc_gen = ''.join(acc_gen)

    return acc_gen

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
