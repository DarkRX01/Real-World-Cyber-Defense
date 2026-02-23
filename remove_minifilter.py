#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

minifilter_path = Path(__file__).parent / "minifilter-rust"
if minifilter_path.exists():
    shutil.rmtree(minifilter_path)
    print(f"Deleted: {minifilter_path}")
else:
    print(f"Not found: {minifilter_path}")
