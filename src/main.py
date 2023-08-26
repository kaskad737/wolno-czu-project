import os
import sys
import datetime
import pytz
import psycopg2
import requests
import argparse
import logging
import logging.config
from bs4 import BeautifulSoup
from logging_config import dict_config
from itertools import takewhile
from ap_zones import ap_zones

logging.config.dictConfig(dict_config)
wolno_logger: logging.Logger = logging.getLogger('wolnoLogger')

def peoples_in_network_counter(network_type, zones_list):
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
        wolno_logger.info(f'Request to {URL} is ok')
        soup = BeautifulSoup(response.text, 'html.parser')

        wifi_zones = {}
        total_users = 0

        for link in soup.find_all('a'):
            if (('pef' in link.get('href')) or ('cems' in link.get('href'))) and ('out' not in link.get('href')):
                if link['href']:
                    zone_name = link['href']
                    zone_response = requests.get(f'{URL}/{zone_name}')
                    if zone_response.ok:
                        wolno_logger.info(f'Request to zone - {zone_name} is ok')
                        wifi_zones[zone_name] = {}
                        zone_total_users = 0
                        zone_data_list = zone_response.text.split('\n')
                        wolno_logger.info(f'Start counting peoples for 5G and 2.4G networks in {zone_name} zone')
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
                        wolno_logger.info(f'Counting finish ({zone_name})')     
                    else:
                        wolno_logger.error(f'Bad request. Zone - {zone_name}. We don\'t have any data')

        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD)
        wolno_logger.info(f'Connecting to DB ({DB_NAME})')
        with conn:
            with conn.cursor() as cursor:
                wolno_logger.info('Creating "wifi_data_new_test" table if not exists')
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
                wolno_logger.info('Creating "wifi_users_new_test" table if not exists')
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
                    wolno_logger.info(f'Inserting data ({z_name}) into "wifi_data_new_test" table')
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
                    # take data for each ap and sort it to zones    
                    for ap in ap_zones:
                        if z_name in ap:
                            ap[z_name] += zone_data.get(f'{z_name}_total')
                # summ data and put it in DB
                for index, ap in enumerate(ap_zones):
                    actual_date_time_zone = ((pytz.utc.localize(datetime.datetime.utcnow())).astimezone(pytz.timezone("Europe/Prague"))).strftime('%Y-%m-%d %H:%M:%S%z')
                    sum_of_users_in_zone = sum(ap.values())  
                    wolno_logger.info(f'Inserting data (Zone number - {index + 1}) into "wifi_users_new_test" table')
                    cursor.execute(
                        '''
                            INSERT INTO wifi_users_new_test (
                                connUsers, 
                                timemark, 
                                sectorId
                            ) VALUES (%s, %s, %s)
                        ''',
                        (
                            sum_of_users_in_zone,
                            actual_date_time_zone,
                            index + 1
                        )
                    )
        wolno_logger.info('Parsing was successful')
        sys.exit(0)
    else:
        wolno_logger.error(f'Bad initial request to {URL}')
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Arguments for DB')
    parser.add_argument('-dh', '--db_host', type=str, help='Host of database', required=True)
    parser.add_argument('-n', '--db_name', type=str, help='Name of database', required=True)
    parser.add_argument('-u', '--db_user', type=str, help='Database user', required=True)
    parser.add_argument('-p', '--db_password', type=str, help='Database password', required=True)
    args = parser.parse_args()
    DB_HOST = args.dh
    DB_NAME = args.n
    DB_USER = args.u
    DB_PASSWORD = args.p
    main()