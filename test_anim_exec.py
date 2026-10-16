import subprocess
import time
from pathlib import Path

jsfl = Path("C:/Users/jofin/test_min.jsfl")
res_txt = Path("C:/Users/jofin/animate_test.txt")

if res_txt.exists():
    res_txt.unlink()

code = """
FLfile.write("file:///C:/Users/jofin/animate_test.txt", "SUCCESS_ANIMATE_API");
fl.quit(false);
"""
jsfl.write_text(code, encoding="utf-8")
print(f"Launching Animate with {jsfl}...")
p = subprocess.Popen([r"C:\Program Files\Adobe\Adobe Animate 2024\Animate.exe", str(jsfl)])

start = time.time()
while time.time() - start < 35:
    if res_txt.exists():
        print(f"File created! Content: {res_txt.read_text()}")
        break
    time.sleep(1)
else:
    print("Timeout waiting for output")

if jsfl.exists():
    jsfl.unlink()
if res_txt.exists():
    res_txt.unlink()
