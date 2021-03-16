from app.microservice_tables import Field


async def get_database_fields(request):
  """All fields present in FSDR database for procedueral search generation"""

  database_names = [
      'fsdr.employee',
      'fsdr.employee_history',
      'fsdr.job_role_history',
      'fsdr.device',
      'fsdr.job_role',
      'fsdr.databasechangelog',
      'fsdr.action_indicator',
      'fsdr.update_state',
      'fsdr.user_authentication',
      'fsdr.request_log',
      'fsdr.adecco',
      'gsuite.chromebook',
      'gsuite.databasechangelog',
      'gsuite.databasechangeloglock',
      'gsuite.group_lookup',
      'gsuite.gsuite',
      'xma.databasechangelog'
      'xma.xma',
      'lws.databasechangelog',
      'lws.lws',
  ]

  # {'database_name':[Field,Field],'database2_name':[Field,]}
  all_fields = {}
  for db_name in database_names:
    all_fields[db_name] = await get_custom_fields(db_name, request)

  return (database_names, all_fields)


async def get_custom_fields(database_name, request):
  # Set default Dropdown Values
  job_role_dropdown_options = await request.app['jr_names_service'].fetch(
      request)

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

  if database_name == 'fsdr.employee':
    return ([
        Field("first_name", ),
        Field("unique_employee_id", ),
        Field("surname", ),
        Field("preferred_name", ),
        Field("address_1", ),
        Field("address_2", ),
        Field("town", ),
        Field("county", ),
        Field("postcode", ),
        Field("personal_email_address", ),
        Field("ons_email_address", ),
        Field("telephone_number_contact_1", ),
        Field("telephone_number_contact_2", ),
        Field("emergency_contact_full_name", ),
        Field("emergency_contact_mobile_no", ),
        Field("mobility", ),
        Field("id_badge_no", ),
        Field("weekly_hours", ),
        Field("dob", ),
        Field("status", ),
        Field("ingest_date", ),
        Field("data_source", ),
        Field("country", ),
        Field("new_device", ),
        Field("last_role_id", ),
        Field("setup", ),
        Field("external_id", ),
    ])
  elif database_name == 'fsdr.employee':
    return ([
        Field("id", ),
        Field("first_name", ),
        Field("unique_employee_id", ),
        Field("surname", ),
        Field("preferred_name", ),
        Field("address_1", ),
        Field("address_2", ),
        Field("town", ),
        Field("county", ),
        Field("postcode", ),
        Field("personal_email_address", ),
        Field("ons_email_address", ),
        Field("telephone_number_contact_1", ),
        Field("telephone_number_contact_2", ),
        Field("emergency_contact_full_name", ),
        Field("emergency_contact_mobile_no", ),
        Field("mobility", ),
        Field("id_badge_no", ),
        Field("weekly_hours", ),
        Field("dob", ),
        Field("status", ),
        Field("ingest_date", ),
        Field("data_source", ),
        Field("country", ),
        Field("new_device", ),
        Field("last_role_id", ),
        Field("setup", ),
        Field("external_id", ),
    ])
  elif database_name == 'fsdr.job_role_history':
    return ([
        Field("id", ),
        Field("job_role", ),
        Field("unique_role_id", ),
        Field("line_manager_first_name", ),
        Field("line_manager_surname", ),
        Field("area_location", ),
        Field("unique_employee_id", ),
        Field("job_role_type", ),
        Field("operational_end_date", ),
        Field("job_role_short", ),
        Field("contract_start_date", ),
        Field("contract_end_date", ),
        Field("assignment_status", ),
        Field("is_active", ),
        Field("cr_status", ),
        Field("reassignment_reason", ),
        Field("parent_job_role", ),
    ])
  elif database_name == 'fsdr.device':
    return ([
        Field("device_id"),
        Field("field_device_phone_number", ),
        Field("device_type",
              search_type="dropdown",
              dropdown_options=[
                  "PHONE",
                  "CHROMEBOOK",
              ]),
        Field("unique_employee_id", ),
        Field(
            "device_sent",
            search_type="dropdown",
            format_as_boolean=True,
            dropdown_options=boolean_dropdown_options,
        ),
    ])
  elif database_name == 'fsdr.job_role':
    return ([
        Field("id", ),
        Field("job_role", ),
        Field("unique_role_id", ),
        Field("line_manager_first_name", ),
        Field("line_manager_surname", ),
        Field("area_location", ),
        Field("unique_employee_id", ),
        Field("job_role_type", ),
        Field("operational_end_date", ),
        Field("job_role_short", ),
        Field("contract_start_date", ),
        Field("contract_end_date", ),
        Field("assignment_status", ),
        Field("is_active", ),
        Field("cr_status", ),
        Field("closing_report_id", ),
        Field("parent_job_role", ),
    ])
  elif database_name == 'fsdr.databasechangelog':
    return ([
        Field("id", ),
        Field("author", ),
        Field("filename", ),
        Field("dateexecuted", ),
        Field("orderexecuted", ),
        Field("exectype", ),
        Field("md5sum", ),
        Field("description", ),
        Field("comments", ),
        Field("tag", ),
        Field("liquibase", ),
        Field("contexts", ),
        Field("labels", ),
        Field("deployment_id", ),
    ])
  elif database_name == 'fsdr.action_indicator':
    return ([
        Field("unique_role_id",
              column_name="Role ID",
              search_box_visible=False),
        Field(
            "job_role_short",
            column_name="Job Role",
            search_type="dropdown",
            dropdown_options=job_role_dropdown_options,
        ),
        Field(
            "unique_employee_id",
            column_name="Employee ID",
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
    ])
  elif database_name == 'fsdr.update_state':
    return ([
        Field("unique_employee_id", ),
        Field("logistics", ),
        Field("employee", ),
    ])
  elif database_name == 'fsdr.request_log':
    return ([
        Field("id", ),
        Field("target_service", ),
        Field("date_time", ),
    ])
  elif database_name == 'fsdr.adecco':
    return ([
        Field("unique_employee_id", ),
        Field("adecco_hash", ),
    ])
  elif database_name == 'fsdr.user_authentication':
    return ([
        Field("username", ),
        Field("password", ),
        Field("user_role", ),
    ])
  elif database_name == 'lws.lws':
    return ([
        Field("unique_employee_id", ),
        Field("lws_hash", ),
    ])
  elif database_name == 'gsuite.gsuite':
    return ([
        Field("unique_employee_id", ),
        Field("gsuitestatus", ),
        Field("gsuiteid", ),
        Field("gsuitehash", ),
        Field("unique_employee_id", ),
    ])
  else:
    return ([])
