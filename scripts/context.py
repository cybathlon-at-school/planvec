"""
Context file to enable proper importing for scripts outside of the main python planvec package.

In python scripts in the scripts folder use

from context import planvec

before any planvec import. Then you can use planvec normally.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import planvec
