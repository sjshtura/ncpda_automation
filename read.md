✅ 1. ChromeDriver Setup
🖥️ For macOS
🛠 Option 1: Using webdriver-manager (Already in your code)
No manual installation needed. Just run:

pip install webdriver-manager
Your code will automatically:

Detect your Chrome version.

Download the correct chromedriver.

Store it in: ~/.wdm/drivers/

🔍 If you want to check Chrome version:
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
🧪 Test:
python your_script.py
🖥️ For Windows
🛠 Also uses webdriver-manager:
No manual setup is needed.

But you must have Google Chrome installed (not Chromium).

⚠️ Optional manual test:
To check Chrome version:

Open Chrome.

Go to: chrome://settings/help

Copy the version, e.g., 114.0.5735.90

Then manually download ChromeDriver if needed:

https://googlechromelabs.github.io/chrome-for-testing/

Extract the executable and place it in your PATH (e.g., C:\WebDriver\bin) and adjust script like:

driver = webdriver.Chrome(executable_path='C:/WebDriver/bin/chromedriver.exe')
But again, your current script with ChromeDriverManager().install() works automatically on both OS.

✅ 2. .env File for Gmail or Other SMTP
Create a file named .env in the same directory as your script, with the following content:

# Example for Gmail
EMAIL_ADDRESS=ncpdiasporaalliance@gmail.com
EMAIL_PASSWORD=your_app_specific_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
⚠️ For Gmail:

If 2FA is enabled (recommended), create an App Password.

Paste that password as EMAIL_PASSWORD.

🧪 How to test .env loading:
from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv("EMAIL_ADDRESS"))
If it prints your email — it’s working.