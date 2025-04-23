from flask import Flask, request
import os, requests, base64
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# ─── env vars ─────────────────────────────────────────────────────────────────
TO_EMAIL          = os.getenv("TO_EMAIL")
FROM_EMAIL        = os.getenv("FROM_EMAIL")
SENDGRID_API_KEY  = os.getenv("SENDGRID_API_KEY")
TWILIO_ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN")
# ──────────────────────────────────────────────────────────────────────────────


def send_email(subject, body, media_url=None, media_type=None):
    """Send e-mail (optionally with attachment) via SendGrid"""
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAIL,
        subject=subject,
        plain_text_content=body,
    )

    if media_url:
        resp = requests.get(media_url,
                            auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
        print(f"[media] status={resp.status_code} len={len(resp.content)}")
        if resp.status_code == 200:
            encoded = base64.b64encode(resp.content).decode()
            message.attachment = Attachment(
                FileContent(encoded),
                FileName("attachment." + media_type.split("/")[-1]),
                FileType(media_type),
                Disposition("attachment"),
            )
        else:
            print(f"[media] failed to fetch media: {resp.status_code}")

    SendGridAPIClient(SENDGRID_API_KEY).send(message)
    print("📧  e-mail sent")


@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    print("📥 webhook triggered ----------------------------")
    for k in request.form:
        print(f"{k} => {request.form[k]}")
    print("-----------------------------------------------")

    sender   = request.form.get("From", "")
    body_txt = request.form.get("Body", "")
    ts       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    num_media = int(request.form.get("NumMedia", 0))
    media_url = request.form.get("MediaUrl0") if num_media else None
    media_type= request.form.get("MediaContentType0") if num_media else None

    subject = f"New WhatsApp Message from {sender}"
    body    = f"Time: {ts}\nFrom: {sender}\nMessage: {body_txt}"

    send_email(subject, body, media_url, media_type)
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
