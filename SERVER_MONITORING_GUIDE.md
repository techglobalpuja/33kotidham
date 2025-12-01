# 🔍 Server Message Status Monitoring Guide

## Quick Status Check Commands

### 1. **Full System Monitor** (Recommended First)
```bash
python monitor_notifications.py
```
**Shows:**
- Configuration settings
- Celery worker status
- Recent bookings (last 72 hours)
- WhatsApp message delivery status
- System recommendations

---

### 2. **Check WhatsApp Messages Only**
```bash
python check_whatsapp_status.py
```
**Shows:**
- All WhatsApp messages sent in last 72 hours
- Message status (queued, sent, delivered, failed)
- Account information
- Sandbox opt-in warnings

---

### 3. **Check Specific Message by SID**
```bash
python check_whatsapp_status.py SM1234567890abcdef...
```
Get detailed status for a specific message (SID found in logs)

---

### 4. **Check Recent Bookings**
```bash
python monitor_notifications.py bookings 24
```
Show bookings from last 24 hours

---

### 5. **Check Only Configuration**
```bash
python monitor_notifications.py config
```
Verify your .env settings

---

## 📊 Understanding WhatsApp Message Status

### Status Values:

| Status | Meaning | Action Needed |
|--------|---------|---------------|
| **queued** | ⏳ Waiting to send - **RECIPIENT NOT IN SANDBOX** | Recipient must send "join ancient-science" to +14155238886 |
| **sending** | 📤 Currently being sent | Wait a moment |
| **sent** | ✅ Delivered to WhatsApp | Success! |
| **delivered** | ✅ Received by recipient's phone | Success! |
| **failed** | ❌ Failed to send | Check error message |
| **undelivered** | ❌ Could not deliver | Check phone number format |

---

## 🚨 Common Issues & Solutions

### Issue 1: All messages are "queued"
**Problem:** Recipient hasn't joined WhatsApp Sandbox

**Solution:**
1. Recipient opens WhatsApp
2. Send to: `+14155238886`
3. Message: `join ancient-science`
4. Wait for confirmation

---

### Issue 2: No messages found
**Possible causes:**
- `SEND_WHATSAPP_ON_BOOKING=false` in .env
- `SEND_BOOKING_NOTIFICATIONS=false` in .env
- No bookings created recently
- Celery worker not running

**Check with:**
```bash
python monitor_notifications.py config
```

---

### Issue 3: Celery not processing
**Problem:** Worker not running

**Solution:**
```powershell
# Windows
.\start-worker.ps1

# Or manually
celery -A app.celery_config worker --loglevel=info --pool=solo
```

---

## 🔧 Monitoring from Server

### Option 1: SSH to Server and Run
```bash
# Connect to your server
ssh user@your-server

# Navigate to project
cd /path/to/33kotidham

# Run monitor
python monitor_notifications.py
```

### Option 2: Check Twilio Dashboard
1. Go to: https://console.twilio.com/
2. Navigate to: **Monitor → Logs → Messages**
3. Filter by: **WhatsApp messages**
4. See delivery status in real-time

### Option 3: Add API Endpoint (Optional)
Add this to your FastAPI app to check status via API:

```python
@router.get("/admin/notification-status")
async def get_notification_status(db: Session = Depends(get_db)):
    """Get notification system status."""
    # Run checks and return JSON
    pass
```

---

## 📝 Server Logs Location

Check application logs for notification details:
```bash
# If using systemd
sudo journalctl -u 33kotidham -f

# If using docker
docker logs 33kotidham -f

# If using PM2
pm2 logs 33kotidham

# Direct log file (if configured)
tail -f /var/log/33kotidham/app.log
```

---

## 🎯 Automated Monitoring Setup

### Create a Cron Job (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add this line to check every hour
0 * * * * cd /path/to/33kotidham && python check_whatsapp_status.py >> /var/log/whatsapp_monitor.log 2>&1
```

### Create a Scheduled Task (Windows)
```powershell
# Create scheduled task to run daily
schtasks /create /tn "WhatsAppMonitor" /tr "python C:\path\to\check_whatsapp_status.py" /sc daily /st 09:00
```

---

## 🔔 Set Up Alerts

### Monitor for "queued" messages:
```bash
#!/bin/bash
# alert_queued_messages.sh

OUTPUT=$(python check_whatsapp_status.py)

if echo "$OUTPUT" | grep -q "QUEUED"; then
    # Send alert email
    echo "$OUTPUT" | mail -s "WhatsApp Messages Queued!" admin@example.com
fi
```

---

## 📞 Quick Debugging Checklist

Run through this checklist:

```bash
# 1. Check configuration
python monitor_notifications.py config

# 2. Check if Celery is running
python monitor_notifications.py celery

# 3. Check recent bookings
python monitor_notifications.py bookings 24

# 4. Check WhatsApp message status
python check_whatsapp_status.py

# 5. Check Twilio account
python check_whatsapp_status.py account
```

---

## 💡 Pro Tips

1. **Save message SIDs** from your app logs for easy tracking
2. **Check logs immediately** after creating a test booking
3. **Use 72-hour window** for investigating issues
4. **Monitor during off-hours** to catch async processing issues
5. **Set up alerts** for "queued" or "failed" statuses

---

## 🆘 Getting Help

If messages still not working after monitoring:

1. Run full monitor and save output:
   ```bash
   python monitor_notifications.py > status_report.txt
   ```

2. Check Twilio Console for errors

3. Verify recipient has joined sandbox

4. Check server firewall isn't blocking Twilio webhook callbacks

---

**Last Updated:** December 1, 2025
