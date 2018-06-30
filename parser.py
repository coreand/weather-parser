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


if __name__ == '__main__':
    places = [
        Place('Beijing', 2038349, 39.9042, 116.4074),
        Place('Zhangjiakou', 2033194, 40.7675, 114.8863),
        Place('Qinhuangdao', 1797593, 39.9354, 119.6005),
        Place('Shijiazhuang', 1795266, 38.0428, 114.5149),
        Place('Tianjin', 1792943, 39.3434, 117.3616),
    ]

    cur_time = int(time.time())

    pollution_key = 'x9HE9OTzXpQIRFaHZljhePhOq6egQ8ko2AnGmOq0l6BfWm4w'
    darksky_key = '4317146d63a0e039a4110e3ea201bd3d'

    s_per_hour = 3600

    pollution_params = ['co', 'no2', 'o3', 'pm10', 'pm25', 'so2']
    weather_params = ['pressure', 'windSpeed', 'windBearing']

    headers = []
    for place in places:
        for param in pollution_params:
            headers.append('{} {}'.format(place.name, param))

        for param in weather_params:
            headers.append('{} {}'.format(place.name, param))

    print(headers)

    for unix_time in range(cur_time, cur_time - 1 * s_per_hour, -s_per_hour):
        row = []
        for place in places:
            r = requests.get('https://api.origins-china.cn/v1/places/{}?key={}'.format(place.id, pollution_key))

            pollution = r.json()['info.aqi']['data']

            # 3 cities don't have o3 field but have aqi.cn instead

            for param in pollution_params:
                try:
                    val = pollution[param]
                except KeyError:
                    val = None
                finally:
                    place.pollution.update({param: val})

            # weather
            r = requests.get(
                'https://api.darksky.net/forecast/{}/{},{},{}'.format(darksky_key, place.lat, place.long, unix_time))
            weather = r.json()['currently']

            # windBearing field may be missing

            for param in weather_params:
                try:
                    val = weather[param]
                except KeyError:
                    val = None
                finally:
                    place.weather.update({param: val})
