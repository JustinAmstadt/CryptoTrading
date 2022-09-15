import requests
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import pytz

headers = {
    'accept': 'application/json',
}

params = {
    'vs_currency': 'usd',
    'days': '30',
}

response = requests.get('https://api.coingecko.com/api/v3/coins/ethereum/market_chart', params=params, headers=headers)

data = response.json()

# print(data)

df = pd.DataFrame.from_dict(data)

dates_list_milli = []
dates_list_calendar = []
dates_list_time = []

timezone = pytz.timezone("UTC")

for index, row in df.iterrows():
    just_dates_mill = row['prices'][0]
    row['prices'] = row['prices'][1]
    row['market_caps'] = row['market_caps'][1]
    row['total_volumes'] = row['total_volumes'][1]
    just_dates_greg = datetime.datetime.fromtimestamp(just_dates_mill/1000.0, tz = timezone)
    dates_list_milli.append(str(just_dates_mill))
    dates_list_calendar.append(just_dates_greg.strftime("%d/%m/%Y"))
    dates_list_time.append(just_dates_greg.strftime("%H:%M:%S"))

df.insert(0, 'millisecond', dates_list_milli)
df.insert(1, 'date', dates_list_calendar)
df.insert(2, 'time', dates_list_time)

print(df)
df.plot(x='date', y='prices', kind='line')
plt.show()
