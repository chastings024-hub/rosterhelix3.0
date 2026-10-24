"""Read-only diagnostics for historical data sync; never modifies imported records."""
import socket, urllib.request, urllib.error
from urllib.parse import urlparse
from update_data import URL

def diagnose(season, resolver=None, opener=None):
    season=int(season)
    if not 1999 <= season <= 2100: raise ValueError('Invalid season')
    url=URL.format(season=season)
    host=urlparse(url).hostname
    resolver=resolver or socket.getaddrinfo
    opener=opener or urllib.request.urlopen
    result={'season':season,'source_url':url,'dns':'unknown','http':'not_checked','ready':False,'advice':''}
    try: resolver(host,443)
    except OSError as exc:
        result.update(dns='failed',advice=f'Cannot resolve {host}: {exc}. Check DNS, VPN, firewall or internet connection. Manual CSV upload is available.')
        return result
    result['dns']='ok'
    req=urllib.request.Request(url,headers={'User-Agent':'FourthDownAnalytics/1.8'},method='GET')
    try:
        with opener(req,timeout=15) as response:
            status=getattr(response,'status',200)
            sample=response.read(8192)
            content_type=response.headers.get('Content-Type','')
        result['http']=status
        if status != 200: result['advice']=f'Source returned HTTP {status}.'
        elif b'season' not in sample[:4096] or b'week' not in sample[:4096]:
            result['advice']='Response did not look like a weekly statistics CSV. Try a manual download.'
        else:
            result.update(ready=True,advice='Source is reachable and appears to contain a weekly CSV. Run one-season sync to validate the complete file.',content_type=content_type)
    except urllib.error.HTTPError as exc:
        result.update(http=exc.code,advice='Release asset not found. Use the manual NFLverse release link or try another season.' if exc.code==404 else f'HTTP {exc.code} from source.')
    except (urllib.error.URLError,OSError,TimeoutError) as exc:
        result['advice']=f'Connection failed: {exc}. Check network, VPN or firewall; manual CSV upload remains available.'
    return result
