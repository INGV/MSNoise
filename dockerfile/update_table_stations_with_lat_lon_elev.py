from obspy.clients.fdsn import Client
import os, glob
import xml.etree.ElementTree as ET
import pymysql
import time

#client = Client("EIDA")
client = Client("INGV")

def extract_station_info(inventory_file, network_code, station_code):
    tree = ET.parse(inventory_file)
    root = tree.getroot()
    if inventory_file != "station.xml":
        ns = {'seiscomp': 'http://geofon.gfz-potsdam.de/ns/seiscomp3-schema/0.10'}

        stations = root.findall('.//seiscomp:station', ns)
        for station in stations:
            latitude = station.find('seiscomp:latitude', ns).text
            longitude = station.find('seiscomp:longitude', ns).text
            elevation = station.find('seiscomp:elevation', ns).text
            print(f'Latitude: {latitude}, Longitude: {longitude}, Elevation: {elevation}')
            return latitude, longitude, elevation

    else:
        ns = {'fdsn': 'http://www.fdsn.org/xml/station/1'}

        for network in root.findall('fdsn:Network', ns):
            if network.get('code') == network_code:
                for station in network.findall('fdsn:Station', ns):
                    if station.get('code') == station_code:
                        latitude = station.find('fdsn:Latitude', ns).text
                        longitude = station.find('fdsn:Longitude', ns).text
                        elevation = station.find('fdsn:Elevation', ns).text
                        return latitude, longitude, elevation
        return None, None, None


Host = "localhost"
User = "msnoise"
Password = "msnoise"
database = "msnoise"

conn = pymysql.connect(host=Host, user=User, password=Password, database=database)
cur = conn.cursor()

query = f"SELECT * FROM stations WHERE X or Y or altitude = 0"
cur.execute(query)

rows = cur.fetchall()

for row in rows:
    print(row)

conn.close()

for row in rows:
    net = row[1]  # Assuming 'net' is in the second column (index 1)
    sta = row[2]  # Assuming 'station' is in the third column (index 2)
    print(net)
    print(sta)

    try:
        try:
            client.get_stations(network=net, station=sta, level="channel", format="xml", filename="station.xml")
            inventory_file = "station.xml"
            latitude, longitude, elevation = extract_station_info(inventory_file, net, sta)
        except Exception as e:
            print(e)
            print('Updating stations table with data from inventory files found in /inventories-for-station-not-on-fdsn folder')
            inventory_file = f"/inventories-for-station-not-on-fdsn/station_{net}_{sta}_inventory.xml"
            latitude, longitude, elevation = extract_station_info(inventory_file, net, sta)

        conn = pymysql.connect(host=Host, user=User, password=Password, database=database)
        cur = conn.cursor()

        query = f"UPDATE stations SET X='{longitude}', Y='{latitude}', altitude='{elevation}', coordinates='DEG' WHERE net='{net}' AND sta='{sta}'"
        cur.execute(query)
        conn.commit()
        conn.close()
        time.sleep(0.2)

    except Exception as e:
        print(e)
