import json,subprocess,sys
from pathlib import Path
slugs=json.loads(Path('work/remaining-encode.json').read_text());p=subprocess.run([sys.executable,'work/encode_clips.py',*slugs],stdin=subprocess.DEVNULL);Path('work/remaining-encode.done').write_text(str(p.returncode))
