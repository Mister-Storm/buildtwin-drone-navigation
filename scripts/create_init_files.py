"""__init__.py files for all packages."""

# All __init__.py files
INIT_FILES = [
    "app/__init__.py",
    "app/api/__init__.py",
    "app/api/routes/__init__.py",
    "app/models/__init__.py",
    "app/services/__init__.py",
    "navigation/__init__.py",
    "navigation/core/__init__.py",
    "navigation/algorithms/__init__.py",
]

import os
base = "/home/mister-storm/development/buildtwin-drone-navigation"
for f in INIT_FILES:
    path = os.path.join(base, f)
    if not os.path.exists(path):
        with open(path, "w") as fh:
            fh.write("")
        print(f"Created: {f}")
    else:
        print(f"Exists: {f}")
