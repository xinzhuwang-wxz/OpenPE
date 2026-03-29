"""Quick utility to read upstream data files for verification."""
import json
import sys
import os

path = sys.argv[1]
with open(path) as f:
    d = json.load(f)
print(json.dumps(d, indent=2)[:5000])
