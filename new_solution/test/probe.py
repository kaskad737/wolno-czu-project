for link in soup.find_all('a'):
    if (('pef' in link.get('href')) or ('cems' in link.get('href'))) and ('out' not in link.get(
                'href')):
        if link['href']:
            zone_name = link['href']
            zone_response = requests.get(f'{URL}/{zone_name}')

            ############################################3

            list_test = zone_response.text.split('\n')
            test_length = len(zone_response.text.split('\n'))
            # good point to write test:
            # ['cems1-1-167', '39 days', '515', 'Site_5G:', 'eduroam', 'CZU-guest', 'CZU-staff', 'Site_2.4G:', 'eduroam', 'CZU-guest', 'CZU-staff', 'Pocet_lidi_5G:', '2', '0', '0', 'Pocet_lidi_2.4G:', '0', '0', '0', 'data z controlleru: ', 'vytvoreni souboru pro dane ap: 23.08.23-16:31:24', '']
            # change quantity of users OR change quantity of 2.4G OR 5G networks 
            # example: ['cems1-1-167', '39 days', '515', 'Site_5G:', 'eduroam', 'CZU-guest', 'CZU-staff', 'Site_2.4G:', 'eduroam', 'CZU-guest', 'CZU-staff', 'Pocet_lidi_5G:', '2', '0', 'Pocet_lidi_2.4G:', '0', '0', 'data z controlleru: ', 'vytvoreni souboru pro dane ap: 23.08.23-16:31:24', '']
            # example: ['cems1-1-167', '39 days', '515', 'Site_5G:', 'eduroam', 'CZU-guest', 'CZU-staff', 'Site_2.4G:', 'eduroam', 'CZU-guest', 'CZU-staff', 'Pocet_lidi_5G:', '2', '2', '3', 'Pocet_lidi_2.4G:', '0', '0', 'data z controlleru: ', 'vytvoreni souboru pro dane ap: 23.08.23-16:31:24', '']
            # list_test = ['cems1-1-167', '39 days', '515', 'Site_5G:', 'eduroam', 'CZU-guest', 'CZU-staff', 'Site_2.4G:', 'eduroam', 'CZU-guest', 'CZU-staff', 'Pocet_lidi_5G:', '2', '2', '3', 'Pocet_lidi_2.4G:', '0', '0', 'data z controlleru: ', 'vytvoreni souboru pro dane ap: 23.08.23-16:31:24', '']
            # test_length = len(list_test)
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