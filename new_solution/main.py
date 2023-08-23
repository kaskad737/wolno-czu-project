import requests
from bs4 import BeautifulSoup

URL = 'http://192.168.80.14/apcka2'

response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

for link in soup.find_all('a'):
    print(link.text)