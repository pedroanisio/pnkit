import build_showcase_extra
import subprocess,sys
subprocess.run([sys.executable,'work/render_stills.py','01-pbr-key-rim','02-hdri-ao-ssr','03-dof-focus-pull','04-25d-parallax','05-pathtrace-hero','06-materials','07-particles-path-alpha','08-grade-lut-look'],stdin=subprocess.DEVNULL,check=True)
