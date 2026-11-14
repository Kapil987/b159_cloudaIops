import os, socket, pathlib, requests
from urllib.parse import urlparse

env_path = pathlib.Path('.env')
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line=line.strip()
        if line and not line.startswith('#') and '=' in line:
            k,v = line.split('=',1)
            os.environ.setdefault(k.strip(), v.strip())
inst = os.environ.get('SERVICENOW_INSTANCE')
print('instance=', inst)
if not inst:
    raise SystemExit('SERVICENOW_INSTANCE not set')
parsed = urlparse(inst if inst.startswith('http') else 'https://' + inst)
host = parsed.netloc
print('host=', host)
print('resolve=', socket.gethostbyname(host))
user = os.environ.get('SERVICENOW_USERNAME')
pwd = os.environ.get('SERVICENOW_PASSWORD')
print('user set=', bool(user), 'pwd set=', bool(pwd))
resp = requests.get(f'{parsed.scheme}://{host}/api/now/table/incident', auth=(user, pwd), headers={'Accept': 'application/json'}, params={'sysparm_limit':1})
print('status', resp.status_code)
print(resp.text[:500])
