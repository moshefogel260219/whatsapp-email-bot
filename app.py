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
    print("------ Full request.form ------")
    for key in request.form:
        print(f"{key} => {request.form[key]}")
    print("------------------------------")
    print(f"Content length: {len(request.form)} bytes")

    print("=========== NEW WHATSAPP MESSAGE ===========")
    print(f"NumMedia: {request.form.get('NumMedia')}")
    print(f"MediaUrl0: {request.form.get('MediaUrl0')}")
    print(f"MediaContentType0: {request.form.get('MediaContentType0')}")

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

if __name__ == "__main__":
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
    import requests
    import base64
    import os

    # פרטי הסביבה
    TO_EMAIL = os.getenv("TO_EMAIL")
    FROM_EMAIL = os.getenv("FROM_EMAIL")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

    # פרטי הקובץ לבדיקה
    image_url = "https://upload.wikimedia.org/wikipedia/commons/9/9a/Gull_portrait_ca_usa.jpg"
    media_type = "image/jpeg"

    # שליחה
    def send_test_email_with_image():
        response = requests.get(image_url)
        encoded_file = base64.b64encode(response.content).decode()

        attachment = Attachment(
            FileContent(encoded_file),
            FileName("test_image.jpg"),
            FileType(media_type),
            Disposition("attachment")
        )

        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=TO_EMAIL,
            subject="📸 Test Image from Script",
            plain_text_content="This is a test email with image attachment."
        )
        message.attachment = attachment

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        print("✅ Test email sent!")

    send_test_email_with_image()
