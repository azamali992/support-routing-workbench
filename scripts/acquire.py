"""Fetch immutable public publisher files, verify bytes, preserve provenance."""
from pathlib import Path
import urllib.request, hashlib, json, datetime, argparse, shutil
ROOT = Path(__file__).resolve().parents[1]
COMMIT = '57ec275d8078af65b7731c2a98be812d844a6d6b'
FILES = {'train.csv': ('banking_data/train.csv','b06e26ac675513959a63135f11b94ea7786ed02da65db93a5650d8838cbc664b'), 'test.csv': ('banking_data/test.csv','d12d6e3bc4c3103966ae786dc435913c0c563dfa328f5a3646d0e62cfeeb474d'), 'LICENSE.txt': ('LICENSE','7e7170e3cebf88a9f60c7b8421418323c09304da1af4d5e90f4da1dc1c8a2661')}
def main():
    p=argparse.ArgumentParser();p.add_argument('--verified-cache',type=Path);a=p.parse_args()
    out=ROOT/'data'/'raw';out.mkdir(parents=True,exist_ok=True);ledger=[]
    for name,(remote,expected) in FILES.items():
        url=f'https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/{COMMIT}/{remote}'
        if a.verified_cache:
            source=a.verified_cache/('banking-'+name.replace('LICENSE.txt','LICENSE.txt'))
            payload=source.read_bytes();date='2026-10-02';method='Previously acquired publisher bytes; checksum verified'
        else:
            payload=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AzamSupportRoutingDemo/1.0'}),timeout=60).read();date=datetime.datetime.now(datetime.timezone.utc).date().isoformat();method='HTTPS immutable publisher URL'
        digest=hashlib.sha256(payload).hexdigest()
        if digest!=expected:raise ValueError(f'Checksum changed: {name}, received {digest}')
        (out/name).write_bytes(payload)
        ledger.append(dict(file=name,url=url,sha256=digest,bytes=len(payload),retrieval_date=date,method=method))
    (ROOT/'data'/'provenance.json').write_text(json.dumps({'publisher_commit':COMMIT,'licence':'CC BY 4.0','files':ledger},indent=2)+'\n')
    shutil.copyfile(out/'LICENSE.txt',ROOT/'data'/'LICENSE-CC-BY-4.0.txt')
    print('Acquired and hash-verified all three public files.')
if __name__=='__main__':main()
