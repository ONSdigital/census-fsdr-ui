async def domain_processor(request):
  domain_protocol = request.app['DOMAIN_URL_PROTOCOL']
  domain_url = request.app['DOMAIN_URL']
  return {'domain_url': domain_protocol + domain_url}
