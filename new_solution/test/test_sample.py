import sys
sys.path.append('/home/archakov/university_projects/new_solution/')
from main import peoples_in_network_counter


def test_peoples_in_network_counter():
    MOCK_DATA = ['cems1-1-167', '39 days', '515', 'Site_5G:', 'eduroam', 'CZU-guest', 'CZU-staff', 'Site_2.4G:', 'eduroam', 'CZU-guest', 'CZU-staff', 'Pocet_lidi_5G:', '2', '0', '0', 'Pocet_lidi_2.4G:', '0', '0', '0', 'data z controlleru: ', 'vytvoreni souboru pro dane ap: 23.08.23-16:31:24', '']
    result = peoples_in_network_counter(network_type='5G', zones_list=MOCK_DATA)
    assert result['5G']['5G_total'] == 2
    assert result['5G']['eduroam'] == 2
    assert result['5G']['CZU-guest'] == 0

def test_peoples_in_network_counter_fail():
    MOCK_DATA = ['cems1-1-167', '39 days', '515', 'Site_5G:', 'eduroam', 'CZU-guest', 'CZU-staff', 'Site_2.4G:', 'eduroam', 'CZU-guest', 'CZU-staff', 'Pocet_lidi_5G:', '2', '0', '0', 'Pocet_lidi_2.4G:', '0', '0', '0', 'data z controlleru: ', 'vytvoreni souboru pro dane ap: 23.08.23-16:31:24', '']
    result = peoples_in_network_counter(network_type='5G', zones_list=MOCK_DATA)
    assert result['5G']['5G_total'] != 3

