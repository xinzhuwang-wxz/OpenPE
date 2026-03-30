import subprocess
result = subprocess.run(["fc-list"], capture_output=True, text=True)
for line in result.stdout.splitlines():
    if "latin" in line.lower() or "lmodern" in line.lower() or "libertinus" in line.lower() or "computer modern" in line.lower():
        print(line)
