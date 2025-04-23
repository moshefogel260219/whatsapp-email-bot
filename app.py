from flask import Flask, request
import os, base64, requests, logging
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ----- ENV -----
TO_EMAIL          = os.getenv("TO_EMAIL")
FROM_EMAIL        = os.getenv("FROM_EMAIL")
SENDGRID_API_KEY  = os.getenv("SENDGRID_API_KEY")
TWILIO_ACCOUNT_SID= os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# --------------------------------------------------
def fetch_twilio_media(url: str) -> tuple[bytes,str]:
    """מחזיר (bytes, mime-type) או (b'', '') במקרה כישלון"""
    r = requests.get(url, auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), timeout=15)
    logging.info("Twilio media GET %s -> %s", url, r.status_code)
    if r.status_code != 200:
        return b'', ''
    mime = r.headers.get("Content-Type", "")
    return r.content, mime

def send_email(subject, body, file_bytes=b'', file_mime=''):
    msg = Mail(from_email=FROM_EMAIL, to_emails=TO_EMAIL,
               subject=subject, plain_text_content=body)

    # רק אם באמת יש קובץ ושוקל >0
    if file_bytes:
        logging.info("Attachment size: %d bytes  mime=%s", len(file_bytes), file_mime)
        enc = base64.b64encode(file_bytes).decode()
        fname = "attachment." + (file_mime.split("/")[-1] or "bin")
        msg.attachment = Attachment(FileContent(enc),
                                    FileName(fname),
                                    FileType(file_mime or "application/octet-stream"),
                                    Disposition("attachment"))
    else:
        logging.warning("No attachment added")

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    resp = sg.send(msg)
    logging.info("SendGrid response %s", resp.status_code)

# --------------------------------------------------
@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    logging.info("----New webhook-----")
    media_cnt = int(request.form.get("NumMedia", "0"))
    sender    = request.form.get("From", "")
    body_txt  = request.form.get("Body", "")
    ts        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    media_bytes = b''
    media_mime  = ''

    if media_cnt > 0:
        url0  = request.form.get("MediaUrl0")
        mime0 = request.form.get("MediaContentType0", "")
        logging.info("NumMedia=%s  url=%s  mime=%s", media_cnt, url0, mime0)
        media_bytes, media_mime = fetch_twilio_media(url0)
        # אם Twilio לא החזיר Mime ניקח מה־form
        if not media_mime:
            media_mime = mime0

    subject = f"New WhatsApp Message from {sender}"
    body    = f"Time: {ts}\nFrom: {sender}\nMessage: {body_txt}"
    send_email(subject, body, media_bytes, media_mime)
    return "OK", 200

# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
