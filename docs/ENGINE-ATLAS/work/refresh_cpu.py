from pathlib import Path
import json,subprocess,sys
items=json.loads(Path('work/catalog.json').read_text());slugs=[x['slug'] for x in items if int(x['slug'].split('-')[0]) in range(9,26)]
subprocess.run([sys.executable,'work/render_stills.py',*slugs],stdin=subprocess.DEVNULL,check=True)
