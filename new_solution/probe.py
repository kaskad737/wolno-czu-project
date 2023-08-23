import bs4 as bs
import urllib3
import os
import datetime as d
import pytz
import logging
from itertools import chain

counter_ap = 0
zones = []
wifi_zones = {}

http = urllib3.PoolManager(num_pools=1)
# we make initial request to main page
response = http.request('GET', 'http://192.168.80.14/apcka2')
html = response.data.decode('utf8')
soup = bs.BeautifulSoup(html, 'html.parser')
# when we getting names of all zones
for link in soup.find_all('a'):
    if (('pef' in link.get('href')) or ('cems' in link.get('href'))) and ('out' not in link.get(
            'href')):  # Checking if AP's whitch we need is in building PEF (pef, cems) and adding to list of names of APs
        zones.append(link.get('href'))
# when we make requests using name of zones to get data for each zone
for name in zones:
    if name:
        counter_ap += 1
    response = http.request('GET', f'http://192.168.80.14/apcka2/{name}')
    html = response.data.decode('utf8')
    networks_counts = list(chain(x.split('\n')[1:-1] for x in html.split(':')[1:5]))
    g2, g5 = tuple(dict(zip(networks_counts[x], networks_counts[y])) for x, y in [
        (1, 3),
        (0, 2),
    ])

    wifi_zones[name] = {'2.4G': g2, '5G': g5}

print(wifi_zones)