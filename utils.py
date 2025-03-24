import json
import os
import nltk
import networkx as nx
import cugraph as cnx

from transformers import pipeline
from tqdm import tqdm

REDDIT_DATA_PATH = "data/"  # Replace with your directory path

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def list_json_files(directory):
    json_files = []
    for f in os.listdir(directory):
        if f.endswith('.json'):
            json_files.append(f)
    return json_files

def process_month(file_path):
    bs_month_text = []
    pr_month_text = []
    json_data = read_json_file(REDDIT_DATA_PATH+file_path)
    for d in json_data:
        if d['subreddit'] in ["brandonsanderson", "Stormlight_Archive"]:
            if "selftext" in d:
                print(d)
                bs_month_text.append(d["selftext"])
                break
        elif d['subreddit'] in ["KingkillerChronicle", "PatrickRothfuss"]:
            if "selftext" in d:
                print(d)
                pr_month_text.append(d["selftext"])
                break
    sentiment(pr_month_text, file_path + "r/brandonsanderson and r/Stormlight_Archive")
    sentiment(bs_month_text, file_path + "r/KingkillerChronicle and r/PatrickRothfuss")

def process_month_graph(file_path, g=None, subreddits = ["brandonsanderson", "Stormlight_Archive"]):
    if g is None:
        g = nx.Graph()

    json_data = read_json_file(REDDIT_DATA_PATH+file_path)

    if "RS" in file_path: # processing submissions
        for d in json_data:
            if d['subreddit'] in subreddits:

                g.add_node(d['author'], type='user')
                g.add_node(d['id'], type="submission", time=d['created_utc'])
                g.add_edge(d['author'], d['id'], time=d['created_utc'])

    elif "RC" in file_path: # processing comments
        for d in json_data:
            if d['subreddit'] in subreddits:
                
                g.add_node(d['author'], type='user')
                g.add_node(d['id'], type="comment", time=d['created_utc'])
                g.add_edge(d['author'], d['parent_id'], time=d['created_utc'])

    return g

def sentiment(list_of_strings, title):
    LOS = []
    for string in list_of_strings:
        if isinstance(string, list):
           LOS.append(string[0])
        else:
            LOS.append(string)

    def agg_scores(score_list):
        label0 = 0
        label1 = 0
        label2 = 0
        for item in score_list:
            if item['label'] == 'LABEL_1':
                label1 += 1
            elif item['label'] == 'LABEL_0':
                label0 += 1
            elif item['label'] == 'LABEL_2':
                label2 += 1
        print(title+'\n')
        print("negative sentiment: ", label0/len(score_list))
        print("neutral sentiment:", label1/len(score_list))
        print("positive sentiment: ", label2/len(score_list))
    model_path = "cardiffnlp/twitter-roberta-base-sentiment"
    sentiment_pipeline = pipeline(model=model_path, tokenizer=model_path, max_length=512, truncation=True)
    score_list = sentiment_pipeline(LOS)
    agg_scores(score_list)

def get_largest_connected_component(G):
    """Returns the largest connected component as a subgraph."""
    if nx.is_directed(G):
        # Use weakly connected components for directed graphs
        largest_cc = max(nx.weakly_connected_components(G), key=len)
    else:
        # Use connected components for undirected graphs
        largest_cc = max(nx.connected_components(G), key=len)

    # Create a subgraph from the largest component
    return G.subgraph(largest_cc).copy()

def compute_graph_measures(G):
    """Compute various network measures with tqdm tracking progress."""
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        measures = {}
        measures["degree_centrality"] = cnx.degree_centrality(G)
        measures["betweenness_centrality"] = cnx.betweenness_centrality(G)
        # measures["eigenvector_centrality"] = cnx.eigenvector_centrality(G)
        measures["pagerank"] = cnx.pagerank(G)
        hubs, authorities = nx.hits(G)
        measures["hubs"] = hubs
        measures["authorities"] = authorities

    return measures

def remove_node_type_and_rewire(G):
    """
    Removes nodes of a given type and rewires their neighbors directly.

    Parameters:
        G (networkx.Graph): The original graph.
        node_type_to_remove (str): The node type to remove (assumed stored in node attribute "type").

    Returns:
        networkx.Graph: A modified graph without the removed node type, with rewired connections.
    """
    G_modified = G.copy()

    # Identify nodes to remove
    nodes_to_remove = [n for n, data in G.nodes(data=True) if data.get("type") == 'node']

    for node in nodes_to_remove:
        neighbors = list(G_modified.neighbors(node))  # Get neighbors before removing the node


        # Fully connect the neighbors to each other
        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                if not G_modified.has_edge(neighbors[i], neighbors[j]):  # Avoid duplicate edges
                    G_modified.add_edge(neighbors[i], neighbors[j])

        # Remove the node
        G_modified.remove_node(node)

    return G_modified

nltk.download([
    "names",
    "stopwords",
    "state_union",
    "twitter_samples",
    "movie_reviews",
    "averaged_perceptron_tagger",
    "vader_lexicon",
    "punkt",
], quiet=True)
