import subprocess
import time
from pathlib import Path

jsfl = Path(r"C:\Users\jofin\test_always.jsfl")
out_txt = Path(r"C:\Users\jofin\test_always_out.txt")

if out_txt.exists():
    out_txt.unlink()

code = r"""
var doc = fl.createDocument();
var saveURI = FLfile.platformPathToURI("C:\\Users\\jofin\\test_always.fla");
fl.saveDocument(doc, saveURI);
fl.closeDocument(doc, false);

var outURI = FLfile.platformPathToURI("C:\\Users\\jofin\\test_always_out.txt");
FLfile.write(outURI, "SUCCESS_ALWAYS_RUN_JSFL");
fl.quit(false);
"""
jsfl.write_text(code.strip(), encoding="utf-8")

cmd = [
    r"C:\Program Files\Adobe\Adobe Animate 2024\Animate.exe",
    str(jsfl),
    "-AlwaysRunJSFL"
]
print("Running command:", " ".join(cmd))
proc = subprocess.Popen(cmd)

start = time.time()
while time.time() - start < 35:
    if out_txt.exists():
        print(f"SUCCESS! Output: {out_txt.read_text()}")
        break
    time.sleep(1)
else:
    print("TIMEOUT")

fla = Path(r"C:\Users\jofin\test_always.fla")
print("FLA created:", fla.exists())
if fla.exists():
    print("FLA size:", fla.stat().st_size)
    fla.unlink()

if jsfl.exists():
    jsfl.unlink()
if out_txt.exists():
    out_txt.unlink()
