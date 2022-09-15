import requests
import pandas as pd
import time


headers = {
    'accept': 'application/json',
}

params = {
    'ids': 'ethereum',
    'vs_currencies': 'usd',
    'include_market_cap': 'true',
    'include_24hr_vol': 'true',
    'include_24hr_change': 'true',
    'include_last_updated_at': 'true',
}

response = requests.get('https://api.coingecko.com/api/v3/simple/price', params=params, headers=headers)
data = response.json()
print(data)
df = pd.DataFrame.from_dict(data)
df.round(20)

dates_list = []

for index, row in df.iterrows():
    print(row)
print(df)
time.sleep(1.21)
