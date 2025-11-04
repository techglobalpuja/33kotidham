"""
Celery Worker Startup Script for Windows
Run this to start the Celery worker for processing notification queue
"""
import subprocess
import sys
import os

def start_celery_worker():
    """Start Celery worker for processing notifications"""
    
    # Set the working directory to the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    print("=" * 70)
    print("Starting Celery Worker for Booking Notifications")
    print("=" * 70)
    print()
    print("This worker will process notification messages from the queue")
    print("Messages are processed one by one for each user")
    print()
    print("Queue: notifications")
    print("Tasks: send_booking_notification")
    print()
    print("Press Ctrl+C to stop the worker")
    print("=" * 70)
    print()
    
    # Celery command for Windows
    cmd = [
        sys.executable,  # Python executable
        "-m",
        "celery",
        "-A",
        "app.celery_config.celery_app",  # Celery app location
        "worker",
        "--loglevel=info",
        "--pool=solo",  # Use solo pool for Windows
        "-Q",
        "notifications",  # Process notifications queue
        "--concurrency=1",  # Process one message at a time
        "-n",
        "notification_worker@%h"  # Worker name
    ]
    
    try:
        # Run Celery worker
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n\nStopping Celery worker...")
        print("Worker stopped successfully")
    except Exception as e:
        print(f"\n\nError starting Celery worker: {e}")
        print("\nMake sure:")
        print("1. Redis is running (redis-server)")
        print("2. Celery is installed (pip install celery redis)")
        print("3. You're in the correct directory")
        sys.exit(1)


if __name__ == "__main__":
    start_celery_worker()
