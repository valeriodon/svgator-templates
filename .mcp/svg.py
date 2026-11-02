"""Helper: calls the SVGator MCP from Python (through mcp.py) and returns the JSON of the result."""
import json,subprocess,os
D=os.path.dirname(os.path.abspath(__file__))
def call(name,args):
    import tempfile
    with tempfile.NamedTemporaryFile('w',suffix='.json',delete=False,dir=D) as f: json.dump(args,f); fn=f.name
    try: r=subprocess.run([os.path.join(D,'mcp.py'),'call',name,'@'+fn],capture_output=True,text=True)
    finally: os.remove(fn)
    if r.returncode: raise RuntimeError(r.stdout+r.stderr)
    o=json.loads(r.stdout)
    if 'error' in o: raise RuntimeError(json.dumps(o['error']))
    res=o['result']; t=res['content'][0]['text']
    try: j=json.loads(t)
    except Exception: j=t
    if res.get('isError'): raise RuntimeError(t[:3000])
    return j
def export_svg(pid,**kw):
    j=call('export_project',dict(project_id=pid,format='svg',inline=True,**kw))
    return j['content']
