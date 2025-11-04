# PowerShell script to start Celery worker
# Usage: .\start-worker.ps1

Write-Host ""
Write-Host "======================================================================"
Write-Host "Starting Celery Worker for Booking Notifications"
Write-Host "======================================================================"
Write-Host ""
Write-Host "Queue: notifications"
Write-Host "Tasks: send_booking_notification"
Write-Host ""
Write-Host "Press Ctrl+C to stop"
Write-Host "======================================================================"
Write-Host ""

# Start Celery worker
celery -A app.celery_config.celery_app worker --loglevel=info --pool=solo -Q notifications --concurrency=1 -n notification_worker@$env:COMPUTERNAME
