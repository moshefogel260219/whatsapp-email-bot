from flask import Flask, request
import os
import requests
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from requests.auth import HTTPBasicAuth
import base64

app = Flask(__name__)

# Environment variables
TO_EMAIL = os.getenv("TO_EMAIL")
FROM_EMAIL = os.getenv("FROM_EMAIL")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

def send_email(subject, body, media_url=None, media_type=None):
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAIL,
        subject=subject,
        plain_text_content=body,
    )

    if media_url:
        response = requests.get(media_url, auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))

        print(f"Status: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Content length: {len(response.content)}")

        if response.status_code != 200:
            print(f"Failed to fetch media: {response.status_code}")
        else:
            file_data = response.content
            if len(file_data) < 100:
                print(f"\u26a0\ufe0f Warning: very small file size ({len(file_data)} bytes)")

            encoded_file = base64.b64encode(file_data).decode()

            filename = "attachment." + media_type.split("/")[-1]
            print(f"Attachment: {filename}")

            attachment = Attachment(
                FileContent(encoded_file),
                FileName(filename),
                FileType(media_type),
                Disposition("attachment")
            )
            message.attachment = attachment

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    print(f"SendGrid response code: {response.status_code}")
    print(f"SendGrid response body: {response.body}")

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
