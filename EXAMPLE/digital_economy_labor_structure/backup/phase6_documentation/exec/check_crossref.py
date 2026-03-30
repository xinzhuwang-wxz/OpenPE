import subprocess
r = subprocess.run(["pandoc-crossref", "--version"], capture_output=True, text=True)
print("stdout:", r.stdout)
print("stderr:", r.stderr)
print("returncode:", r.returncode)
