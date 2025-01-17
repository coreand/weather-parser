import datetime

import requests
import pandas as pd


class Place:
    def __init__(self, name, id, lat, long) -> None:
        self.name = name
        self.id = id
        self.lat = lat
        self.long = long


places = [
    Place('Beijing', 2038349, 39.9042, 116.4074),
    Place('Zhangjiakou', 2033194, 40.7675, 114.8863),
    Place('Qinhuangdao', 1797593, 39.9354, 119.6005),
    Place('Shijiazhuang', 1795266, 38.0428, 114.5149),
    Place('Tianjin', 1792943, 39.3434, 117.3616),
]

start_time = datetime.datetime(2017, 3, 31, hour=0)
end_time = datetime.datetime.now()
_dates = pd.date_range(start_time, end_time, freq="1h")

pollution_params = ['co', 'no2', 'o3', 'pm10', 'pm25', 'so2']
weather_params = ['pressure', 'windSpeed', 'windBearing']
beijing_hours = [1, 3, 6, 12, 24, 48, 72, 168]
bj_pm = 'Beijing pm25'


def get_header():
    header = []
    for place in places:
        for param in pollution_params + weather_params:
            header.append('{} {}'.format(place.name, param))

    for hours in beijing_hours:
        header.append('{} {}'.format(bj_pm, hours))

    return header


df = pd.DataFrame(index=_dates, columns=get_header())


def get_place_pollution(place, r_start, r_end):
    key = 'x9HE9OTzXpQIRFaHZljhePhOq6egQ8ko2AnGmOq0l6BfWm4w'
    url = 'https://api.origins-china.cn/v1/places/{}/history?series=raw&begin={}&end={}&key={}'

    r = requests.get(url.format(place.id, r_start, r_end, key))
    info = r.json()['info.aqi']

    for hour_info in info:
        pollution = hour_info['data']
        timestamp = hour_info['ts']
        timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
        for param in pollution_params:
            try:
                val = pollution[param]
            except KeyError:
                val = None
            finally:
                col = '{} {}'.format(place.name, param)
                df.at[timestamp, col] = val


def get_pollution():
    delta = datetime.timedelta(days=30)
    time_format = '%Y-%m-%dT%H:%M:%SZ'

    r_time = start_time
    while r_time < end_time:
        r_start = r_time.strftime(time_format)
        r_time += delta
        r_end = r_time.strftime(time_format)

        for place in places:
            get_place_pollution(place, r_start, r_end)


def add_beijing_pm():
    for row in df.itertuples(index=True):
        timestamp = row[0]

        for hours in beijing_hours:
            delta = datetime.timedelta(hours=hours)
            r_time = timestamp + delta

            try:
                pm_val = df.at[r_time, bj_pm]
            except KeyError:
                pm_val = None
            finally:
                df.at[timestamp, '{} {}'.format(bj_pm, hours)] = pm_val


def get_weather():
    key = '4317146d63a0e039a4110e3ea201bd3d'
    url = 'https://api.darksky.net/forecast/{}/{},{},{}'

    delta = datetime.timedelta(hours=24)

    r_time = start_time
    while r_time < end_time:
        unix_time = int(r_time.timestamp())

        for place in places:
            r = requests.get(url.format(key, place.lat, place.long, unix_time))
            hourly_weather = r.json()['hourly']['data']

            for weather in hourly_weather:
                timestamp = datetime.datetime.fromtimestamp(weather['time'])

                for param in weather_params:
                    try:
                        val = weather[param]
                    except KeyError:
                        val = None
                    finally:
                        col = '{} {}'.format(place.name, param)
                        df.at[timestamp, col] = val

        r_time += delta


def save_df():
    get_pollution()
    get_weather()
    add_beijing_pm()

    time_format = '%Y-%m-%d %H:%M'
    time_header = 'Timestamp (UTC)'

    df[1:].to_csv('weather.csv', index_label=time_header, date_format=time_format)


if __name__ == '__main__':
    save_df()
