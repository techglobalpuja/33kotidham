"""
Check the status of a Celery task
"""
from app.celery_config import celery_app
import sys

if len(sys.argv) > 1:
    task_id = sys.argv[1]
else:
    task_id = "d900cdbe-3217-47db-9123-838f1e9fa804"

result = celery_app.AsyncResult(task_id)

print(f"📋 Task ID: {task_id}")
print(f"📊 Status: {result.state}")
print(f"✅ Ready: {result.ready()}")
print(f"🎯 Successful: {result.successful() if result.ready() else 'Pending'}")

if result.ready():
    if result.successful():
        print(f"📦 Result: {result.result}")
    else:
        print(f"❌ Error: {result.result}")
        print(f"📜 Traceback: {result.traceback}")
