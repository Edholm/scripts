#!/usr/bin/python
# Send a pushover notification about Styr och Ställ bike availability
import sys
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


def list_bikes(data, stations):
    filtered = [x for x in data if x['StationId'] in stations]
    # TODO: sort by distance to "me"

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
    formatted = list_bikes(bikes, config['wanted_stations'])
    print(formatted)
    pushover_notification(formatted, config)


if __name__ == '__main__':
    main()
