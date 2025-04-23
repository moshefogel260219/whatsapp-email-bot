"""
whatsapp-email-bot / app.py
---------------------------
• מקבל Webhook מטוויליו-וואטסאפ
• מוריד קבצי מדיה (אם קיימים) עם HTTP Basic-Auth של Twilio
• שולח מייל דרך SendGrid +‬ קובץ מצורף (ב־Base64) ‬
"""

from flask import Flask, request
from datetime import datetime
from requests.auth import HTTPBasicAuth
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName, FileType, Disposition
)

import os, requests, base64

app = Flask(__name__)

# ──────────────── ENV ─────────────────
TO_EMAIL          = os.getenv("TO_EMAIL")          # כתובת היעד
FROM_EMAIL        = os.getenv("FROM_EMAIL")        # כתובת השולח (Sender Verified)
SENDGRID_API_KEY  = os.getenv("SENDGRID_API_KEY")  # מפתח SendGrid
TWILIO_ACCOUNT_SID= os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
# ──────────────────────────────────────


def send_email(subject: str,
               body: str,
               media_url: str | None = None,
               media_type: str | None = None) -> None:
    """שליחת דוא״ל (כולל קובץ מצורף אם media_url קיים)"""
    msg = Mail(
        from_email = FROM_EMAIL,
        to_emails  = TO_EMAIL,
        subject    = subject,
        plain_text_content = body,
    )

    # ░░ קובץ מצורף ░░
    if media_url:
        resp = requests.get(
            media_url,
            auth = HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout = 20
        )
        print(f"[media] status={resp.status_code} bytes={len(resp.content)}")

        if resp.status_code == 200 and resp.content:
            encoded = base64.b64encode(resp.content).decode()
            msg.attachment = Attachment(
                FileContent(encoded),
                FileName(f"attachment.{media_type.split('/')[-1]}"),
                FileType(media_type),
                Disposition("attachment")
            )
        else:
            print("[media] ⚠️  failed to fetch media — sending mail without attachment")

    # שליחה
    SendGridAPIClient(SENDGRID_API_KEY).send(msg)
    print("📧  e-mail sent via SendGrid")


@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """Twilio → Flask Webhook"""
    print("📥 webhook triggered — form keys:", list(request.form.keys()))

    sender   = request.form.get("From", "")
    text     = request.form.get("Body", "")
    ts       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    num_media = int(request.form.get("NumMedia", "0"))
    media_url  = request.form.get("MediaUrl0")          if num_media else None
    media_type = request.form.get("MediaContentType0")  if num_media else None

    subject = f"New WhatsApp Message from {sender}"
    body    = f"Time: {ts}\nFrom: {sender}\nMessage: {text}"

    send_email(subject, body, media_url, media_type)
    return "OK", 200


# Flask entry-point (Render מחפש זאת)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
