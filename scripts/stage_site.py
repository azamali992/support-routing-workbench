"""Stage the public static demo only: no training data or audit labels."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'site';out.mkdir(exist_ok=True)
for name in ['index.html','style.css','app.js','README.md','DATA.md']:
 shutil.copyfile(ROOT/name,out/name)
for name in ['public']:
 shutil.copytree(ROOT/name,out/name,dirs_exist_ok=True)
for name in ['evaluation/results.json','evaluation/ood-fixtures.json','data/LICENSE-CC-BY-4.0.txt','data/provenance.json']:
 target=out/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
(out/'.nojekyll').write_text('')
print('Staged static demo in site/; no test labels or training data included.')
