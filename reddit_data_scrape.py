import json
import os

# import networkx as nx
# import numpy as np
import matplotlib.pyplot as plt

from pathos.multiprocessing import ProcessingPool as Pool

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download([
    "names",
    "stopwords",
    "state_union",
    "twitter_samples",
    "movie_reviews",
    "averaged_perceptron_tagger",
    "vader_lexicon",
    "punkt",
])

from transformers import pipeline

directory_path = "C:\\Users\\Trenton W. Ford\\PycharmProjects\\TrustUCD\\data\\"  # Replace with your directory path


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


def word_plot(list_of_words, title):
    comment_words = ''
    stopwords = set(STOPWORDS)

    for val in list_of_words:
        # typecaste each val to string
        val = str(val)
        # split the value
        tokens = val.split()
        # Converts each token into lowercase
        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()

        comment_words += " ".join(tokens)+" "

    wordcloud = WordCloud(width = 1680, height = 960,
                    background_color ='white',
                    stopwords = stopwords,
                    min_font_size = 10).generate(comment_words)

    # plot the WordCloud image
    plt.figure(figsize = (8, 16), facecolor = None)
    plt.imshow(wordcloud)
    plt.title(title)
    plt.axis("off")
    plt.tight_layout(pad = 0)

    plt.show()


def process_month(file_path):
    bs_month_text = []
    pr_month_text = []
    json_data = read_json_file(directory_path+file_path)
    for d in json_data:
        if d['subreddit'] in ["brandonsanderson", "Stormlight_Archive"]:
            bs_month_text.append(d["selftext"])
        elif d['subreddit'] in ["KingkillerChronicle", "PatrickRothfuss"]:
            pr_month_text.append(d["selftext"])

    sentiment(pr_month_text, file_path + "r/brandonsanderson and r/Stormlight_Archive")
    sentiment(bs_month_text, file_path + "r/KingkillerChronicle and r/PatrickRothfuss")


json_files_list = list_json_files(directory_path)
json_files_list = [j for j in json_files_list if "RS" in j]

pool = Pool(processes=12)

# Map the file opening function to the file paths
pool.map(process_month, json_files_list)

# Close the pool
pool.close()
pool.join()