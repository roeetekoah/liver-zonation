#!/usr/bin/env python3
"""Thin shim — the Step 4b implementation now lives in src/steps/step4b_classifier.py
(single source of truth). Kept so `python classifier.py` and `import classifier` still work.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # src/ on path
from steps.step4b_classifier import (  # noqa: F401  (re-export for backward compatibility)
    main, classify_entropy, load_p1, load_p2, derive_labels, LABEL_SOURCE,
)

if __name__ == "__main__":
    main()
