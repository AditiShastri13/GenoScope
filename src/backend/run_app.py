#!/usr/bin/env python

"""
Genoscope API Server Runner

This script starts the Genoscope API server with proper configuration
from environment variables.
"""

import sys
import os
import logging
import argparse
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("genoscope")

# Load environment variables from .env file if it exists
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    logger.info(f"Loaded environment from {dotenv_path}")
else:
    logger.warning(f".env file not found at {dotenv_path}. Using default or system environment variables.")

# Add the current directory to Python's path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Genoscope API Server")
    parser.add_argument("--host", default=os.getenv("API_HOST", "127.0.0.1"), 
                        help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=int(os.getenv("API_PORT", "8000")),
                        help="Port to bind the server to")
    parser.add_argument("--reload", action="store_true", default=False,
                        help="Enable auto-reload on code changes (development only)")
    parser.add_argument("--workers", type=int, default=int(os.getenv("API_WORKERS", "1")),
                        help="Number of worker processes")
    parser.add_argument("--log-level", default=os.getenv("API_LOG_LEVEL", "info"),
                        choices=["debug", "info", "warning", "error", "critical"],
                        help="Logging level")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    try:
        # Importing here to avoid loading the app before environment variables are set
        import uvicorn
        from app.main import app
        
        logger.info(f"Starting Genoscope API server...")
        logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        logger.info(f"Host: {args.host}, Port: {args.port}, Workers: {args.workers}")
        
        # Start the server
        uvicorn.run(
            "app.main:app", 
            host=args.host, 
            port=args.port,
            reload=args.reload,
            workers=args.workers,
            log_level=args.log_level
        )
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error("Please make sure you have installed all requirements with 'pip install -r requirements.txt'")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)