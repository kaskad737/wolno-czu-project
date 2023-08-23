import requests
from bs4 import BeautifulSoup
import psycopg2
import logging
import logging.config
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

            list_test = zone_response.text.split('\n')
            test_length = len(zone_response.text.split('\n'))
            print(list_test)
            if 'Pocet_lidi_5G:' in list_test:
                g5_index = list_test.index('Pocet_lidi_5G:')
                g5_result = list(takewhile(lambda x: x.isdigit(), list_test[g5_index + 1:]))
                print(g5_result)
            if 'Pocet_lidi_2.4G:' in list_test:
                g2_index = list_test.index('Pocet_lidi_2.4G:')
                g2_result = list(takewhile(lambda x: x.isdigit(), list_test[g2_index + 1:]))
                print(g2_result)
            break
    
            # wifi_zones[zone_name] = {'2.4G': g2, '5G': g5}




# for name in zones:
#         if name:
#             counter_ap += 1
#         response = http.request('GET', f'http://192.168.80.14/apcka2/{name}')
#         html = response.data.decode('utf8')
#         networks_counts = list(chain(x.split('\n')[1:-1] for x in html.split(':')[1:5]))
#         g2, g5 = tuple(dict(zip(networks_counts[x], networks_counts[y])) for x, y in [
#             (1, 3),
#             (0, 2),
#         ])