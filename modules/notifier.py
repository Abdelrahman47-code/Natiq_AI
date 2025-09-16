import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Email
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))


# Save text to PDF
def create_pdf_from_text(text: str, filename: str) -> str:
    """Generate a simple PDF file from text and return the file path."""
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Write text line by line
    y = height - 40
    for line in text.split("\n"):
        c.drawString(40, y, line[:110])  # limit line width
        y -= 15
        if y < 40:  # new page if needed
            c.showPage()
            y = height - 40
    c.save()
    return filename


# Sending Functions
def send_telegram(message: str, title: str = "Output"):
    """Send text (chunked if needed) and PDF to Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return "⚠️ Telegram credentials missing."

    base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

    # --- Step 1: Send the full message in chunks ---
    chunk_size = 4000  # Telegram max ~4096
    for i in range(0, len(message), chunk_size):
        chunk = message[i:i + chunk_size]
        text_msg = f"📄 {title}\n\n{chunk}" if i == 0 else chunk
        requests.post(f"{base_url}/sendMessage", data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text_msg
        })

    # --- Step 2: Create and send PDF ---
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        create_pdf_from_text(message, tmpfile.name)
        with open(tmpfile.name, "rb") as f:
            files = {"document": f}
            response = requests.post(
                f"{base_url}/sendDocument",
                data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"📄 {title} (Full text also sent above)"},
                files=files
            )

    if response.status_code == 200:
        return "✅ Sent to Telegram with text + PDF!"
    return f"❌ Telegram Error: {response.text}"


def send_email(subject: str, message: str, recipient: str):
    """Send email with text and PDF attachment."""
    if not EMAIL_USER or not EMAIL_PASS:
        return "⚠️ Email credentials missing."

    try:
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = recipient

        # Attach plain text
        msg.attach(MIMEText(message, "plain"))

        # Attach PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            create_pdf_from_text(message, tmpfile.name)
            with open(tmpfile.name, "rb") as f:
                part = MIMEApplication(f.read(), _subtype="pdf")
                part.add_header("Content-Disposition", "attachment", filename="output.pdf")
                msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, recipient, msg.as_string())
        return "✅ Email sent with PDF!"
    except Exception as e:
        return f"❌ Email Error: {e}"


# Streamlit Share Wrapper
def share_output(session_key: str, title: str = "Output"):
    """
    Generic share UI for Telegram & Email.
    session_key: key in st.session_state where output is stored.
    title: label for the section (e.g., 'Q&A Result').
    """
    st.sidebar.title("📤 Share Results")
    send_option = st.sidebar.radio("Send output to:", ["None", "Telegram", "Email"], index=0)
    email_recipient = None
    if send_option == "Email":
        email_recipient = st.sidebar.text_input("Recipient Email")

    if session_key in st.session_state:
        output = st.session_state[session_key]

        if send_option == "Telegram":
            st.info(send_telegram(output, title))
        elif send_option == "Email" and email_recipient:
            st.info(send_email(title, output, email_recipient))
