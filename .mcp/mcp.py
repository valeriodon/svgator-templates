#!/usr/bin/env python3
"""Minimal client for the SVGator MCP server (Streamable HTTP + OAuth with token refresh).
usage: mcp.py tools | mcp.py call NAME '{"arg":1}' | mcp.py raw METHOD '{params}'

Credentials are read from files next to this script, all ignored by git:
  client.json   the OAuth client registered with the server (needs "client_id")
  token.json    the OAuth tokens (needs "access_token" and "refresh_token"); rewritten on refresh
  session.txt   the MCP session id, cached for 30 minutes
See client.example.json, token.example.json and docs/svgator-mcp.md."""
import json,sys,os,time,urllib.request,urllib.parse,http.client
D=os.path.dirname(os.path.abspath(__file__))
URL='https://mcp.svgator.com/mcp'
def load(n): return json.load(open(os.path.join(D,n)))
def save(n,o):
    p=os.path.join(D,n); json.dump(o,open(p,'w')); os.chmod(p,0o600)
def refresh():
    t=load('token.json'); c=load('client.json')
    d=urllib.parse.urlencode({'grant_type':'refresh_token','refresh_token':t['refresh_token'],'client_id':c['client_id'],'resource':URL}).encode()
    r=json.loads(urllib.request.urlopen(urllib.request.Request('https://mcp.svgator.com/token',data=d)).read())
    if 'refresh_token' not in r: r['refresh_token']=t['refresh_token']
    save('token.json',r); return r
def post(body,sid=None,retry=True):
    t=load('token.json')
    h={'Content-Type':'application/json','Accept':'application/json, text/event-stream','Authorization':'Bearer '+t['access_token'],'MCP-Protocol-Version':'2025-06-18'}
    if sid: h['Mcp-Session-Id']=sid
    try:
        r=urllib.request.urlopen(urllib.request.Request(URL,data=json.dumps(body).encode(),headers=h),timeout=600)
    except urllib.error.HTTPError as e:
        # 401: refresh the token once; 404 on a session: let rpc() open a new one; 5xx: retry with backoff
        if e.code==401 and retry: refresh(); return post(body,sid,False)
        if e.code==404 and sid:
            txt=e.read().decode()
            if 'session' in txt.lower(): return json.loads(txt),sid
            raise SystemExit(f'HTTP 404: {txt[:2000]}')
        if e.code in (502,503,504) and retry is not False:
            n=retry if isinstance(retry,int) and retry is not True else 0
            if n<4:
                time.sleep(2*(2**n)); return post(body,sid,n+1)
        raise SystemExit(f'HTTP {e.code}: {e.read().decode()[:2000]}')
    except (urllib.error.URLError, TimeoutError) as e:
        n=retry if isinstance(retry,int) and retry is not True else 0
        if n<4: time.sleep(2*(2**n)); return post(body,sid,n+1)
        raise
    sid=r.headers.get('Mcp-Session-Id') or sid
    try: raw=r.read().decode()
    except (http.client.IncompleteRead, ConnectionError, TimeoutError):
        n=retry if isinstance(retry,int) and retry is not True else 0
        if n<4: time.sleep(2*(2**n)); return post(body,sid,n+1)
        raise
    if not raw.strip(): return None,sid
    if r.headers.get('Content-Type','').startswith('text/event-stream'):
        msgs=[json.loads(l[5:]) for l in raw.splitlines() if l.startswith('data:') and l[5:].strip()]
        msg=[m for m in msgs if 'id' in m and m.get('id')==body.get('id')] or msgs
        return msg[-1],sid
    return json.loads(raw),sid
def session():
    sp=os.path.join(D,'session.txt')
    if os.path.exists(sp) and time.time()-os.path.getmtime(sp)<1800:
        return open(sp).read().strip()
    r,sid=post({'jsonrpc':'2.0','id':0,'method':'initialize','params':{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'launch-card-mcp-client','version':'1'}}})
    post({'jsonrpc':'2.0','method':'notifications/initialized'},sid)
    open(sp,'w').write(sid or ''); return sid
def rpc(method,params):
    sid=session()
    r,_=post({'jsonrpc':'2.0','id':int(time.time()*1000)%10**9,'method':method,'params':params},sid)
    if r and r.get('error',{}).get('message','').lower().find('session')>=0:
        os.remove(os.path.join(D,'session.txt')); sid=session()
        r,_=post({'jsonrpc':'2.0','id':1,'method':method,'params':params},sid)
    return r
if __name__=='__main__':
    a=sys.argv[1:]
    if a[0]=='tools': r=rpc('tools/list',{})
    elif a[0]=='call':
        arg=(json.load(open(a[2][1:])) if a[2].startswith('@') else json.loads(a[2])) if len(a)>2 else {}
        r=rpc('tools/call',{'name':a[1],'arguments':arg})
    else: r=rpc(a[1],json.loads(a[2]) if len(a)>2 else {})
    print(json.dumps(r,indent=1,ensure_ascii=False))
