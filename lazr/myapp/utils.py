from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

def send_email(user_email, amount, link):
    sender_email = os.getenv("GMAIL_ADDRESS")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    

    subject = "Receive payment"
    body = f"""
    Hello,

    You have received a payment of {amount} Sol, to claim it
    follow the link below: {link}

    Best,
    LazrPay team
    """

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = user_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
        print(f"Email sent successfully to {user_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
