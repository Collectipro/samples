import os
from pathlib import Path
import gzip
import dateutil.parser
import csv
import numpy as np
import itertools
import matplotlib.pyplot as plt
import statsmodels.api as sm
import matplotlib.ticker as mtick

# Provide the path to your directory containing the Collectipro csv.gz file(s)
data_directory = "{}/collectipro-bulk-data/".format(Path.home())

# Keep a running dictionary of editionId -> purchase prices
edition_to_hour_to_purchase_prices = {}

def process_file(gzip_file):
  print("Loading file {}".format(gzip_file))

  total_lines = 0
  with gzip.open(data_directory + gzip_file, 'rt') as f:
    for i, l in enumerate(f):
      pass
    total_lines = i
    print("File {} contains {} events".format(gzip_file, total_lines))
  
  with gzip.open(data_directory + gzip_file, 'rt') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
      if i % 10_000 == 0:
        print("{}/{} | {}% parsing {}".format(str(i).rjust(8), total_lines, str(round(i / total_lines * 100, 2)).rjust(6), gzip_file))
      if row['eventType'] == 'purchased':
        hour = dateutil.parser.parse(row['transactionDt']).strftime('%H')
        this_edition_hour_to_purchase_prices = edition_to_hour_to_purchase_prices.setdefault(row['editionId'], {})
        this_edition_hour_to_purchase_prices.setdefault(hour, []).append(float(row['price']))

    print("Finished parsing {}\n".format(gzip_file))

for gzip_file in filter(lambda x: '2021-01' in x, sorted(os.listdir(data_directory))):
  if gzip_file.endswith('.csv.gz'):
    process_file(gzip_file)

hour_to_avg_diffs = {}
for edition_id, hour_to_purchase_prices in edition_to_hour_to_purchase_prices.items():
  for hour, purchase_prices in sorted(hour_to_purchase_prices.items()):
    mean = np.mean(list(itertools.chain(*hour_to_purchase_prices.values())))
    hour_to_avg_diffs.setdefault(hour, []).append(np.mean(purchase_prices) - mean)

x = []
y = []
mean = np.mean(list(itertools.chain(*hour_to_avg_diffs.values())))
for hour, avg_diffs in sorted(hour_to_avg_diffs.items()):
  x.append(hour)
  y.append(np.mean(avg_diffs) - mean)

lowess = sm.nonparametric.lowess(y, x, frac=.4)
lowess_x = list(zip(*lowess))[0]
lowess_y = list(zip(*lowess))[1]

plt.gcf().suptitle("January's average sale price by hour (UTC) relative to overall average")
plt.plot(x, y, label='hourly mean')
plt.plot(lowess_x, lowess_y, label='loess fit')
plt.gca().fill_between(x, 0, y)
plt.gca().yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}')) 
plt.gca().legend()
plt.show()
