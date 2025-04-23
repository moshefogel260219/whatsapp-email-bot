from flask import Flask, request
import os, base64, requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

app = Flask(__name__)

# --- env ---
TO_EMAIL           = os.getenv("TO_EMAIL")
FROM_EMAIL         = os.getenv("FROM_EMAIL")
SENDGRID_API_KEY   = os.getenv("SENDGRID_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")


# ---------- helpers ----------
def send_email(subject, body, media_url=None, media_type=None):
    """build & send email (optionally with attachment) via SendGrid"""
    msg = Mail(from_email=FROM_EMAIL,
               to_emails=TO_EMAIL,
               subject=subject,
               plain_text_content=body)

    if media_url:
        r = requests.get(media_url, auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
        print(f"[Fetch media] status={r.status_code} len={len(r.content)} url={media_url}")

        if r.ok and r.content:
            encoded = base64.b64encode(r.content).decode()
            fname   = "attachment." + media_type.split("/")[-1]
            msg.attachment = Attachment(
                FileContent(encoded),
                FileName(fname),
                FileType(media_type),
                Disposition("attachment")
            )
        else:
            print("[!] media fetch failed – attachment skipped")

    SendGridAPIClient(SENDGRID_API_KEY).send(msg)
    print("✅ email sent")


# ---------- webhook ----------
@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    print("📥 webhook triggered")
    print("------ request.form ------")
    for k, v in request.form.items():
        print(f"{k}: {v}")
    print("--------------------------")

    num_media = int(request.form.get("NumMedia", "0"))
    media_url = request.form.get("MediaUrl0") if num_media else None
    media_type = request.form.get("MediaContentType0") if num_media else None

    print(f"NumMedia={num_media} url={media_url} type={media_type}")

    sender    = request.form.get("From", "")
    text      = request.form.get("Body", "")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    subj = f"New WhatsApp Message from {sender}"
    body = f"Time: {timestamp}\nFrom: {sender}\nMessage: {text or '[no text]'}"

    send_email(subj, body, media_url, media_type)
    return "OK", 200


# ---------- local run ----------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
