import os
import datetime
import pytz
import psycopg2
import requests
import logging
import logging.config
from bs4 import BeautifulSoup
from logging_config import dict_config
from itertools import takewhile

logging.config.dictConfig(dict_config)
wolno_logger: logging.Logger = logging.getLogger('wolnoLogger')

URL = 'http://192.168.80.14/apcka2'

response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

zones = []
wifi_zones = {}

for link in soup.find_all('a'):
    if (('pef' in link.get('href')) or ('cems' in link.get('href'))) and ('out' not in link.get(
                'href')):
        if link['href']:
            zone_name = link['href']
            zone_response = requests.get(f'{URL}/{zone_name}')

            if zone_response.ok:

                list_test = zone_response.text.split('\n')
                test_length = len(zone_response.text.split('\n'))
                print(list_test)
                if 'Pocet_lidi_5G:' in list_test:
                    g5_index = list_test.index('Pocet_lidi_5G:')
                    g5_result = map(list(takewhile(lambda x: x.isdigit(), list_test[g5_index + 1:])), int)
                if 'Pocet_lidi_2.4G:' in list_test:
                    g2_index = list_test.index('Pocet_lidi_2.4G:')
                    g2_result = map(list(takewhile(lambda x: x.isdigit(), list_test[g2_index + 1:])), int)
        
                wifi_zones[zone_name] = {'2.4G': g2_result, '5G': g5_result}
            
            else:
                wolno_logger.info(f'From zone - {zone_name}, we don\'t have any data')


DB_HOST, DB_NAME, DB_USER, DB_PASSWORD = tuple(os.environ.get(x) for x in ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD'])

conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD)

# get actual date and time
actual_date_time_zone = ((pytz.utc.localize(datetime.datetime.utcnow())).astimezone(pytz.timezone("Europe/Prague"))).strftime('%Y-%m-%d %H:%M:%S%z')

