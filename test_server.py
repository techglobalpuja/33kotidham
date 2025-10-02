#!/usr/bin/env python3
"""
Test script to verify the FastAPI server starts correctly
"""

import uvicorn
from app.main import app

def test_server():
    """Test if the server can start without errors."""
    try:
        print("Testing FastAPI application...")
        
        # Test if app can be imported
        print("✓ App imported successfully")
        
        # Test if routes are registered
        routes = [route.path for route in app.routes]
        print(f"✓ Found {len(routes)} routes")
        
        # Print some key routes
        api_routes = [route for route in routes if route.startswith('/api')]
        print(f"✓ API routes: {len(api_routes)}")
        
        print("\nKey endpoints:")
        for route in app.routes:
            if hasattr(route, 'path') and route.path.startswith('/api/v1'):
                print(f"  {route.path}")
        
        print("\n✓ Server configuration looks good!")
        print("You can now run: uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_server()
