import os
from pathlib import Path
import gzip
import dateutil.parser
import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Provide the path to your directory containing the Collectipro csv.gz file(s)
data_directory = "{}/collectipro-bulk-data/".format(Path.home())

# Keep a running dictionary of date -> purchase volume on that day
date_to_purchase_volume = {}
# Keep a running dictionary of date -> count of listings/purchases on that day
date_to_purchases = {}
date_to_listings = {}

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
      date = dateutil.parser.parse(row['transactionDt']).strftime('%Y-%m-%d')
      if row['eventType'] == 'purchased':
        date_to_purchase_volume[date] = date_to_purchase_volume.setdefault(date, 0) + float(row['price'])
        date_to_purchases[date] = date_to_purchases.setdefault(date, 0) + 1
      elif row['eventType'] == 'listed':
        date_to_listings[date] = date_to_listings.setdefault(date, 0) + 1

    print("Finished parsing {}\n".format(gzip_file))

for gzip_file in sorted(os.listdir(data_directory)):
  if gzip_file.endswith('.csv.gz'):
    process_file(gzip_file)

dates_purchases, purchases = zip(*sorted(date_to_purchases.items()))
dates_listings, listings = zip(*sorted(date_to_listings.items()))

fig, ax = plt.subplots()
fig.suptitle('Daily purchase volume and events')
fig.autofmt_xdate()
ax.xaxis_date()
ax2 = ax.twinx()

ax.bar([dateutil.parser.parse(x) for x in dates_purchases], purchases, label = 'purchase volume', width=1, alpha=0.5)
ax.set_ylabel("volume ($)")
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}')) 

ax2.plot([dateutil.parser.parse(x) for x in dates_purchases], purchases, label = 'purchases')
ax2.plot([dateutil.parser.parse(x) for x in dates_listings], listings, label = 'listings')
ax2.set_ylabel("# events")

ax.legend(loc=2)
ax2.legend(loc=1)

plt.show()
