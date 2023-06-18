import networkx as nx
import pandas as pd
import spacy
import textacy
import pickle
import wikipediaapi
from spacy.lang.en.stop_words import STOP_WORDS
from spellchecker import SpellChecker
import os
import matplotlib.pyplot as plt
from keytotext import pipeline

nlp_ai = pipeline("k2t-base")
nlp = spacy.load("en_core_web_md")

wiki_page_name = "Presidency_of_Donald_Trump"
graph_file_path = wiki_page_name + "_knowledge_graph.gpickle"
wiki_file_path = wiki_page_name + "_page"

def create_graph_from_wikipedia_page():
    # Check if the wiki file exists
    if os.path.exists(wiki_file_path):
        with open(wiki_file_path, 'r') as file:
            text_py = file.read()
    else:
        wiki_wiki = wikipediaapi.Wikipedia('en')
        page_py = wiki_wiki.page(wiki_page_name)
        text_py = page_py.text

        with open(wiki_file_path, 'w', encoding='utf-8') as file:
            file.write(text_py)

    lst_docs = [sent for sent in nlp(text_py).sents]

    ## extract entities and relations
    dic = {"id": [], "text":[], "entity":[], "relation":[], "object":[]}

    for i, sentence in enumerate(lst_docs):
        for sent in textacy.extract.subject_verb_object_triples(sentence):
            subj = " ".join(map(str, sent.subject))
            obj  = " ".join(map(str, sent.object))
            relation = " ".join(map(str, sent.verb))

            dic["id"].append(i)
            dic["text"].append(sentence.text)
            dic["entity"].append(subj)
            dic["object"].append(obj)
            dic["relation"].append(relation)

    ## create dataframe
    dtf = pd.DataFrame(dic)

    most_common_entity = dtf["entity"].value_counts().head().index[0]
    f = most_common_entity
    tmp = dtf[(dtf["entity"]==f) | (dtf["object"]==f)]

    ## create small graph
    G = nx.from_pandas_edgelist(tmp, source="entity", target="object", 
                                edge_attr="relation", 
                                create_using=nx.DiGraph())
    
    with open(graph_file_path, 'wb') as f:
        pickle.dump(G, f)

    ## plot
    plt.figure(figsize=(15,10))
    pos = nx.spring_layout(G, k=1)

    node_color = ["red" if node==f else "skyblue" for node in G.nodes]
    edge_color = ["red" if edge[0]==f else "black" for edge in G.edges]

    nx.draw(G, pos=pos, with_labels=True, node_color=node_color, 
            edge_color=edge_color,
            node_size=2000, node_shape="o")

    nx.draw_networkx_edge_labels(G, pos=pos, label_pos=0.5, 
                            edge_labels=nx.get_edge_attributes(G,'relation'),
                            font_size=12, font_color='black', alpha=0.6)
    plt.show()

    return G

def load_graph(file_path):
    with open(file_path, 'rb') as f:
        G = pickle.load(f)
    return G

def preprocess_text(input_text):
    # Convert input text to lowercase
    input_text = input_text.lower()

    # Remove question mark
    input_text = input_text.replace("?", "")

    # Remove stopwords
    doc = nlp(input_text)
    tokens = [token.text for token in doc if token.text.lower() not in STOP_WORDS]
    preprocessed_text = " ".join(tokens)

    # Perform spelling correction
    spell_checker = SpellChecker(language='en')
    query = spell_checker.correction(preprocessed_text)
    if query is None:
        query = preprocessed_text

    # lemmenitizer

    return query

def generate_answer(graph, query):
    highest_score = 0
    nodes = {}
    for node in graph.nodes:
        similarity = nlp(query).similarity(nlp(node))
        if similarity > highest_score:
            highest_score = similarity
            nodes[node] = [highest_score, graph[node]]
    
    best_answer = max(nodes, key=nodes.get)

    for source, destination, relation in graph.out_edges(best_answer, data=True):
        if source == best_answer:
            relationship = relation.get('relation')

    response = None
    train = {"do_sample": True, "num_beams": 4, "no_repeat_ngram_size": 3, "early_stopping": True, "max_new_tokens":20}

    for source, destination, relation in graph.out_edges(best_answer, data=True):
        if source == best_answer:
            response = nlp_ai([source, relation.get('relation'), destination], **train)
            break
        elif(relation.get('relation') == relationship):
            response = nlp_ai([source, relation.get('relation'), destination], **train)
            break
    if not response:
        response = "Sorry, I have no information on that"
    return response

def get_response(input_text):
    if input_text == 'exit':
        return None
    
    # Check if the graph file exists
    if os.path.exists(graph_file_path):
        # Load the graph from the saved file
        G = load_graph(graph_file_path)
    else:
        # Create the graph and save it
        G = create_graph_from_wikipedia_page()
    
    # preprocess text
    query = preprocess_text(input_text)  # Preprocess the user's input

    # Add code here to generate the chatbot response using the loaded_graph
    # return generate_answer(G, query)
    answer = generate_answer(G, query)
    if not answer:
        return "I'm sorry i dont know the answer to that"

    return answer

# Loop to continuously prompt the user for input and return chatbot responses
while True:
    user_input = input("Question: ")
    chatbot_response = get_response(user_input)
    if not chatbot_response:
        break
    print("Chatbot: " + chatbot_response)

print("Thanks for chatting with my bot")