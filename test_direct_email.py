#!/usr/bin/env python
"""Direct email test to verify notification system."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL')

# Test recipient
TO_EMAIL = "nawabkh2040@gmail.com"

print("=" * 70)
print("📧 SENDING TEST EMAIL")
print("=" * 70)

try:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🙏 Test Booking Notification - 33 Koti Dham"
    msg["From"] = SMTP_FROM_EMAIL
    msg["To"] = TO_EMAIL

    # Plain text version
    text = """Dear Customer,

This is a TEST email from 33 Koti Dham notification system.

If you received this email, it means:
✅ Email notifications are WORKING
✅ Booking notifications WILL be sent to you

Booking ID: TEST-001
Status: PENDING
Amount: ₹1.00

Thank you for choosing 33 Koti Dham!

Best regards,
33 Koti Dham Team
"""

    # HTML version
    html = """<html>
<body>
<h2>🙏 Test Booking Notification</h2>
<p>Dear Customer,</p>
<p>This is a <strong>TEST email</strong> from 33 Koti Dham notification system.</p>
<p>If you received this email, it means:</p>
<ul>
    <li>✅ Email notifications are <strong>WORKING</strong></li>
    <li>✅ Booking notifications <strong>WILL be sent</strong> to you</li>
</ul>
<hr>
<p><strong>Booking Details:</strong></p>
<ul>
    <li>Booking ID: TEST-001</li>
    <li>Status: PENDING</li>
    <li>Amount: ₹1.00</li>
</ul>
<p>Thank you for choosing 33 Koti Dham!</p>
<p>Best regards,<br><strong>33 Koti Dham Team</strong></p>
</body>
</html>"""

    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    # Send email
    print(f"\n📬 Connecting to SMTP server: {SMTP_HOST}:{SMTP_PORT}")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        print(f"✓ TLS connection established")
        
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        print(f"✓ Authentication successful")
        
        server.send_message(msg)
        print(f"✓ Email sent successfully!")

    print(f"\n" + "=" * 70)
    print(f"✅ SUCCESS! Test email sent to: {TO_EMAIL}")
    print(f"=" * 70)
    print(f"\nCheck your email inbox/spam folder for the test message.")
    print(f"If you receive it, notifications are working!")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
