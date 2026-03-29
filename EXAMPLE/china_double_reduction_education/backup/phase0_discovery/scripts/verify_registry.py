"""Verify the registry is complete and well-formed."""
import yaml

with open("phase0_discovery/data/registry.yaml") as f:
    reg = yaml.safe_load(f)

print(f"Total datasets: {len(reg['datasets'])}")
print()
for i, ds in enumerate(reg["datasets"], 1):
    status = ds.get("status", "unknown")
    name = ds.get("name", "unnamed")
    print(f"{i:2d}. [{status:8s}] {name}")
print()
acquired = sum(1 for d in reg["datasets"] if d.get("status") == "acquired")
failed = sum(1 for d in reg["datasets"] if d.get("status") == "failed")
print(f"Acquired: {acquired}, Failed: {failed}")
