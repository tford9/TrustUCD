import networkx as nx
import pickle
from utils import *
import matplotlib.pyplot as plt
from tqdm.notebook import tqdm

global_G = nx.Graph()
nx.config.warnings_to_ignore.add("cache")


json_files_list = list_json_files(REDDIT_DATA_PATH)
rs_json_files_list = [j for j in json_files_list if "RS" in j]
rs_json_files_list = sorted(rs_json_files_list, key=lambda x: x[3:10])

rc_json_files_list = [j for j in json_files_list if "RC" in j]
rc_json_files_list = sorted(rc_json_files_list, key=lambda x: x[3:10])

grouped_files = list(zip(rs_json_files_list, rc_json_files_list))

global_data = []
local_running_data = []

for f1,f2 in tqdm(grouped_files):
    local_G: nx.Graph = process_month_graph(f1)
    local_G = process_month_graph(f2,g=local_G)
    local_G = get_largest_connected_component(local_G)
    print(f"Graph: Size {local_G.size()} - Order {local_G.order()}")

    dat = compute_graph_measures(local_G)
    local_running_data.append(dat)

    # pickle_filename = "local_graph_measures.pkl"
    # with open(pickle_filename, "wb") as f:
    #     pickle.dump(local_running_data, f)

    # Save to JSON
    json_filename = "local_graph_measures.json"
    with open(json_filename, "w") as f:
        json.dump(local_running_data, f, indent=4)

    # global_G = nx.compose(local_G, global_G)
    # dat = compute_graph_measures(global_G)
    # global_data.append(dat)

    # pickle_filename = "global_graph_measures.pkl"
    # with open(pickle_filename, "wb") as f:
    #     pickle.dump(global_data, f)