import streamlit as st
import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from PIL import Image

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(page_title="NCP WhatsApp Automation", page_icon="💬", layout="wide")

# ----------------------------
# Load .env Email Config
# ----------------------------
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

# ----------------------------
# CSS for Scrollable Message Log
# ----------------------------
st.markdown("""
<style>
.scrollbox {
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #ddd;
    padding: 1em;
    background-color: #f9f9f9;
    border-radius: 8px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Email Sending Function
# ----------------------------
def send_email(recipient, message_text):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient
        msg['Subject'] = "Fallback: WhatsApp Message"
        msg.attach(MIMEText(message_text.replace('%0A', '\n'), 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return f"❌ Email to {recipient} failed: {e}"

# ----------------------------
# WhatsApp + Email Logic
# ----------------------------
def send_messages(dataframe, message_text, log_box):
    options = webdriver.ChromeOptions()
    # options.add_argument("--user-data-dir=./User_Data")  # Keep login session
    # options.add_argument("--headless")  # Classic headless (Windows safe)
    options.add_argument("--headless-chrome")  # Classic headless (Windows safe)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # options.add_argument("--disable-gpu")  # Don't use on Windows
    # options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # Optional

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://web.whatsapp.com/")
    log_box.markdown("🔵 <b>Please scan the QR code if required. Waiting 20 seconds...</b>", unsafe_allow_html=True)

    wait = WebDriverWait(driver, 20)
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "canvas")))
    except:
        pass
    time.sleep(20)

    failed_records = []
    log_content = ""

    for idx, row in dataframe.iterrows():
        number = row['Phone']
        email = row.get('Email', '')

        log_content += f"📤 Sending to {number}...<br>"
        url = f"https://web.whatsapp.com/send?phone={number}&text={message_text}"
        driver.get(url)
        time.sleep(7)

        try:
            send_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Send']")))
            send_button.click()
            log_content += f"✅ WhatsApp sent to {number}<br>"
        except Exception:
            log_content += f"⚠️ WhatsApp failed for {number}. Trying email...<br>"
            result = send_email(email, message_text)
            if result is True:
                log_content += f"✉️ Email sent to {email}<br>"
            else:
                log_content += f"{result}<br>"
                failed_records.append({"Phone": number, "Email": email})

        log_box.markdown(f"<div class='scrollbox'>{log_content}</div>", unsafe_allow_html=True)
        time.sleep(random.uniform(4, 6))

    driver.quit()
    return failed_records

# ----------------------------
# UI Layout
# ----------------------------
col_left, col_right = st.columns([1, 2])

with col_left:
    logo = Image.open("NCPDA.png")
    st.image(logo, use_container_width=True)
    st.markdown("<h2 style='color: #d62828;'>NCP Automation</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #444;'>WhatsApp/Email sending tool</p>", unsafe_allow_html=True)

with col_right:
    st.markdown("### 📥 Upload Excel File")
    st.write("Make sure it contains **Phone** and **Email** columns.")
    uploaded_file = st.file_uploader("", type=["xlsx"])

    st.markdown("### 💬 Message to Send")
    user_message = st.text_area(
        "Type your message here (use new lines for formatting):",
        value=(
            "Dear NCP Members,\n"
            "ধন্যবাদান্তে,\n"
            "........\n"
            "NCPDA Member Europe"
        ),
        height=200
    )

    message = user_message.replace("\n", "%0A")

    send_btn = st.button("🚀 Send WhatsApp Messages")

# ----------------------------
# Action Handler
# ----------------------------
if send_btn and uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        if "Phone" not in df.columns:
            st.error("❗ The Excel file must have a column named `Phone`.")
        else:
            df["Phone"] = df["Phone"].astype(str).str.replace(r"[^\d+]", "", regex=True)
            df["Phone"] = ["+" + num if not num.startswith("+") else num for num in df["Phone"]]

            with col_right:
                st.markdown("### 📬 Message Log")
                log_box = st.empty()
                failed = send_messages(df, message, log_box)

                if failed:
                    failed_df = pd.DataFrame(failed)
                    st.warning(f"⚠️ Failed to send to {len(failed)} contact(s).")
                    st.dataframe(failed_df)

                    output = BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        failed_df.to_excel(writer, index=False, sheet_name="Failed")

                    st.download_button(
                        label="📥 Download Failed List",
                        data=output.getvalue(),
                        file_name="failed_fallback.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.success("🎉 All messages sent via WhatsApp or email!")

    except Exception as e:
        st.error(f"❌ Error: {e}")

# ----------------------------
# Footer
# ----------------------------
st.markdown(
    """
    <hr style="margin-top: 50px;">
    <div style="text-align: center; font-size: 0.9em; color: gray;">
        Created by <strong>NCP Diaspora Alliance Europe IT</strong>
    </div>
    """,
    unsafe_allow_html=True
)
