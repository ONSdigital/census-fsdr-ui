
class View:
  def __init__(self,
      database_name,
      user_role,
      display_name=None,
      url  = None,
      who_can_view    =[],)

  self.database_name = database_name
  self.display_name = create_display_name(display_name)
  self.url  = create_url(url, database_name)
  self.currently_visible = visible(user_role, who_can_view)
  self.download_available = download_available(user_role, database_name)

  def create_url(self, url, database_name):
    if display_name == None:
      url = (f'/microservices/{database_name}clear')
    return url
      
  def create_display_name(self, display_name):
    if display_name == None:
      display_name = self.database_name.replace("table", "").title()
    return (display_name)

  def download_available(self, user_role, database_name):


  def visible(self, user_role, who_can_view):


def get_views():
  views = []

  views.append( View("gsuitetable"),)
  views.append( View("iattable"),)
  views.append( View("devicetable"),)
  views.append( View("xmatable"),)
  views.append( View("lwstable"),)
  views.append( View("servicenowtable"),)
  views.append( View("updatestatetable"),)
  views.append( View("requestlogtable"),)
  views.append( View("chromebooktable"),)

  return (views)


