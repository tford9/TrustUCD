import networkx as nx
import pickle
from utils import *
import matplotlib.pyplot as plt
from tqdm.notebook import tqdm
import pandas as pd
import numpy as np
import seaborn as sns 

def find_files(folder, substring):
    return [f for f in os.listdir(folder) if substring.lower() in f.lower()]

df = df2 = None


search_sub = 'comment'
matching_files = find_files("./data/raw_csv/", search_sub)
for f in matching_files:
    if df is None:
        df = pd.read_csv("./data/raw_csv/"+f,low_memory=False)
    else:
        df = pd.concat([df, pd.read_csv("./data/raw_csv/"+f,low_memory=False)])
df["type"] = 'comment'


search_sub = 'submission'
matching_files = find_files("./data/raw_csv/", search_sub)
for f in matching_files:
    if df2 is None:
        df2 = pd.read_csv("./data/raw_csv/"+f)
    else:
        df2 = pd.concat([df, pd.read_csv("./data/raw_csv/"+f,low_memory=False)])
df2["type"] = search_sub

df = pd.concat([df,df2])

data = df[['author', 'score', 'created_utc', 'body', 'selftext', 'parent_id', 'id','type', "link_id"]]

data['created_utc'] = pd.to_datetime(data['created_utc'], errors="coerce", utc=True, unit='s')

data = data.dropna(subset=['created_utc'])

# Extract year-month for grouping
data['year_month'] = data['created_utc'].dt.to_period('M')

start_date = pd.Timestamp("2011-08-01")
end_date = pd.Timestamp("2024-12-31")
date_range = pd.date_range(start=start_date, end=end_date, freq="MS")  # MS = Month Start

# Process one month at a time
G = nx.DiGraph()
local_running_data = []
global_data = []

for month, month_df in tqdm(data.groupby('year_month')):
    print(f"Processing {month}...")

    # Create directed graph
    L = nx.DiGraph()

    # Add edges based on user interactions via comments
    for _, row in month_df.iterrows():
        parent = row['parent_id']
        commenter = row['author']
        if row['type'] == 'submission':
            G.add_node(commenter)
            L.add_node(commenter)
        else:
            # print(parent)
            replying_to_submission = data[(data["id"] == parent[3:])]["author"]
            replying_to_comment = data[(data["id"] == parent[3:])]["author"]
            if len(replying_to_submission) > 0:
                # print(replying_to_submission.values[0])
                G.add_edge(replying_to_submission.values[0], commenter)
                L.add_edge(replying_to_submission.values[0], commenter)
            elif len(replying_to_comment) > 0: 
                # print(replying_to_comment.values[0])
                G.add_edge(replying_to_comment.values[0], commenter)
                L.add_edge(replying_to_comment.values[0], commenter)

    dat = compute_graph_measures(L)
    local_running_data.append(dat)

    dat = compute_graph_measures(G)
    global_data.append(dat)

    # Save the graph
    graph_filename = f"graphs/local_reddit_network_{month}.graphml"
    nx.write_graphml(L, graph_filename)
    # print(f"Saved {graph_filename}")
    
    # Save the graph
    graph_filename = f"graphs/global_reddit_network_{month}.graphml"
    nx.write_graphml(G, graph_filename)
    # print(f"Saved {graph_filename}")
    
    # Save to JSON
    json_filename = "local_graph_measures_extended.json"
    with open(json_filename, "w") as f:
        json.dump(local_running_data, f, indent=4)
    
    # Save to JSON
    json_filename = "global_graph_measures_extended.json"
    with open(json_filename, "w") as f:
        json.dump(global_data, f, indent=4)

print("Processing complete.")