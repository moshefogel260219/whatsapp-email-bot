
from flask import Flask, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

TO_EMAIL = os.getenv("TO_EMAIL")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")

def send_email(subject, body, attachment_url=None, attachment_filename=None):
    data = {
        "from": f"WhatsApp Bot <bot@{MAILGUN_DOMAIN}>",
        "to": [TO_EMAIL],
        "subject": subject,
        "text": body
    }

    files = None
    if attachment_url and attachment_filename:
        # Download the media
        file_response = requests.get(attachment_url)
        if file_response.status_code == 200:
            files = [("attachment", (attachment_filename, file_response.content))]

    return requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data=data,
        files=files
    )

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    sender = request.form.get("From", "")
    message = request.form.get("Body", "")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    num_media = int(request.form.get("NumMedia", "0"))
    attachment_url = None
    attachment_filename = None

    if num_media > 0:
        attachment_url = request.form.get("MediaUrl0")
        attachment_filename = request.form.get("MediaContentType0", "file").split("/")[-1]
        if not attachment_filename:
            attachment_filename = "attachment"

    subject = f"New WhatsApp Message from {sender}"
    body = f"Time: {timestamp}\nFrom: {sender}\nMessage: {message}"

    send_email(subject, body, attachment_url, attachment_filename)

    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)
