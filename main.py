import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
import random
from requestium import Session, Keys


def get_cookie_count():
    url = "https://example.com"  # Scraping yapmak istediğiniz web sitesinin URL'sini buraya girin
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Web sayfasında cookie sayısını içeren bir HTML elementini bulun
    cookie_element = soup.find("span", id="cookie_count")  # Örnek olarak, "cookie_count" ID'sine sahip bir <span> elementini arıyoruz

    if cookie_element:
        cookie_count = int(cookie_element.text)
        return cookie_count
    else:
        print("Cookie count element not found on the page.")
        return None

# Cookie sayısını get_cookie_count() fonksiyonunu kullanarak alalım
cookie_count = get_cookie_count()
if cookie_count:
    print("Cookie Count:", cookie_count)

# Set the URL and headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

proxy_list = [
    # Proxy listesi buraya eklenecek
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

# Fonksiyon: URL oluşturma
def generate_url(domain, extension):
    url = f"https://www.example.{domain}.{extension}"
    return url

# Fonksiyon: Tüm siteleri tara
def scrape_all_sites():
    data = []
    extensions = ["com", "org", "xyz"]
    for domain_length in range(3, 16):
        domain_list = generate_domain_list(domain_length)
        for domain in domain_list:
            for extension in extensions:
                url = generate_url(domain, extension)
                try:
                    response = session.get(url, headers=headers)
                    response.raise_for_status()  # Raise an exception if the response is not OK
                    soup = BeautifulSoup(response.text, "html.parser")
                    # Extract the data from the current page
                    for person in soup.find_all("div", class_="person"):
                        email = person.find("a", class_="email").text.strip()
                        name = person.find("span", class_="name").text.strip()
                        surname = person.find("span", class_="surname").text.strip()
                        company = person.find("span", class_="company").text.strip()
                        phone = person.find("span", class_="phone").text.strip()
                        data.append([email, name, surname, company])
                        time.sleep(random.uniform(1, 5))
                except Exception as e:
                    logging.error(f"Error on URL: {url}\n{e}")
                    continue
    return data

# Fonksiyon: Tüm olası domainleri üretme
def generate_domain_list(length):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    domains = [""]
    for i in range(length):
        new_domains = []
        for domain in domains:
            for char in chars:
                new_domains.append(domain + char)
        domains = new_domains
    return domains

# Ana işlem
try:
    data = scrape_all_sites()
except Exception as e:
    logging.error(f"Error during scraping: {e}")
    raise

# Save the data as a CSV file
try:
    with open("data.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Email", "Name", "Surname", "Company"])
        writer.writerows(data)
except Exception as e:
    logging.error(f"Error saving data to CSV: {e}")
    raise
