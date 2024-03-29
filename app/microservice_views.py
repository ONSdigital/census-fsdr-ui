from app.role_matchers import (
    microservices_permissions,
    has_download_permission,
)


class View:
  def __init__(
      self,
      database_name,
      user_role,
      search_section_accordioned=False,
      hide_table=False,
      hide_search_criteria=False,
      filter_button_label=None,
      display_name=None,
      who_can_view=None,
      url=None,
  ):

    self.database_name = database_name
    self.search_section_accordioned = search_section_accordioned
    self.display_name = self.create_display_name(display_name)
    self.url_clear = self.create_url(url, database_name, clear='clear')
    self.url = self.create_url(url, database_name, clear='')
    self.currently_visible = self.visible(user_role, database_name,
                                          who_can_view)
    self.download_available = self.download_available(user_role, database_name)
    self.filter_button_label = 'Apply filters'
    self.hide_table = hide_table
    self.hide_search_criteria = hide_search_criteria

  def create_url(self, url, database_name, clear):
    return url or f'/microservices/{database_name}{clear}'

  def create_display_name(self, display_name):
    if display_name == None:
      display_name = self.database_name.replace('table', '').title()
    return (display_name)

  def download_available(self, user_role, database_name):
    return has_download_permission(user_role, database_name)

  def visible(self, user_role, database_name, who_can_view):
    return microservices_permissions(user_role, database_name)


def get_html(user_role, views):
  # Non microservice headers added here
  header_html = []

  for view in views:
    if view.currently_visible:
      header_html.append({
          'title': view.display_name,
          'url': view.url_clear,
      })

  return header_html


def get_views(user_role, microservice_name):
  views = []

  views.append(
      View(
          'index',
          user_role,
          display_name='Home',
          filter_button_label='Filter',
      ), )
  views.append(
      View(
          'search',
          user_role,
          display_name='Search',
          filter_button_label='Submit',
          hide_table=True,
          hide_search_criteria=False,
      ), )

  views.append(View(
      'iattable',
      user_role,
      display_name='Interface Action',
  ), )
  views.append(View('devicetable', user_role), )
  views.append(View('gsuitetable', user_role), )
  views.append(View('xmatable', user_role), )
  views.append(View('lwstable', user_role), )
  views.append(View('servicenowtable', user_role), )
  views.append(View(
      'updatestatetable',
      user_role,
      display_name='Update',
  ), )
  views.append(View(
      'requestlogtable',
      user_role,
      display_name='Request',
  ), )
  views.append(View('chromebooktable', user_role), )
  views.append(
      View(
          'missingdevicestable',
          user_role,
          display_name='Missing Devices',
      ), )
  views.append(
      View('customsql',
           user_role,
           display_name='Custom SQL',
           url='/customsqlchoice'), )

  current_view_index = 0
  for counter, view in enumerate(views):
    if view.database_name == microservice_name:
      current_view_index = counter

  return (views, current_view_index)
