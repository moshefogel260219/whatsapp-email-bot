
📦 WhatsApp לבוט עם תמיכה ב-SendGrid:

1. התקן ספריות:
pip install -r requirements.txt

2. צור קובץ .env בתיקייה והדבק בו את:
TO_EMAIL=moshfog@gmail.com
FROM_EMAIL=moshfog@gmail.com
SENDGRID_API_KEY=המפתח שלך מ-SendGrid

3. הרץ את הבוט:
python app.py

4. חבר את Twilio לכתובת:
http://<כתובת השרת>/whatsapp

5. שלח הודעה או תמונה לוואטסאפ → תגיע למייל!

🎯 עובד גם עם טקסט וגם עם מדיה (תמונה/וידאו)
