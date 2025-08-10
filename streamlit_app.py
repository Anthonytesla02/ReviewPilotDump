#!/usr/bin/env python3

"""
Streamlit app wrapper for Vercel deployment
"""

import streamlit as st
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main app
from app import main

if __name__ == "__main__":
    main()