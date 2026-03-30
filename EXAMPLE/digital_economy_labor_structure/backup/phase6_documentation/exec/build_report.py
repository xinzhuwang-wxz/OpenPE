import subprocess
import sys
import shutil

result = subprocess.run(
    [
        "pandoc",
        "REPORT.md",
        "-o",
        "REPORT.pdf",
        "--pdf-engine=tectonic",
        "--number-sections",
        "--toc",
        "--filter=pandoc-crossref",
        "--citeproc",
        "--bibliography=references.bib",
        "-V", "geometry:margin=1in",
        "-V", "fontsize=11pt",
        "-V", "colorlinks=true",
    ],
    capture_output=True,
    text=True,
    cwd="phase6_documentation/exec",
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)

if result.returncode == 0:
    shutil.copy("phase6_documentation/exec/REPORT.pdf", "REPORT.pdf")
    print("Copied REPORT.pdf to analysis root.")

sys.exit(result.returncode)
