#!/usr/bin/python
# Send a pushover notification about Styr och Ställ bike availability
import sys
import requests
import json
from pathlib import Path


def read_config():
    script_name = Path(sys.argv[0]).stem
    conf_file = Path(script_name + '.json')
    if not conf_file.exists():
        print("Couldn't read config file " + str(conf_file))
        sys.exit(1)

    return json.loads(conf_file.read_text())


def list_bikes(data, stations):
    filtered = [x for x in data if x['StationId'] in stations]

    ret = []
    longest_name = max([len(x['Name']) for x in filtered])
    for bike in filtered:
        name = bike['Name'].ljust(longest_name)
        avail_bikes = bike['AvailableBikes'] if 'AvailableBikes' in bike else 0
        avail_stands = bike['BikeStands'] - avail_bikes
        ret.append("{3:>2} {0}  {1:>2} cycklar - {2:>2} platser".format(
            name,
            avail_bikes,
            avail_stands,
            bike['StationId']))
    return "\n".join(ret)


def main():
    config = read_config()
    req = requests.get(config['url'])

    if req.status_code != 200:
        print("Failed to get bikes from API. Status code: " + req.status_code)
        return
    bikes = req.json()
    # FIXME: pushover notification
    print(list_bikes(bikes, config['wanted_stations']))


if __name__ == '__main__':
    main()
