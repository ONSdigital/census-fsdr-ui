from structlog import get_logger

logger = get_logger('fsdr-ui')

class Field:
    def __init__(self,database_name,search_type="input_box",search_options=None,column_name=None,accordion=False):
        self.database_name =  database_name
        self.column_name = self.create_column_name(column_name)
        self.search_type = search_type
        self.search_options = search_options
        self.accordion = accordion

    def create_column_name(self,column_name):
        if column_name == None:
            column_name = self.database_name.replace("_"," ").title()
        else:
            column_name = column_name
        return(column_name)


def get_fields(service_name):
    fields =  []
    if service_name == "gsuitetable":
        fields = [
                Field("unique_employee_id"),
                Field("gsuite_status"),
                Field("gsuite_id"),
                Field("gsuite_hash"),
                Field("current_groups"),
                ]
    return(fields)

def get_fields_to_load(Fields):
    fields_to_load = []
    for field in Fields:
        fields_to_load.append(field.database_name)
    return(fields_to_load)

def get_table_records(Fields,json_records):
    #TODO remove 
    logger.error("Fields: " + str(Fields) + "\n\nJsonRecords:  " + str(json_records))
    formatted_records = []
    for each_record in json_records:
        record = {'tds': None}
        combined_field = []
        for each_field in Fields:
            combined_field.append( {
                'value': each_record[each_field.database_name],
            },)
        record['tds'] = combined_field[:]
        formatted_records.append(record)

    logger.error("FORMATTED RECORDS" + str(formatted_records))
    return formatted_records 

def get_table_headers(Fields):
    # TODO update so accordion is created if needed
    headers = []
    for field in Fields:
        headers.append(
                {
                'value': str(field.column_name),
                'aria_sort': 'none',
                 })

    return(headers)
