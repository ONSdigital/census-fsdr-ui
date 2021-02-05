    async def get(self, request):
        session = await get_session(request)

        await saml.ensure_logged_in(request)

        await clear_stored_search_criteria(session)
        setup_request(request)
        log_entry(request, 'start')

        user_role = await saml.get_role_id(request)

        page_number = get_page(request)

        try:
            search_range, records_per_page = page_bounds(page_number)

            get_device_info = get_device_records(search_range)
            get_device_info_json = get_device_info.json() 

            if len(get_device_info_json) > 0:
                device_sum = get_device_info_json[0].get('total_devices',0)
                max_page = math.ceil(device_sum / records_per_page)        
            else:
                max_page = 1 

        except ClientResponseError as ex:
            client_response_error(ex, request)

        if get_device_info.status_code == 200:
            table_headers = device_table_headers()

            device_records = device_records_table(get_device_info_json)
            device_type_dropdown_options = device_type_dropdown('blank')
            device_sent_dropdown_options = device_sent_dropdown('blank')

            return {
                'page_title': f'Device Table view for: {user_role}',
                'table_headers': table_headers,
                'device_records': device_records,
                'page_number': page_number,
                'last_page_number': max_page,
                'device_type_options': device_type_dropdown_options,
                'device_sent_options': device_sent_dropdown_options,
                'dst_download': download_permission(user_role),
            }
        else:
            logger.warn('Database is down', client_ip=request['client_ip'])
            flash(request, NO_EMPLOYEE_DATA)
            raise HTTPFound(request.app.router['MainPage:get'].url_for())


