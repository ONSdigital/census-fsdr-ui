import json

from structlog import get_logger
from app.tabutils import acc_generation
from app.searchfunctions import get_job_role_shorts

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
               checkbox_value=False,
               name=False,
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
    self.checkbox_value = checkbox_value
    self.name = name

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
          'text': 'Select an option',
          'disabled': True,
      }]
      for option in dropdown_options:
        entry = {'value': option, 'text': option}
        final_dropdowns.append(entry)

      for each_dict in final_dropdowns:
        if each_dict['value'] == selected_value:
          each_dict['selected'] = True

      return final_dropdowns

  def refresh_dropdown_status(self, value_to_change_to):
    self.checkbox_value = value_to_change_to

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
      elif field.search_type == "checkbox":
        field.refresh_dropdown_status(
            previous_criteria.get(field.database_name))

  return field_classes


async def get_fields(service_name):
  # Set default Dropdown Values
  job_role_dropdown_options = await get_job_role_shorts()
  job_role_dropdown_options = job_role_dropdown_options.json()
  if None in job_role_dropdown_options:
    job_role_dropdown_options.remove(None)
  if "null" in job_role_dropdown_options:
    job_role_dropdown_options.remove("null")
  job_role_dropdown_options = sorted(job_role_dropdown_options, key=str.lower)

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

  assignment_status_dropdown_options = [
      'TRAINING_IN_PROGRESS',
      'ASSIGNED',
      'READY_TO_START',
  ]

  # NISRA HQ Checkboxese
  data_source_checkboxes = [
      Field(
          "include_nisra",
          column_name="Include NISRA Records",
          show_as_table_header=False,
          search_type="checkbox",
      ),
      Field(
          "include_hq",
          column_name="Include HQ Records",
          show_as_table_header=False,
          search_type="checkbox",
      ),
  ]

  if service_name == "gsuitetable":
    return ([
        Field(
            "unique_employee_id",
            accordion=True,
        ),
        Field("ons_email_address", accordion=True, column_name="ONS ID"),
        Field("gsuite_status",
              search_type="dropdown",
              dropdown_options=status_options),
        Field("gsuite_id"),
        Field("gsuite_hash"),
        Field("current_groups"),
    ])
  elif service_name == "index":
    return ([
        Field("id_badge_no", column_name="Badge No.",
              search_box_visible=False),
        Field("name", column_name="Name", search_box_visible=False, name=True),
        Field("unique_role_id",
              column_name="Job Role ID",
              search_box_visible=False),
        Field("job_role_short",
              column_name="Job Role",
              search_type="dropdown",
              dropdown_options=job_role_dropdown_options),
        Field("assignment_status",
              column_name="Asgnmt. Status",
              search_box_visible=False),
        Field("surname",
              column_name="Worker Surname",
              show_as_table_header=False),
        Field("area_location", show_as_table_header=False, column_name="Area"),
        Field(
            "noDevice",
            column_name="Only show users with no device",
            show_as_table_header=False,
            search_type="checkbox",
        ),
    ] + data_source_checkboxes)
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
  elif service_name == "missingdevicestable":
    return ([
        Field(
            "unique_employee_id",
            column_name="Employee ID",
            accordion=True,
        ),
        Field(
            "contract_start_date",
            column_name="Opperational Start Date",
            search_box_visible=False,
        ),
        Field(
            "assignment_status",
            search_type="dropdown",
            dropdown_options=assignment_status_dropdown_options,
        ),
        Field("ons_email_address", column_name="ONS ID"),
        Field(
            "unique_role_id",
            column_name="Job Role ID",
        ),
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
            format_as_boolean=True,
            dropdown_options=boolean_dropdown_options,
        ),
        Field("ons_email_address", column_name="ONS ID"),
    ])
  elif service_name == "iattable":
    return ([
        Field(
            "unique_role_id", column_name="Role ID", search_box_visible=False),
        Field("job_role_short",
              column_name="Job Role",
              search_type="dropdown",
              dropdown_options=job_role_dropdown_options,
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
            "adecco_status",
            search_type="dropdown",
            dropdown_options=status_options,
        ),
        Field(
            "setup",
            search_type="dropdown",
            dropdown_options=boolean_dropdown_options,
            format_as_boolean=True,
        ),
    ] + data_source_checkboxes)

  return ([])


def get_fields_to_load(field_classes):
  fields_to_load = []
  for field in field_classes:
    fields_to_load.append(field.database_name)
  return (fields_to_load)


def get_table_records(field_classes, json_records, remove_html=False):
  formatted_records = []
  for each_record in json_records:
    record = {'tds': None}
    combined_field = []
    for field in field_classes:
      if field.show_as_table_header:
        if field.name:
          record_field_data = '<a href="/employeeinformation/' + \
            each_record['unique_employee_id'] + '">' + each_record['first_name'] + \
            " " + each_record['surname'] + '</a>'
        else:
          record_field_data = each_record[field.database_name]

        if field.format_as_boolean:
          record_field_data = str(record_field_data)
        if (field.accordion and not remove_html):
          record_field_data = acc_generation(str(record_field_data))
        combined_field.append({
            'value': record_field_data,
        }, )
    record['tds'] = combined_field[:]
    formatted_records.append(record)

  return formatted_records


def get_table_headers(field_classes, remove_html=False):
  headers = []
  for field in field_classes:
    if field.show_as_table_header:
      headers.append({
          'value': str(field.column_name),
          'aria_sort': 'none',
      })

  return (headers)
