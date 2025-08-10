import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streamlit_app import app

def handler(request):
    """Vercel serverless function handler"""
    return app(request.environ, lambda status, headers: None)