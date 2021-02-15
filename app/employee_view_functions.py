from aiohttp.web import HTTPInternalServerError
import requests
from requests.auth import HTTPBasicAuth

from app.utils import FSDR_URL, FSDR_USER, FSDR_PASS
from . import role_matchers


def map_false_to_dash(dict):
  return {k: (v if v else '-') for (k, v) in dict.items()}


# receives a list of devices. a device is a hash of fields.
def process_device_details(initial_devices):
  def map_device(device):
    return {
        'Device ID': device['deviceId'],
        'Device Phone Number': device['fieldDevicePhoneNumber'],
        'Device Type': device['deviceType']
    }

  devices = [
      map_device(map_false_to_dash(device)) for device in initial_devices
  ]

  # TODO remove this once all views have migrated to extract_device_* methods
  device_numbers = [(device['fieldDevicePhoneNumber'] or None)
                    for device in initial_devices]

  return devices, device_numbers


def extract_device(devices, type):
  ds = [d for d in devices if d['Device Type'] == type]
  if len(ds) > 1:
    raise HTTPInternalServerError('Two devices of same type')
  elif len(ds) == 1:
    return ds[0]
  else:
    return None


def extract_device_phone(devices):
  return extract_device(devices, 'PHONE')


def extract_device_chromebook(devices):
  return extract_device(devices, 'CHROMEBOOK')


def process_employee_information(employee_information):
  def handle_blank(key):
    if key == 'mobility':
      return 'No'
    else:
      return '-'

  return {
      k: (v if v else handle_blank(k))
      for (k, v) in employee_information.items()
  }


def format_line_manager(current_job_role):
  maybe_names = (current_job_role['lineManagerFirstName'],
                 current_job_role['lineManagerSurname'])
  names = (n for n in maybe_names if n and n != '-')
  return ' '.join(names) or '-'


def get_employee_device(employee_id):
  return requests.get(FSDR_URL + f'/devices/byEmployee/{employee_id}',
                      verify=False,
                      auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_employee_information(role, employee_id):
  extract_type = role.extract_type
  return requests.get(FSDR_URL +
                      f'/fieldforce/byId/{extract_type}/{employee_id}',
                      verify=False,
                      auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_employee_history_information(role, employee_id):
  extract_type = role.extract_type
  return requests.get(FSDR_URL +
                      f'/fieldforce/historyById/{extract_type}/{employee_id}',
                      verify=False,
                      auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))
