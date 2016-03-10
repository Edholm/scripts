#!/usr/bin/python
# Send a pushover notification about Styr och Ställ bike availability
import sys
import math
import requests
import json
from pathlib import Path


def read_config():
    script_path = Path(sys.argv[0])
    conf_file = script_path.parent / Path(script_path.stem + '.json')
    if not conf_file.exists():
        print("Couldn't read config file " + str(conf_file))
        sys.exit(1)

    return json.loads(conf_file.read_text())


# Takes coordinates as (lat, long)
# http://stackoverflow.com/a/27943
def calc_dist(coord, my_coord):
    lat1, lon1 = coord
    lat2, lon2 = my_coord

    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
        math.cos(math.radians(lat1)) * \
        math.radians(lat2) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d


def list_bikes(data, stations, config):
    filtered = [x for x in data if x['StationId'] in stations]
    my_coord = (config['my_lat'], config['my_long'])
    filtered = sorted(filtered,
                      key=lambda x: calc_dist((x['Lat'], x['Long']),
                                              my_coord))

    ret = []
    longest_name = max([len(x['Name']) for x in filtered])
    for bike in filtered:
        name = bike['Name'].ljust(longest_name)
        avail_bikes = bike['AvailableBikes'] if 'AvailableBikes' in bike else 0
        avail_stands = bike['BikeStands'] - avail_bikes
        ret.append("{1:02d}|{2:>2} - {0}".format(
            name,
            avail_bikes,
            avail_stands))
    return "\n".join(ret)


def pushover_notification(text, config):
    data = {
        'token': config['pushover_app'],
        'user': config['pushover_user'],
        'message': text,
        'title': "Bike availability",
    }
    r = requests.post("https://api.pushover.net/1/messages.json", data=data)
    print("Pushover response (" + str(r.status_code) + "): ")
    print(r.text)


def main():
    config = read_config()
    req = requests.get(config['url'])

    if req.status_code != 200:
        print("Failed to get bikes from API. Status code: " + req.status_code)
        return
    bikes = req.json()
    formatted = list_bikes(bikes, config['wanted_stations'], config)
    print(formatted)
    pushover_notification(formatted, config)


if __name__ == '__main__':
    main()
