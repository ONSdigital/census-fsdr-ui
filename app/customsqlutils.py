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
        Field("first_name", database_association_name=database_name,),
        Field("unique_employee_id", database_association_name=database_name,),
        Field("surname", database_association_name=database_name,),
        Field("preferred_name", database_association_name=database_name,),
        Field("address_1", database_association_name=database_name,),
        Field("address_2", database_association_name=database_name,),
        Field("town", database_association_name=database_name,),
        Field("county", database_association_name=database_name,),
        Field("postcode", database_association_name=database_name,),
        Field("personal_email_address", database_association_name=database_name,),
        Field("ons_email_address", database_association_name=database_name,),
        Field("telephone_number_contact_1", database_association_name=database_name,),
        Field("telephone_number_contact_2", database_association_name=database_name,),
        Field("emergency_contact_full_name", database_association_name=database_name,),
        Field("emergency_contact_mobile_no", database_association_name=database_name,),
        Field("mobility", database_association_name=database_name,),
        Field("id_badge_no", database_association_name=database_name,),
        Field("weekly_hours", database_association_name=database_name,),
        Field("dob", database_association_name=database_name,),
        Field("status", database_association_name=database_name,),
        Field("ingest_date", database_association_name=database_name,),
        Field("data_source", database_association_name=database_name,),
        Field("country", database_association_name=database_name,),
        Field("new_device", database_association_name=database_name,),
        Field("last_role_id", database_association_name=database_name,),
        Field("setup", database_association_name=database_name,),
        Field("external_id", database_association_name=database_name,),
    ])
  elif database_name == 'fsdr.employee_history':
    return ([
        Field("id", database_association_name=database_name,),
        Field("first_name", database_association_name=database_name,),
        Field("unique_employee_id", database_association_name=database_name,),
        Field("surname", database_association_name=database_name,),
        Field("preferred_name", database_association_name=database_name,),
        Field("address_1", database_association_name=database_name,),
        Field("address_2", database_association_name=database_name,),
        Field("town", database_association_name=database_name,),
        Field("county", database_association_name=database_name,),
        Field("postcode", database_association_name=database_name,),
        Field("personal_email_address", database_association_name=database_name,),
        Field("ons_email_address", database_association_name=database_name,),
        Field("telephone_number_contact_1", database_association_name=database_name,),
        Field("telephone_number_contact_2", database_association_name=database_name,),
        Field("emergency_contact_full_name", database_association_name=database_name,),
        Field("emergency_contact_mobile_no", database_association_name=database_name,),
        Field("mobility", database_association_name=database_name,),
        Field("id_badge_no", database_association_name=database_name,),
        Field("weekly_hours", database_association_name=database_name,),
        Field("dob", database_association_name=database_name,),
        Field("status", database_association_name=database_name,),
        Field("ingest_date", database_association_name=database_name,),
        Field("data_source", database_association_name=database_name,),
        Field("country", database_association_name=database_name,),
        Field("new_device", database_association_name=database_name,),
        Field("last_role_id", database_association_name=database_name,),
        Field("setup", database_association_name=database_name,),
        Field("external_id", database_association_name=database_name,),
    ])
  elif database_name == 'fsdr.job_role_history':
    return ([
        Field("id", database_association_name=database_name,),
        Field("job_role", database_association_name=database_name,),
        Field("unique_role_id", database_association_name=database_name,),
        Field("line_manager_first_name", database_association_name=database_name,),
        Field("line_manager_surname", database_association_name=database_name,),
        Field("area_location", database_association_name=database_name,),
        Field("unique_employee_id", database_association_name=database_name,),
        Field("job_role_type", database_association_name=database_name,),
        Field("operational_end_date", database_association_name=database_name,),
        Field("job_role_short", database_association_name=database_name,),
        Field("contract_start_date", database_association_name=database_name,),
        Field("contract_end_date", database_association_name=database_name,),
        Field("assignment_status", database_association_name=database_name,),
        Field("is_active", database_association_name=database_name,),
        Field("cr_status", database_association_name=database_name,),
        Field("reassignment_reason", database_association_name=database_name,),
        Field("parent_job_role", database_association_name=database_name,),
    ])
  elif database_name == 'fsdr.device':
    return ([
        Field("device_id",database_association_name=database_name,),
        Field("field_device_phone_number", database_association_name=database_name,),
        Field("device_type",
              search_type="dropdown",
              database_association_name=database_name,
              dropdown_options=[
                  "PHONE",
                  "CHROMEBOOK",
              ]),
        Field("unique_employee_id",  database_association_name=database_name,),
        Field(
            "device_sent",
            search_type="dropdown",
             database_association_name=database_name,
            format_as_boolean=True,
            dropdown_options=boolean_dropdown_options,
        ),
    ])
  elif database_name == 'fsdr.job_role':
    return ([
        Field("id",  database_association_name=database_name,),
        Field("job_role",  database_association_name=database_name,),
        Field("unique_role_id",  database_association_name=database_name,),
        Field("line_manager_first_name",  database_association_name=database_name,),
        Field("line_manager_surname",  database_association_name=database_name,),
        Field("area_location",  database_association_name=database_name,),
        Field("unique_employee_id",  database_association_name=database_name,),
        Field("job_role_type",  database_association_name=database_name,),
        Field("operational_end_date",  database_association_name=database_name,),
        Field("job_role_short",  database_association_name=database_name,),
        Field("contract_start_date",  database_association_name=database_name,),
        Field("contract_end_date",  database_association_name=database_name,),
        Field("assignment_status",  database_association_name=database_name,),
        Field("is_active",  database_association_name=database_name,),
        Field("cr_status",  database_association_name=database_name,),
        Field("closing_report_id",  database_association_name=database_name,),
        Field("parent_job_role",  database_association_name=database_name,),
    ])
  elif database_name == 'fsdr.databasechangelog':
    return ([
        Field("id",  database_association_name=database_name,),
        Field("author",  database_association_name=database_name,),
        Field("filename",  database_association_name=database_name,),
        Field("dateexecuted",  database_association_name=database_name,),
        Field("orderexecuted",  database_association_name=database_name,),
        Field("exectype",  database_association_name=database_name,),
        Field("md5sum",  database_association_name=database_name,),
        Field("description",  database_association_name=database_name,),
        Field("comments",  database_association_name=database_name,),
        Field("tag",  database_association_name=database_name,),
        Field("liquibase",  database_association_name=database_name,),
        Field("contexts",  database_association_name=database_name,),
        Field("labels",  database_association_name=database_name,),
        Field("deployment_id",  database_association_name=database_name,),
    ])
  elif database_name == 'fsdr.action_indicator':
    return ([
        Field("unique_role_id",
              column_name="Role ID",
               database_association_name=database_name,
              search_box_visible=False),
        Field(
            "job_role_short",
             database_association_name=database_name,
            column_name="Job Role",
            search_type="dropdown",
            dropdown_options=job_role_dropdown_options,
        ),
        Field(
            "unique_employee_id",
             database_association_name=database_name,
            column_name="Employee ID",
        ),
        Field(
            "gsuite_status",
             database_association_name=database_name,
            search_type="dropdown",
            dropdown_options=status_options,
        ),
        Field(
            "xma_status",
             database_association_name=database_name,
            search_type="dropdown",
            dropdown_options=status_options,
        ),
        Field(
            "granby_status",
             database_association_name=database_name,
            search_type="dropdown",
            dropdown_options=status_options,
        ),
        Field(
            "lone_worker_solution_status",
             database_association_name=database_name,
            search_type="dropdown",
            dropdown_options=status_options,
            column_name="Lone Worker Status",
        ),
        Field(
            "service_now_status",
             database_association_name=database_name,
            search_type="dropdown",
            dropdown_options=status_options,
        ),
        Field(
            "adecco_status",
             database_association_name=database_name,
            search_type="dropdown",
            dropdown_options=status_options,
        ),
        Field(
            "setup",
             database_association_name=database_name,
            search_type="dropdown",
            dropdown_options=boolean_dropdown_options,
            format_as_boolean=True,
        ),
    ])
  elif database_name == 'fsdr.update_state':
    return ([
        Field("unique_employee_id",  database_association_name=database_name,),
        Field("logistics",  database_association_name=database_name,),
        Field("employee",  database_association_name=database_name,),
    ])
  elif database_name == 'fsdr.request_log':
    return ([
        Field("id",  database_association_name=database_name,),
        Field("target_service",  database_association_name=database_name,),
        Field("date_time",  database_association_name=database_name,),
    ])
  elif database_name == 'fsdr.adecco':
    return ([
        Field("unique_employee_id",  database_association_name=database_name,),
        Field("adecco_hash",  database_association_name=database_name,),
    ])
  elif database_name == 'fsdr.user_authentication':
    return ([
        Field("username",  database_association_name=database_name,),
        Field("password",  database_association_name=database_name,),
        Field("user_role",  database_association_name=database_name,),
    ])
  elif database_name == 'lws.lws':
    return ([
        Field("unique_employee_id",  database_association_name=database_name,),
        Field("lws_hash",  database_association_name=database_name,),
    ])
  elif database_name == 'gsuite.gsuite':
    return ([
        Field("unique_employee_id",  database_association_name=database_name,),
        Field("gsuite_status",  database_association_name=database_name,),
        Field("gsuite_id",  database_association_name=database_name,),
        Field("gsuite_hash",  database_association_name=database_name,),
        Field("unique_employee_id",  database_association_name=database_name,),
    ])
  elif database_name == 'gsuite.chromebook':
    return ([
        Field("device_serial_number",  database_association_name=database_name,),
        Field("ons_id",  database_association_name=database_name,),
    ])

  else:
    return ([])
