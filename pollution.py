import requests


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
    pollution_key = 'x9HE9OTzXpQIRFaHZljhePhOq6egQ8ko2AnGmOq0l6BfWm4w'

    for place in places:
        r = requests.get('https://api.origins-china.cn/v1/places/{}?key={}'.format(place.id, pollution_key))

        pollution = r.json()['info.aqi']['data']

        for key, val in pollution.items():
            # 3 cities don't have o3 field but have aqi.cn instead
            if key in ['_count', 'aqi.cn']:
                continue
            place.pollution.update({key: val})

        print(place.name, place.pollution)



