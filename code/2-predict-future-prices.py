import requests
import matplotlib.pyplot as plt
import dateutil.parser
import matplotlib.ticker as mtick

from pygam import LinearGAM, s
from pygam.utils import make_2d

url = 'https://api.collectipro.com/topshot-market-events'

request_params = {
  'apiKey': '<YOUR_API_KEY_HERE>',
  'editionId': '36_839',
  'eventTypeFilter': 'purchased',
  'limit': 100,
}

timestamps = []
prices = []
serial_numbers = []

num_requests = 0
def make_request(params):
  global num_requests
  num_requests += 1
  print("Making request #{}. Fetched and retained {} events so far.".format(num_requests, len(timestamps)))
  return requests.get(url, params=request_params).json()

def extract_data(json_response):
  for data in json_response['data']:
    if int(data['serialNumber'] >= 100): # filter out extremely low serial numbers
      timestamps.append(dateutil.parser.parse(data['transactionDt']))
      prices.append(float(data['price']))
      serial_numbers.append(int(data['serialNumber']))

response = make_request(request_params)
extract_data(response)
while 'cursor' in response['pagination']:
  request_params['cursor'] = response['pagination']['cursor']
  response = make_request(request_params)
  extract_data(response)

timestamps.reverse()
prices.reverse()
serial_numbers.reverse()

# Metadata found via https://collectipro.com/access/edition-finder
plt.figure().suptitle('Jayson Tatum dunk | 2021 All-Star Game (Series 2)')
plt.gca().set_yscale('log', base=1.1)
plt.gca().yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}')) 
scatter = plt.scatter(timestamps, prices, s=25, c=serial_numbers)
handles, labels = scatter.legend_elements(prop="colors", alpha=0.6)
legend2 = plt.gca().legend(handles, labels, loc="upper right", title="Serial #")

X = make_2d([x.timestamp() for x in timestamps], verbose=False)
y = prices
gam = LinearGAM(n_splines=4).gridsearch(X, y)
plt.plot(timestamps, list(gam.predict(X)), color='black')
plt.plot(timestamps, gam.confidence_intervals(X, width=0.9999), color='black', ls='--')

plt.gcf().autofmt_xdate()
plt.show()
