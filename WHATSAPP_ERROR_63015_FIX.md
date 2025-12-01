# 🔥 WhatsApp Error 63015 - SOLUTION GUIDE

## ❌ Problem Identified

**Error Code:** 63015  
**Meaning:** Media file could not be downloaded by Twilio/WhatsApp  
**Your Booking:** #106 to phone `8962507486`  
**Failed Message SID:** `MM40d37d7e30aa53a4aebb000ddfc91255`

---

## 🎯 Root Cause

The WhatsApp message failed because the **image attachment** could not be downloaded. Common causes:

1. **Image format not supported** (.webp, .svg - NOT supported by WhatsApp)
2. **Image URL not publicly accessible** (requires authentication, blocked by firewall)
3. **Wrong domain in fallback URL** (was .com, should be .in)
4. **SSL/HTTPS issues** (certificate problems)
5. **Image server blocking Twilio's servers**

---

## ✅ Fixes Applied

### 1. **Fixed Fallback Image URL**
```python
# OLD (WRONG):
default_fallback_image = "https://api.33kotidham.com/uploads/..."

# NEW (CORRECT):
default_fallback_image = "https://api.33kotidham.in/uploads/..."
```

### 2. **Added Automatic Retry Without Media**
If message with image fails, system now automatically retries **without the image**.

```python
# Try with media first
whatsapp_sent = send_whatsapp_notification(phone, message, media_url=image)

# If failed, retry without media
if not whatsapp_sent and media_url:
    whatsapp_sent = send_whatsapp_notification(phone, message, media_url=None)
```

This ensures the **message always gets delivered**, even if the image fails.

---

## 🚀 Deploy the Fix

### On Your Server:

```bash
cd ~/backend/33kotidham

# Pull the latest code
git pull origin master

# Restart your API server
sudo systemctl restart 33kotidham
# OR if using PM2:
pm2 restart 33kotidham
# OR if using uvicorn directly:
pkill -f uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**No need to restart Celery worker** - it will pick up the changes automatically.

---

## 🧪 Test the Fix

### Option 1: Test Simple Message (Recommended First)

```bash
cd ~/backend/33kotidham
source .venv/bin/activate

# Send test message WITHOUT media
python test_whatsapp_simple.py 8962507486
```

This will send a simple text message to verify WhatsApp is working.

### Option 2: Test Full Notification

Create a new test booking through your API and check if message delivers.

---

## 🔍 Verify Image URL is Accessible

Check if your fallback image is publicly accessible:

```bash
# Test from server
curl -I https://api.33kotidham.in/uploads/images/b4bd9c33-d6e3-4069-b436-ef8e4c5cfaa0.png

# Should return:
# HTTP/2 200
# content-type: image/png
```

If this fails, you need to:
1. Upload a valid fallback image
2. Ensure it's publicly accessible
3. Use HTTPS (not HTTP)

---

## 📊 Monitor After Fix

After deploying, create a test booking and run:

```bash
cd ~/backend/33kotidham
source .venv/bin/activate

# Check recent messages
python check_whatsapp_status.py
```

Look for:
- ✅ Status: `sent` or `delivered` (SUCCESS)
- ❌ Status: `failed` (still failing - check error code)

---

## 🎯 What Changed in Code

### File: `app/services.py`

**Line ~929:** Fixed fallback image URL
```python
default_fallback_image = "https://api.33kotidham.in/uploads/..."  # Changed .com to .in
```

**Lines ~952-958:** Added automatic retry without media
```python
# Try with media
whatsapp_sent = send_whatsapp_notification(phone, message, media_url=media_url)

# Retry without media if failed
if not whatsapp_sent and media_url:
    print(f"⚠️ Retrying WITHOUT media...")
    whatsapp_sent = send_whatsapp_notification(phone, message, media_url=None)
```

---

## 💡 Understanding WhatsApp Media Errors

### Error 63015 Causes:

| Cause | Solution |
|-------|----------|
| Unsupported format (.webp, .svg) | Use only: .jpg, .jpeg, .png, .gif |
| URL not accessible | Ensure image is publicly accessible via HTTPS |
| Image too large | Keep images under 5MB |
| Server blocking Twilio | Whitelist Twilio's IP ranges |
| SSL certificate issues | Ensure valid HTTPS certificate |

### Supported Image Formats:
- ✅ .jpg / .jpeg
- ✅ .png
- ✅ .gif
- ✅ .bmp
- ❌ .webp (NOT supported)
- ❌ .svg (NOT supported)
- ❌ .ico (NOT supported)

---

## 🔄 Fallback Strategy

Your system now has a **3-tier fallback**:

1. **Try puja image** (if exists and supported format)
2. **Try fallback image** (if puja image fails/unsupported)
3. **Send without image** (if both fail - NEW!)

This ensures messages **always deliver**, even if images fail.

---

## 📱 About WhatsApp Sandbox

Remember: Recipients still need to join the sandbox:

1. Open WhatsApp
2. Send to: `+14155238886`
3. Message: `join ancient-science`
4. Wait for confirmation

**Without joining sandbox:**
- Error 63007: "Recipient not in sandbox"
- Messages get queued but never delivered

**After joining sandbox:**
- Messages deliver immediately
- Works for 72 hours per user
- Need to re-join after 72 hours of inactivity

---

## 🆘 If Still Failing After Fix

### 1. Check error code of new message:
```bash
python check_whatsapp_status.py
# Look at the newest message SID

python check_failed_message.py
# Enter the new SID when prompted
```

### 2. Different error codes mean different issues:
- **63015**: Still media issue (check image URL)
- **63007**: User needs to join sandbox
- **63016**: Image too large
- **21211**: Invalid phone number

### 3. Test without media:
```bash
python test_whatsapp_simple.py 8962507486
```

If this works, the issue is definitely with the image attachment.

---

## ✅ Success Criteria

After fix, you should see:

```bash
python monitor_notifications.py

# Expected output:
✅ Found 1 message(s)
✅ SENT: 1 message(s)    # or DELIVERED
   • To: whatsapp:+918962507486
     SID: MM...
     Date: 2025-12-01 XX:XX:XX+00:00
```

---

## 📝 Summary

**What was wrong:**
- Image attachment could not be downloaded (Error 63015)
- Fallback URL had wrong domain (.com instead of .in)
- No retry mechanism if media failed

**What was fixed:**
- Corrected fallback image URL
- Added automatic retry without media
- Messages now always deliver (even without image)

**Next steps:**
1. Deploy changes (git pull, restart API)
2. Test with `test_whatsapp_simple.py`
3. Create real booking and verify delivery
4. Check message status with `check_whatsapp_status.py`

---

**Date Fixed:** December 1, 2025  
**Files Changed:** `app/services.py`  
**Impact:** All future bookings will auto-retry without media if image fails
