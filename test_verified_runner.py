import subprocess
import time
from pathlib import Path

jsfl = Path(r"C:\Users\jofin\test_verified.jsfl")
out_txt = Path(r"C:\Users\jofin\test_verified_out.txt")
fla = Path(r"C:\Users\jofin\test_verified.fla")

if out_txt.exists():
    out_txt.unlink()
if fla.exists():
    fla.unlink()

code = r"""
var outURI = FLfile.platformPathToURI("C:\\Users\\jofin\\test_verified_out.txt");
FLfile.write(outURI, "STAGE_1_START");

var doc = fl.createDocument();
var saveURI = FLfile.platformPathToURI("C:\\Users\\jofin\\test_verified.fla");
fl.saveDocument(doc, saveURI);
fl.closeDocument(doc, false);

FLfile.write(outURI, "STAGE_2_COMPLETE");
fl.quit(false);
"""
jsfl.write_text(code.strip(), encoding="utf-8")

cmd = [
    r"C:\Program Files\Adobe\Adobe Animate 2024\Animate.exe",
    "--run-jsfl",
    str(jsfl)
]
print("Running command:", " ".join(cmd), flush=True)
p = subprocess.Popen(cmd)

start = time.time()
while time.time() - start < 80:
    if out_txt.exists():
        content = out_txt.read_text()
        print(f"Progress ({int(time.time() - start)}s): {content}", flush=True)
        if "STAGE_2_COMPLETE" in content:
            print("Full script execution succeeded!", flush=True)
            break
    time.sleep(2)
else:
    print("TIMEOUT after 80 seconds", flush=True)

print(f"FLA created: {fla.exists()}", flush=True)
if fla.exists():
    print(f"FLA size: {fla.stat().st_size} bytes", flush=True)

# Cleanup
try:
    p.terminate()
except Exception:
    pass
