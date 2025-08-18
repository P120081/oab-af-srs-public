#!/usr/bin/env python3
from pathlib import Path
import sys

def main():
    root = Path(__file__).resolve().parents[1]
    print("Repo root:", root)
    print("OK")

if __name__ == "__main__":
    sys.exit(main())
