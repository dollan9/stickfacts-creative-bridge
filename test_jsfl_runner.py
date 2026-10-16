import os
import time
from pathlib import Path

cmd_dir = Path(r"C:\Users\jofin\AppData\Local\Adobe\Animate 2024\sv_SE\Configuration\Commands")
cmd_dir.mkdir(parents=True, exist_ok=True)
script = cmd_dir / "test_pipeline.jsfl"
out_txt = Path(r"C:\Users\jofin\test_out.txt")

if out_txt.exists():
    out_txt.unlink()

code = r"""
var outURI = FLfile.platformPathToURI("C:\\Users\\jofin\\test_out.txt");
FLfile.write(outURI, "SUCCESS_FROM_COMMANDS_FOLDER");
fl.quit(false);
"""
script.write_text(code.strip(), encoding="utf-8")
print(f"Script written to: {script}")

print("Executing script via os.startfile...")
os.startfile(str(script))

start = time.time()
while time.time() - start < 35:
    if out_txt.exists():
        print(f"SUCCESS! File output: {out_txt.read_text()}")
        break
    time.sleep(1)
else:
    print("TIMEOUT waiting for os.startfile")

if script.exists():
    script.unlink()
if out_txt.exists():
    out_txt.unlink()
