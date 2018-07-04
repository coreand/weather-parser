import csv
import datetime

import requests


class Place:
    def __init__(self, name, id, lat, long) -> None:
        self.name = name
        self.id = id
        self.lat = lat
        self.long = long
        self.pollution = []


places = [
    Place('Beijing', 2038349, 39.9042, 116.4074),
    Place('Zhangjiakou', 2033194, 40.7675, 114.8863),
    Place('Qinhuangdao', 1797593, 39.9354, 119.6005),
    Place('Shijiazhuang', 1795266, 38.0428, 114.5149),
    Place('Tianjin', 1792943, 39.3434, 117.3616),
]

start_time = datetime.datetime(2017, 3, 31, hour=0)
end_time = start_time + datetime.timedelta(days=1)


# end_time = datetime.datetime.now()


def write_csv(name, places, params, data):
    time_header = 'Timestamp (UTC)'

    header = [time_header]
    for place in places:
        for param in params:
            header.append('{} {}'.format(place.name, param))

    with open(name + '.csv', 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter='\t')
        csv_writer.writerow(header)
        csv_writer.writerows(data)


class PlaceData:
    def __init__(self, place, pollution) -> None:
        self.place = place
        self.pollution = pollution


# r_time.strftime('%Y-%m-%d %H:%M')


def get_place_pollution(place, r_start, r_end, params):
    key = 'x9HE9OTzXpQIRFaHZljhePhOq6egQ8ko2AnGmOq0l6BfWm4w'
    url = 'https://api.origins-china.cn/v1/places/{}/history?series=raw&begin={}&end={}&key={}'

    r = requests.get(url.format(place.id, r_start, r_end, key))
    info = r.json()['info.aqi']

    for hour_info in info:
        pollution = hour_info['data']
        timestamp = hour_info['ts'].replace('T', ' ').replace(':00Z', '')
        hour_data = [timestamp]

        for param in params:
            try:
                val = pollution[param]
            except KeyError:
                val = None
            finally:
                hour_data.append(val)

        place.pollution.append(hour_data)


def get_pollution():
    params = ['co', 'no2', 'o3', 'pm10', 'pm25', 'so2']

    delta = datetime.timedelta(days=30)

    r_time = start_time
    while r_time < end_time:
        r_start = r_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        r_time += delta
        r_end = r_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        for place in places:
            get_place_pollution(place, r_start, r_end, params)

        r_time += delta

    for idx, place in enumerate(places):
        write_csv(place.name, [place], params, place.pollution)

    data = []
    first_pollution = places[0].pollution
    for row_idx, row_data in enumerate(first_pollution):
        combined_row = [row_data[0]]
        for place in places:
            combined_row.extend(place.pollution[row_idx][1:])

        data.append(combined_row)

    write_csv('pollution', places, params, data)


def get_weather():
    key = '4317146d63a0e039a4110e3ea201bd3d'
    url = 'https://api.darksky.net/forecast/{}/{},{},{}'
    params = ['pressure', 'windSpeed', 'windBearing']

    delta = datetime.timedelta(hours=1)
    data = []

    r_time = start_time
    while r_time < end_time:
        unix_time = int(r_time.timestamp())

        for place in places:
            r = requests.get(url.format(key, place.lat, place.long, unix_time))
            weather = r.json()['currently']

            hour_data = [r_time.strftime('%Y-%m-%d %H:%M')]

            for param in params:
                try:
                    val = weather[param]
                except KeyError:
                    val = None
                finally:
                    hour_data.append(val)

            data.append(hour_data)

        r_time += delta


if __name__ == '__main__':
    get_pollution()
