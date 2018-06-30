import csv
import requests
import time


class Place:
    def __init__(self, name, id, lat, long) -> None:
        self.name = name
        self.id = id
        self.lat = lat
        self.long = long
        self.pollution = {}
        self.weather = {}


def get_pollution(places, unix_time, params):
    pollution_key = 'x9HE9OTzXpQIRFaHZljhePhOq6egQ8ko2AnGmOq0l6BfWm4w'

    for place in places:
        r = requests.get('https://api.origins-china.cn/v1/places/{}?key={}'.format(place.id, pollution_key))

        pollution = r.json()['info.aqi']['data']

        # 3 cities don't have o3 field but have aqi.cn instead
        for param in params:
            try:
                val = pollution[param]
            except KeyError:
                val = None
            finally:
                place.pollution.update({param: val})


def get_weather(places, unix_time, params):
    darksky_key = '4317146d63a0e039a4110e3ea201bd3d'

    for place in places:
        r = requests.get(
            'https://api.darksky.net/forecast/{}/{},{},{}'.format(darksky_key, place.lat, place.long, unix_time))

        weather = r.json()['currently']

        # windBearing field may be missing
        for param in params:
            try:
                val = weather[param]
            except KeyError:
                val = None
            finally:
                place.weather.update({param: val})


def main():
    places = [
        Place('Beijing', 2038349, 39.9042, 116.4074),
        Place('Zhangjiakou', 2033194, 40.7675, 114.8863),
        Place('Qinhuangdao', 1797593, 39.9354, 119.6005),
        Place('Shijiazhuang', 1795266, 38.0428, 114.5149),
        Place('Tianjin', 1792943, 39.3434, 117.3616),
    ]

    hours = 10

    pollution_params = ['co', 'no2', 'o3', 'pm10', 'pm25', 'so2']
    weather_params = ['pressure', 'windSpeed', 'windBearing']

    headers = []
    for place in places:
        for param in pollution_params:
            headers.append('{} {}'.format(place.name, param))

        for param in weather_params:
            headers.append('{} {}'.format(place.name, param))

    with open('weather.csv', 'w') as out_file:
        csv_writer = csv.writer(out_file)
        csv_writer.writerow(headers)

        s_per_hour = 3600
        cur_time = int(time.time())

        for unix_time in range(cur_time, cur_time - hours * s_per_hour, -s_per_hour):
            get_pollution(places, unix_time, pollution_params)
            get_weather(places, unix_time, weather_params)

            row = []
            for place in places:
                row.extend(place.pollution.values())
                row.extend(place.weather.values())

            csv_writer.writerow(row)


if __name__ == '__main__':
    main()
