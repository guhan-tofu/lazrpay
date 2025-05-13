from dotenv import load_dotenv
import os

load_dotenv()

sender_email = os.getenv("GMAIL_ADDRESS")


print(sender_email)
print("12212")

