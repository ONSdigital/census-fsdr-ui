import json

from structlog import get_logger
from app.tabutils import acc_generation
from app.searchfunctions import get_distinct_job_role_short

logger = get_logger('fsdr-ui')


class Field:
  def __init__(self,
               database_name,
               search_type="input_box",
               search_options=None,
               column_name=None,
               accordion=False,
               dropdown_options=None,
               search_box_visible=True,
               format_as_boolean=False,
               show_as_table_header=True):

    self.database_name = database_name
    self.column_name = self.create_column_name(column_name)
    self.search_type = search_type
    self.dropdown_options = self.format_dropdown_options(dropdown_options)
    self.accordion = accordion
    self.previous_value = ""
    self.show_as_table_header = show_as_table_header
    self.search_box_visible = search_box_visible
    self.format_as_boolean = format_as_boolean

  def create_column_name(self, column_name):
    if column_name == None:
      column_name = self.database_name.replace("_", " ").title()
    else:
      column_name = column_name
    return (column_name)

  def format_dropdown_options(self, dropdown_options, selected_value='blank'):
    if dropdown_options != None:
      final_dropdowns = [{
          'value': 'blank',
          'text': 'Select a status',
          'disabled': True,
      }]
      for option in dropdown_options:
        entry = {'value': option, 'text': option}
        final_dropdowns.append(entry)

      for each_dict in final_dropdowns:
        if each_dict['value'] == selected_value:
          each_dict['selected'] = True

      return final_dropdowns

  def refresh_selected_dropdown(self, selected_value):
    dropdown_values = [i.get('value') for i in self.dropdown_options]
    dropdown_values.remove('blank')
    self.dropdown_options = self.format_dropdown_options(
        dropdown_values, selected_value=selected_value)


def load_cookie_into_fields(field_classes, previous_criteria):
  for field in field_classes:
    if field.database_name in previous_criteria.keys():
      if field.search_type == "input_box":
        field.previous_value = previous_criteria.get(field.database_name)
      elif field.search_type == "dropdown":
        field.refresh_selected_dropdown(
            previous_criteria.get(field.database_name))
  return field_classes


def get_fields(service_name):
  # Set default Dropdown Values
  status_options = [
      "CREATE",
      "SETUP",
      "UPDATE",
      "LEAVER",
      "LEFT",
      "COMPLETE",
      "SUSPENDED",
  ]

  boolean_dropdown_options = [
      'True',
      'False',
  ]

  if service_name == "gsuitetable":
    return ([
        Field(
            "unique_employee_id",
            accordion=True,
        ),
        Field("gsuite_status",
              search_type="dropdown",
              dropdown_options=status_options),
        Field("gsuite_id"),
        Field("gsuite_hash"),
        Field("current_groups"),
    ])
  elif service_name == "xmatable":
    return ([
        Field("unique_employee_id"),
        Field("xma_id"),
        Field("xma_hash"),
    ])
  elif service_name == "lwstable":
    return ([
        Field("unique_employee_id"),
        Field("lws_hash"),
    ])
  elif service_name == "servicenowtable":
    return ([
        Field("unique_employee_id"),
        Field("service_now_id"),
        Field("service_now_hash"),
    ])
  elif service_name == "updatestatetable":
    return ([
        Field("unique_employee_id"),
        Field("logistics"),
        Field("employee"),
    ])
  elif service_name == "adecco":
    return ([
        Field("unique_employee_id"),
        Field("adecco_hash"),
    ])
  elif service_name == "requestlogtable":
    return ([
        Field("id"),
        Field("target_service",
              search_type="dropdown",
              dropdown_options=[
                  "NISRA_EXTRACT",
                  "ADECCO",
                  "NISRA",
                  "logistics",
              ]),
        Field("date_time"),
    ])
  elif service_name == "chromebooktable":
    return ([
        Field("device_serial_number"),
        Field("ons_id"),
    ])
  elif service_name == "devicetable":
    return ([
        Field("device_id"),
        Field(
            "field_device_phone_number",
            column_name="Phone Number",
        ),
        Field("device_type",
              search_type="dropdown",
              dropdown_options=[
                  "PHONE",
                  "CHROMEBOOK",
              ]),
        Field(
            "device_sent",
            search_type="dropdown",
            dropdown_options=boolean_dropdown_options,
        ),
        Field("ons_email_address", column_name="ONS ID"),
    ])
  elif service_name == "iattable":
    return ([
        Field("unique_role_id",
              column_name="Role ID",
              search_box_visible=False),
        Field("job_role_short",
              column_name="Job Role",
              search_type="dropdown",
              dropdown_options=get_distinct_job_role_short().json(),
              show_as_table_header=False),
        Field(
            "ons_email_address",
            column_name="ONS ID",
            accordion=True,
        ),
        Field(
            "unique_employee_id",
            column_name="Employee ID",
            accordion=True,
        ),
        Field(
            "gsuite_status",
            search_type="dropdown",
            dropdown_options=status_options,
        ),
        Field(
            "xma_status",
            search_type="dropdown",
            dropdown_options=status_options,
        ),
        Field(
            "granby_status",
            search_type="dropdown",
            dropdown_options=status_options,
        ),
        Field(
            "lone_worker_solution_status",
            search_type="dropdown",
            dropdown_options=status_options,
            column_name="Lone Worker Status",
        ),
        Field(
            "service_now_status",
            search_type="dropdown",
            dropdown_options=status_options,
        ),
        Field(
            "setup",
            search_type="dropdown",
            dropdown_options=boolean_dropdown_options,
            format_as_boolean=True,
        ),
    ])

  return ([])


def get_fields_to_load(field_classes):
  fields_to_load = []
  for field in field_classes:
    fields_to_load.append(field.database_name)
  return (fields_to_load)


def get_table_records(field_classes, json_records):
  formatted_records = []
  for each_record in json_records:
    record = {'tds': None}
    combined_field = []
    for field in field_classes:
      if field.show_as_table_header:
        record_field_data = each_record[field.database_name]
        if field.format_as_boolean:
          record_field_data = "True" if record_field_data == "t" else "False"
        combined_field.append(
            {
                'value':
                record_field_data if not field.accordion else acc_generation(
                    str(record_field_data)),
            }, )
    record['tds'] = combined_field[:]
    formatted_records.append(record)

  return formatted_records


def get_table_headers(field_classes):
  headers = []
  for field in field_classes:
    if field.show_as_table_header:
      headers.append({
          'value': str(field.column_name),
          'aria_sort': 'none',
      })

  return (headers)
