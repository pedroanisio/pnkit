from pathlib import Path
import subprocess,os,json,time,shutil
from PIL import Image
import numpy as np
root=Path(__file__).resolve().parents[1];folder=root/'27-caption-source-breaks';env=os.environ.copy();env.update(CARGO_TARGET_DIR='/home/pals/.cache/cx-engine-linebreaks-target',CARGO_BUILD_JOBS='8',SR_GPU_BACKEND='vulkan',SR_LINEBREAKS_ATLAS_DIR=str(folder))
cargo='/home/pals/.cargo/bin/cargo';manifest=str(root/'work/linebreaks-source/Cargo.toml');results=[]
for label,args in [('deliver-final',['test','--locked','--manifest-path',manifest,'-p','sr-deliver','--lib','captions::tests']),('gpu-final',['test','--locked','--manifest-path',manifest,'-p','sr-gpu','--test','text']),('clippy',['clippy','--locked','--manifest-path',manifest,'-p','sr-text','-p','sr-gpu','-p','sr-deliver','-p','sr-model','--all-targets','--','-D','warnings'])]:
    started=time.monotonic()
    with (root/f'work/linebreaks-{label}-tests.log').open('w') as log:p=subprocess.run([cargo,*args],stdin=subprocess.DEVNULL,stdout=log,stderr=log,env=env)
    results.append(dict(stage=label,exit=p.returncode,seconds=time.monotonic()-started));print(results[-1],flush=True)
    if p.returncode:raise RuntimeError(label+': '+(root/f'work/linebreaks-{label}-tests.log').read_text()[-5000:])
shutil.copy2(folder/'frames/0042.png',folder/'still.png')
with (folder/'legacy-pin-render.log').open('w') as log:p=subprocess.run(['/home/pals/.local/share/scene-render/bin/scene-render-premium','render',str(folder/'legacy.scene.xml'),'--time','1.75','-o',str(folder/'legacy-pin.png'),'--strict','--quality','final'],stdin=subprocess.DEVNULL,stdout=log,stderr=log)
if p.returncode:raise RuntimeError((folder/'legacy-pin-render.log').read_text())
a=np.array(Image.open(folder/'legacy-source-test.png').convert('RGBA'),dtype=int);b=np.array(Image.open(folder/'legacy-pin.png').convert('RGBA'),dtype=int);delta=np.abs(a-b);proof=dict(stages=results,frames=len(list((folder/'frames').glob('*.png'))),legacy_pin_rgba_max_difference=int(delta.max()),legacy_pin_different_components=int((delta!=0).sum()),legacy_pin_mean_absolute_difference=float(delta.mean()),scope='Native source test-library frames versus unchanged premium pinned render for document with no lineBreaks attribute. No candidate CLI build.')
(folder/'evidence.json').write_text(json.dumps(proof,indent=2));print(proof,flush=True)
