import os
import json
import networkx as nx
import pandas as pd
import cudf as cd
from utils import compute_graph_measures
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


def find_files(folder, substring):
    return [f for f in os.listdir(folder) if substring.lower() in f.lower()]

df = df2 = None

search_sub = 'comment'
matching_files = find_files("./data/raw_csv/", search_sub)
for f in matching_files:
    if df is None:
        df = pd.read_csv("./data/raw_csv/"+f)
    else:
        df = pd.concat([df, pd.read_csv("./data/raw_csv/"+f)])
df["type"] = 'comment'

search_sub = 'submission'
matching_files = find_files("./data/raw_csv/", search_sub)
for f in matching_files:
    if df2 is None:
        df2 = pd.read_csv("./data/raw_csv/"+f)
    else:
        df2 = pd.concat([df, pd.read_csv("./data/raw_csv/"+f)])
df2["type"] = search_sub

df = pd.concat([df,df2])

data = df[['author', 'score', 'created_utc', 'body', 'selftext', 'parent_id', 'id','type', "link_id"]]


# data.year_month = data.year_month.apply(lambda x: x.strftime("%Y%m"))

data['parent_id'] = data['parent_id'].astype('str')

data['parent_raw_id'] = data['parent_id'].apply(lambda x:x[3:])

lookup_data = cd.from_pandas(data[['author', 'score', 'body', 'selftext', 'parent_id','parent_raw_id', 'id','type', "link_id", 'created_utc']])

parent_data = lookup_data[['author', 'parent_raw_id']]

id_data = lookup_data[['id','author', 'score', 'body', 'selftext', 'parent_id','type', "link_id", 'created_utc']]

lookup_data = cd.merge(id_data, parent_data, left_on='id', right_on='parent_raw_id', how='inner', suffixes=('_parent', '_commenter'))

# print(lookup_data.head())

data = lookup_data.to_pandas()

data['created_utc'] = pd.to_datetime(data['created_utc'], errors="coerce", utc=True, unit='s')

data = data.dropna(subset=['created_utc'])

# Extract year-month for grouping
data['year_month'] = data['created_utc'].dt.to_period('M')

start_date = pd.Timestamp("2011-08-01")
end_date = pd.Timestamp("2024-12-31")
date_range = pd.date_range(start=start_date, end=end_date, freq="MS")  # MS = Month Start

# lookup_data['parent_author'] = lookup_data.parent_id.apply(lambda x: lookup_author(x))
#
#
# data.set_index("id", inplace=True)
#
# # Process one month at a time
# G = cnx.Graph()
local_running_data = []
global_data = []

def process_month(month, month_df):
    month_df = month_df.drop(columns=['created_utc', 'year_month'])

    L = nx.from_pandas_edgelist(month_df, source='author_commenter', target='author_parent', create_using=nx.DiGraph())

    dat = compute_graph_measures(L)

    graph_filename = f"graphs/local_reddit_network_{month}.graphml"
    nx.write_graphml(L, graph_filename)

    return {
        "month": str(month),
        "graph_file": graph_filename,
        "measures": dat
    }

# Group and launch threads
monthly_groups = list(data.groupby('year_month'))

with ThreadPoolExecutor(max_workers=16) as executor:
    futures = [executor.submit(process_month, month, month_df.copy()) for month, month_df in monthly_groups]

    for future in tqdm(as_completed(futures), total=len(futures), desc="Processing months"):
        result = future.result()
        local_running_data.append(result)

# Save results after all threads complete
with open("local_graph_measures_extended.json", "w") as f:
    json.dump(local_running_data, f, indent=4)

print("Multithreaded processing complete.")