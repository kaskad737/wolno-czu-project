# ČZU Wolno Application WiFi Parser Script

![wolno_logo.png](http://ls40.pef.czu.cz/files/wolno_logo.png)

---
## Content
1. [Introduction](#intro)
2. [Structure description](#structdesc)
3. [How the script works](#howworks)
4. [Database SQL Tables](#DB)
5. [Map of Zones](#zones)


---

## <a id='intro'>Introduction</a>
The purpose of this script is to parse data from WiFi access points, then process them and save them to the database
__[More info about Wolno application](http://ls40.pef.czu.cz/obsazenost-arealu-czu)__


---
## <a id='structdesc'>Structure description</a>

File ```wifi_parser.py``` сontains actually script for parsing data from WiFi acces points and saves it to database

File ```ap_zones.py``` is file for mapping (static mapping) existing acces points to zones we have on map (see images). One zone can include one or more acces points. ID of zones depend on the zone index in the zone list.


##### When creating the script, the following modules were used:
```
beautifulsoup4==4.9.3
urllib3==1.26.4
SQLAlchemy==1.4.5
SQLAlchemy-Utils==0.36.8
pytz==2021.1
```
and dependencies that come with them.
___

## <a id='howworks'>How the script works</a>

```python
counter_ap = 0
    zones = []
    wifi_zones = {}

    http = urllib3.PoolManager(num_pools=1)
    # we make initial request to main page
    response = http.request('GET', 'http://192.168.80.14/apcka2')
    html = response.data.decode('utf8')
    soup = bs.BeautifulSoup(html, 'html.parser')
    # when we getting names of all zones
```
We define variables for parsing and additional variables for working and sorting data. 

___

```python
for link in soup.find_all('a'):
        if (('pef' in link.get('href')) or ('cems' in link.get('href'))) and ('out' not in link.get(
                'href')):  # Checking if AP's whitch we need is in building PEF (pef, cems) and adding to list of names of APs
            zones.append(link.get('href'))
```

Here we finding all `<a>` tags and with `if` condition we get all acces points we have on PEF (`'pef'`, `'cems'`), then we adding it to our zones list. This is how we get names of acces points. 

___

Then, using acces points names, we can make a request to a specific acces point and get this tamplate of data:

```
API response structure:
AP_Name (Hostname)
AP_Uptime 
AP_Model
Networks_5G: (str, const)
A
B
C
Networks_2.4G: (str, const)
A
B
C
Pocet_lidi_5G: (str, const)
network_A
network_B
network_C
Pocet_lidi_2.4G: (str, const)
network_A
network_B
network_C
data z controlleru (str, const)
vytvoreni souboru pro dane ap creating: (str, const) timestamp (datetime)
```


I would like to dwell especially on this piece of code and explain it in more detail
```python
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
```
First, when we make http request and get data and decode it to html, we take specific html we get before and get lists of names of 5G and 2.4G networks, and lists with specific integers (which means users).

Second, we take these lists with network names and integers and make dicts by connecting specific names with specific integers.

___

## <a id='DB'>Database SQL Tables</a>

Data is saved in two tables (`wifi_data`, `wifi_users`) __Name of Tables is subject to change.__
In table `wifi_data` we save all data. And in table `wifi_users` we save the data that we have previously sorted into specific zones with specific ID by `ap_zones.py`

___

## <a id='zones'>Map of Zones</a>

















