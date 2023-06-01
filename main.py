import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
import random
from requestium import Session, Keys

# Set the URL and headers
url = "https://www.example.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

proxy_list = [
    
]

# Session nesnesi oluşturma
session = Session(webdriver_path='./chromedriver')

# Proxy rotasyonunu etkinleştirme
session.driver.command_executor._commands["DELETE_SESSION"] = ("DELETE", '/session/$sessionId')
session.driver.execute("CREATE_SESSION", {"sessionId": "session_id", "capabilities": {}, "parameters": {"proxy": {"proxyType": "manual", "httpProxy": "", "sslProxy": "", "socksProxy": "", "ftpProxy": ""}}})
session.driver.execute_script("mobileEmulation = { userAgent: 'Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36' };")
session.driver.execute_script("Object.defineProperty(navigator, 'userAgent', { get: function () { return mobileEmulation.userAgent; } });")

# Proxy rotasyonunu kullanarak 10 istek atma
for i in range(10):
    proxy = proxy_list[i % len(proxy_list)]
    session.driver.execute_script("mobileEmulation = { userAgent: 'Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36' };")
    session.driver.execute_script("Object.defineProperty(navigator, 'userAgent', { get: function () { return mobileEmulation.userAgent; } });")
    session.driver.execute_script("chrome.proxy.settings.set({value: {mode: 'fixed_servers', rules: {singleProxy: {scheme: 'http', host: '%s', port: %s}}}, scope: 'regular'}, function(){});" % (proxy.split(':')[0], proxy.split(':')[1]))
    session.driver.get(url)
# Set up logging
logging.basicConfig(filename="scraper.log", level=logging.ERROR)

# Create a session and send the initial request
session = requests.Session()
try:
    response = session.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception if the response is not OK
    soup = BeautifulSoup(response.text, "html.parser")
except Exception as e:
    logging.error(f"Error on initial request: {e}")
    raise

# Check if a CAPTCHA is required
if "captcha" in response.text:
    # Solve the CAPTCHA
    solver = CaptchaSolver("captcha_service_api_key")
    captcha_url = soup.find("img", class_="captcha-image").get("src")
    captcha_text = solver.solve_captcha(captcha_url)
    # Add the CAPTCHA solution to the form data
    form_data["captcha"] = captcha_text

# CAPTCHA var mı kontrol et
captcha_img = soup.find("img", {"class": "captcha-image"})
if captcha_img:
    # CAPTCHA varsa, görüntüyü indir ve çöz
    captcha_url = captcha_img["src"]
    captcha_response = requests.get(captcha_url, stream=True)
    captcha_image = Image.open(captcha_response.raw)
    captcha_text = pytesseract.image_to_string(captcha_image)
    # Çözülen CAPTCHA metnini form verilerine ekleyin
    form_data["captcha"] = captcha_text.strip()
# Find the total number of pages
try:
    total_pages = int(soup.find("span", class_="total-pages").text)
except Exception as e:
    logging.error(f"Error finding total pages: {e}")
    raise

# Loop through all pages and extract the data
data = []
for page in range(1, total_pages + 1):
    try:
        # Send the request for the current page
        params = {"page": page}
        response = session.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception if the response is not OK
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract the data from the current page
        for person in soup.find_all("div", class_="person"):
            email = person.find("a", class_="email").text.strip()
            name = person.find("span", class_="name").text.strip()
            surname = person.find("span", class_="surname").text.strip()
            company = person.find("span", class_="company").text.strip()
            data.append([email, name, surname, company])
            time.sleep(random.uniform(1, 5))
    except Exception as e:
        logging.error(f"Error on page {page}: {e}")
        continue

# Save the data as a CSV file
try:
    with open("data.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Email", "Name", "Surname", "Company"])
        writer.writerows(data)
except Exception as e:
    logging.error(f"Error saving data to CSV: {e}")
    raise
