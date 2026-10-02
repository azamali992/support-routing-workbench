"""python run.py [--reset] [--port 8763]; no dependency required."""
import argparse,http.server,functools
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8763);p.add_argument('--reset',action='store_true');a=p.parse_args()
print(f'Support routing: http://127.0.0.1:{a.port}/'+('?reset=1' if a.reset else ''))
print('Reset state is automatic on every page load; no stored customer data.')
http.server.ThreadingHTTPServer(('127.0.0.1',a.port),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(Path(__file__).parent))).serve_forever()
