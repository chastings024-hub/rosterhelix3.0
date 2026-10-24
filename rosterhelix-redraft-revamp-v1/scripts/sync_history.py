#!/usr/bin/env python3
"""Download NFLverse weekly player stats for multiple seasons and merge atomically.

Requires network access. Failed seasons do not partially alter the local database.
"""
import argparse, datetime, json, time, urllib.request, urllib.error, socket
from pathlib import Path
from history_store import parse, merge
from update_data import URL

MAX_DOWNLOAD=35_000_000

def fetch(season, base_url=URL, attempts=3, opener=None):
    url=base_url.format(season=season)
    if not url.startswith('https://'):
        raise ValueError('Only HTTPS data sources are allowed')
    opener=opener or urllib.request.urlopen
    last=None
    for attempt in range(attempts):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'FourthDownAnalytics/1.3 (historical NFL data sync)'})
            with opener(req,timeout=35) as response:
                content=response.read(MAX_DOWNLOAD+1)
            if len(content)>MAX_DOWNLOAD:
                raise ValueError(f'{season}: source CSV exceeds 35 MB')
            return parse(content,'nflverse',str(season))
        except urllib.error.HTTPError as exc:
            if exc.code in (404, 410):
                raise RuntimeError(f'{season}: NFLverse file not found (HTTP {exc.code}). Check the release assets: {url}') from exc
            last=f'HTTP {exc.code} from NFLverse'
        except urllib.error.URLError as exc:
            reason=str(exc.reason)
            last=f'Cannot reach NFLverse ({reason}). Check internet, firewall, VPN, or DNS. Try downloading the CSV in your browser.'
        except (OSError,ValueError,RuntimeError) as exc:
            last=str(exc)
        if attempt+1<attempts: time.sleep(min(2**attempt,4))
    raise RuntimeError(f'{season}: download or validation failed: {last}')

def sync(start,end,fetcher=fetch):
    current=datetime.datetime.now(datetime.timezone.utc).year
    if not 1999<=start<=end<=current or end-start>25:
        raise ValueError(f'Season range must be between 1999 and {current}, maximum 26 seasons')
    records=[]; counts={}
    for season in range(start,end+1):
        rows=fetcher(season)
        if not rows:raise ValueError(f'{season}: empty season')
        counts[str(season)]=len(rows);records.extend(rows)
    meta=merge(records)  # One commit after ALL seasons validate.
    meta['historical_sync']={'source':'NFLverse stats_player weekly releases','requested_seasons':[start,end],'season_row_counts':counts,'completed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_verified_by':'HTTPS download; publisher authenticity and licensing must be independently assessed'}
    path=Path(__file__).resolve().parents[1]/'data'/'metadata.json'
    path.write_text(json.dumps(meta,indent=2)+'\n')
    return meta

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--start',type=int,default=2020)
    p.add_argument('--end',type=int,default=datetime.datetime.now(datetime.timezone.utc).year)
    args=p.parse_args()
    print(json.dumps(sync(args.start,args.end),indent=2))
