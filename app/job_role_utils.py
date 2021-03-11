import asyncio
from aiohttp_session import get_session
from app.utils import FSDR_USER, FSDR_URL, FSDR_PASS
from aiohttp import BasicAuth
from structlog import get_logger
import time

logger = get_logger('fsdr-ui')

class JRNamesService:
  """Service to fetch and cache Job Role names for use in dropdown menus"""
  def __init__(self):
    self.cache = []
    self.lifetime = 30 * 60
    self.timestamp = 0
    self.lock = asyncio.Lock()

  async def fetch(self, request):
    client = request.app['client']
    refresh_due = (time.time() - self.timestamp) > self.lifetime
    if refresh_due and not self.lock.locked():
      async with self.lock:
        logger.info("Refreshing Job Role Dropdown Cache")
        url = FSDR_URL + f'/jobRoles/allJobRoleShorts/distinct'
        auth = BasicAuth(FSDR_USER, FSDR_PASS)
        async with client.get(url, auth=auth) as resp:
          cache = await resp.json()
          cache = [x for x in cache if x not in ['null', None]]
          self.cache = sorted(cache, key=str.lower)

        self.timestamp = time.time()
    return self.cache
