from app.role_matchers import (
    microservices_permissions,
    has_download_permission,
    )


class View:
  def __init__(self,
      database_name,
      user_role,
      display_name=None,
      who_can_view=None,
      url  = None,):

    self.database_name = database_name
    self.display_name = self.create_display_name(display_name)
    self.url_clear  = self.create_url(url, database_name, clear='clear')
    self.url = self.create_url(url, database_name, clear='')
    self.currently_visible = self.visible(user_role, database_name, who_can_view)
    self.download_available = self.download_available(user_role, database_name)

  def create_url(self, url, database_name, clear):
    if url == None:
      url = (f'/microservices/{database_name}{clear}')
    return url
      
  def create_display_name(self, display_name):
    if display_name == None:
      display_name = self.database_name.replace("table", "").title()
    return (display_name)

  def download_available(self, user_role, database_name):
    return has_download_permission(user_role, database_name)

  def visible(self, user_role, database_name, who_can_view):
    return microservices_permissions(user_role, database_name)


def get_views(user_role, microservice_name):
  views = []

  views.append( View("gsuitetable",user_role),)
  views.append( View("iattable",user_role),)
  views.append( View("devicetable",user_role),)
  views.append( View("xmatable",user_role),)
  views.append( View("lwstable",user_role),)
  views.append( View("servicenowtable",user_role),)
  views.append( View("updatestatetable",user_role),)
  views.append( View("requestlogtable",user_role),)
  views.append( View("chromebooktable",user_role),)

  current_view_index = 0
  for counter, view in enumerate(views):
    if view.database_name == microservice_name:
      current_view_index = counter

  return (views, current_view_index)


