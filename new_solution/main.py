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

def peoples_in_network_counter(name, network_type, zones_list):
    numbers_index = zones_list.index(f'Pocet_lidi_{network_type}:') + 1
    networks_names_index = zones_list.index(f'Site_{network_type}:') + 1
    numbers_result = list(map(int, list(takewhile(lambda x: x.isdigit(), zones_list[numbers_index:]))))

    index_until = len(numbers_result) + networks_names_index

    networks_names_result = list(network_name for network_name in zones_list[networks_names_index:index_until])
    result_summa = sum(numbers_result)
    final_result = dict(zip(networks_names_result, numbers_result))
    wifi_zones[name][f'{network_type}'] = final_result
    wifi_zones[name][f'{network_type}'][f'{network_type}_total'] = result_summa

URL = 'http://192.168.80.14/apcka2'

response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

zones = []
wifi_zones = {}
counter = 0

for link in soup.find_all('a'):
    if (('pef' in link.get('href')) or ('cems' in link.get('href'))) and ('out' not in link.get('href')):
        if link['href']:
            counter += 1
            zone_name = link['href']
            zone_response = requests.get(f'{URL}/{zone_name}')
            if zone_response.ok:
                wifi_zones[zone_name] = {}
                list_test = zone_response.text.split('\n')
                if ('Pocet_lidi_5G:' and 'Site_5G:') in list_test:
                    peoples_in_network_counter(name=zone_name, network_type='5G', zones_list=list_test)
                if ('Pocet_lidi_2.4G:' and 'Site_2.4G:')  in list_test:
                    peoples_in_network_counter(name=zone_name, network_type='2.4G', zones_list=list_test)     
            else:
                wolno_logger.info(f'From zone - {zone_name}, we don\'t have any data')

                
from pprint import pprint
print(counter)
pprint(wifi_zones)
print(len(wifi_zones))

# DB_HOST, DB_NAME, DB_USER, DB_PASSWORD = tuple(os.environ.get(x) for x in ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD'])

# conn = psycopg2.connect(
#     host=DB_HOST,
#     database=DB_NAME,
#     user=DB_USER,
#     password=DB_PASSWORD)

# get actual date and time
# actual_date_time_zone = ((pytz.utc.localize(datetime.datetime.utcnow())).astimezone(pytz.timezone("Europe/Prague"))).strftime('%Y-%m-%d %H:%M:%S%z')

# '''
# CREATE TABLE wifi_data_test (id BIGINT PRIMARY KEY AUTOINCREMENT, ssid TEXT, eduroam_5ghz INTEGER, czu_guest_5ghz INTEGER, czu_staff_5ghz INTEGER, pef_repro_5ghz INTEGER, eduroam_2_4ghz INTEGER, czu_guest_2_4ghz INTEGER, czu_staff_2_4ghz INTEGER, pef_repro_2_4ghz INTEGER, total_networks INTEGER, timemark TIMESTAMPTZ)
# '''

# '''
# CREATE TABLE wifi_users_test (id BIGINT PRIMARY KEY AUTOINCREMENT, connUsers INTEGER, timemark TIMESTAMPTZ, sectorId INTEGER
# '''
