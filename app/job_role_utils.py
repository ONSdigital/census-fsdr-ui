import asyncio

class JRNamesService:
  """Service to fetch and cache Job Role names for use in dropdown menus"""

  def __init__(self):
    self.cache = None
    self.lifetime = 30 * 60
    self.timestamp = None
    self.lock = asyncio.Lock()

  async def fetch(self, request):
    session =  await get_session(request)
    client = session.app['client']
    if self.cache is None or (time.time() - self.timestamp) > self.lifetime:
      async with self.lock:
        url = FSDR_URL + f'/jobRoles/allJobRoleShorts/distinct'
        auth = BasicAuth(FSDR_USER, FSDR_PASS)
        async with client.get(url, auth=auth) as resp:
          self.cache = await resp.text()
        self.timestamp = time.time()
    return self.cache
