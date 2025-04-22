
from flask import Flask, request
import os
import requests
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64

app = Flask(__name__)

TO_EMAIL = os.getenv("TO_EMAIL")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")

def send_email(subject, body, media_url=None, media_type=None):
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAIL,
        subject=subject,
        plain_text_content=body,
    )

    if media_url:
        file_data = requests.get(media_url).content
        encoded_file = base64.b64encode(file_data).decode()
        attachment = Attachment(
            FileContent(encoded_file),
            FileName("attachment." + media_type.split("/")[-1]),
            FileType(media_type),
            Disposition("attachment")
        )
        message.attachment = attachment

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    sg.send(message)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    sender = request.form.get("From", "")
    message = request.form.get("Body", "")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    num_media = int(request.form.get("NumMedia", "0"))
    media_url = None
    media_type = None

    if num_media > 0:
        media_url = request.form.get("MediaUrl0")
        media_type = request.form.get("MediaContentType0")

    subject = f"New WhatsApp Message from {sender}"
    body = f"Time: {timestamp}\nFrom: {sender}\nMessage: {message}"

    send_email(subject, body, media_url, media_type)

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

