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

def peoples_in_network_counter(network_type, zones_list):
    wolno_logger.info(f'Count peoples for {network_type}')
    result_dict = {}
    numbers_index = zones_list.index(f'Pocet_lidi_{network_type}:') + 1
    networks_names_index = zones_list.index(f'Site_{network_type}:') + 1
    numbers_result = list(map(int, list(takewhile(lambda x: x.isdigit(), zones_list[numbers_index:]))))
    index_until = len(numbers_result) + networks_names_index
    networks_names_result = list(network_name for network_name in zones_list[networks_names_index:index_until])
    result_summa = sum(numbers_result)
    final_result = dict(zip(networks_names_result, numbers_result))
    result_dict[f'{network_type}'] = final_result
    result_dict[f'{network_type}'][f'{network_type}_total'] = result_summa

    return result_dict


def main():
    URL = 'http://192.168.80.14/apcka2'

    response = requests.get(URL)
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')

        wifi_zones = {}
        total_users = 0

        for link in soup.find_all('a'):
            if (('pef' in link.get('href')) or ('cems' in link.get('href'))) and ('out' not in link.get('href')):
                if link['href']:
                    zone_name = link['href']
                    zone_response = requests.get(f'{URL}/{zone_name}')
                    if zone_response.ok:
                        wifi_zones[zone_name] = {}
                        zone_total_users = 0
                        zone_data_list = zone_response.text.split('\n')
                        if ('Pocet_lidi_5G:' and 'Site_5G:') in zone_data_list:
                            g5_result = peoples_in_network_counter(network_type='5G', zones_list=zone_data_list)
                            wifi_zones[zone_name].update(g5_result)
                            zone_total_users += wifi_zones[zone_name]['5G']['5G_total']
                        if ('Pocet_lidi_2.4G:' and 'Site_2.4G:')  in zone_data_list:
                            g2_result = peoples_in_network_counter(network_type='2.4G', zones_list=zone_data_list)
                            wifi_zones[zone_name].update(g2_result)
                            zone_total_users += wifi_zones[zone_name]['2.4G']['2.4G_total']
                        wifi_zones[zone_name].update({f'{zone_name}_total': zone_total_users})
                        total_users += zone_total_users        
                    else:
                        wolno_logger.info(f'From zone - {zone_name}, we don\'t have any data')

        DB_HOST, DB_NAME, DB_USER, DB_PASSWORD = tuple(os.environ.get(x) for x in ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD'])

        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD)

        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    '''
                        CREATE TABLE IF NOT EXISTS wifi_data_new_test (
                            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
                            ssid TEXT, 
                            eduroam_5ghz INTEGER, 
                            czu_guest_5ghz INTEGER, 
                            czu_staff_5ghz INTEGER, 
                            pef_repro_5ghz INTEGER,
                            total_5ghz INTEGER, 
                            eduroam_2_4ghz INTEGER, 
                            czu_guest_2_4ghz INTEGER, 
                            czu_staff_2_4ghz INTEGER, 
                            pef_repro_2_4ghz INTEGER,
                            total_2_4_ghz INTEGER, 
                            total_users INTEGER, 
                            timemark TIMESTAMPTZ
                            )
                    '''
                )
                cursor.execute(
                    '''
                        CREATE TABLE IF NOT EXISTS wifi_users_new_test (
                            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
                            connUsers INTEGER, 
                            timemark TIMESTAMPTZ, 
                            sectorId INTEGER
                            )
                    '''
                )

                for z_name, zone_data in wifi_zones.items():
                    # get actual date and time
                    actual_date_time_zone = ((pytz.utc.localize(datetime.datetime.utcnow())).astimezone(pytz.timezone("Europe/Prague"))).strftime('%Y-%m-%d %H:%M:%S%z')
                    cursor.execute(
                        '''
                            INSERT INTO wifi_data_new_test (
                                ssid, 
                                eduroam_5ghz, 
                                czu_guest_5ghz, 
                                czu_staff_5ghz, 
                                pef_repro_5ghz,
                                total_5ghz, 
                                eduroam_2_4ghz, 
                                czu_guest_2_4ghz, 
                                czu_staff_2_4ghz, 
                                pef_repro_2_4ghz,
                                total_2_4_ghz, 
                                total_users, 
                                timemark
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''',
                        (
                            z_name,
                            zone_data['5G'].get('eduroam'),
                            zone_data['5G'].get('CZU-guest'),
                            zone_data['5G'].get('CZU-staff'),
                            zone_data['5G'].get('PEF-repro'),
                            zone_data['5G'].get('5G_total'),
                            zone_data['2.4G'].get('eduroam'),
                            zone_data['2.4G'].get('CZU-guest'),
                            zone_data['2.4G'].get('CZU-staff'),
                            zone_data['2.4G'].get('PEF-repro'),
                            zone_data['2.4G'].get('2.4G_total'),
                            zone_data.get(f'{z_name}_total'),
                            actual_date_time_zone
                        )
                    )           
    else:
        wolno_logger.info('Bad request')

if __name__ == '__main__':
    main()