from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from django.template.loader import render_to_string
load_dotenv()
# this sends an email to user
def send_email(user_email):
    sender_email = os.getenv("GMAIL_ADDRESS")
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    if not sender_email or not app_password:
        return
    subject = "You've received crypto on LazrPay!"
    try:
        html_content = render_to_string("email.html")
    except FileNotFoundError:
        return
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = user_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
    except Exception:
        pass
