from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os

# Load variables from .env
load_dotenv()

def send_email(user_email):
    sender_email = os.getenv("GMAIL_ADDRESS")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    subject = "Welcome to Our App!"
    body = f"""
    Hello,

    Thank you for signing up! We're excited to have you on board.

    Best,
    
    LazrPay team
    """

    # Create MIME email
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
    except Exception as e:
        print(f"Failed to send email: {e}")

# Example usage
if __name__ == "__main__":
    recipient = input("Enter recipient's email: ")
    send_email(recipient)