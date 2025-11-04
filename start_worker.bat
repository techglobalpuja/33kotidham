@echo off
echo ======================================================================
echo Starting Celery Worker for Booking Notifications
echo ======================================================================
echo.
echo This worker will process notification messages from the queue
echo Messages are processed one by one for each user
echo.
echo Queue: notifications
echo Tasks: send_booking_notification
echo.
echo Press Ctrl+C to stop the worker
echo ======================================================================
echo.

REM Start Celery worker for Windows
celery -A app.celery_config.celery_app worker --loglevel=info --pool=solo -Q notifications --concurrency=1 -n notification_worker@%%h

pause
