import random
import pandas as pd
import networkx as nx
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from spellchecker import SpellChecker
import json

# Load English tokenizer, tagger, parser, and NER
nlp = spacy.load("en_core_web_md")

# Define possible user inputs and corresponding chatbot responses
data = pd.read_json("netherlands_data.json")
# print(data.head())

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

    return query

def knowledge_graph(data):
    graph = nx.Graph()
    for question in data["question"]:
        answer = data[data["question"] == question]["answer"].values[0]
        question = preprocess_text(question)  # Preprocess the question

        graph.add_node(question)
        graph.add_node(answer)
        graph.add_edge(question, answer, relation="True")

    return graph



def add_synonyms(graph, synonyms):
    for original, synonym_list in synonyms.items():
        for synonym in synonym_list:
            if graph.nodes.__contains__(synonym):
                graph.add_edge(original, synonym, relation="Synonym")
    return graph

# Create the knowledge graph
graph = knowledge_graph(data)

print("Graph Nodes:", graph.nodes)
print("Graph Edges:", graph.edges)

# get a dictionary of synonyms
with open('synonyms.json') as json_file:
    # Load the JSON data
    synonyms = json.load(json_file)

# Add synonyms to the graph
graph = add_synonyms(graph, synonyms)

print("Graph Nodes:", graph.nodes)
print("Graph Edges:", graph.edges)


# Define function to get a response from the chatbot
def get_response(input_text):
    if input_text == 'exit':
        return None

    # preprocess text
    query = preprocess_text(input_text)  # Preprocess the user's input

    highest_score = 0.0
    most_similar = None
    most_similar_question = None

    for graph_question in graph.nodes:
        similarity = nlp(query).similarity(nlp(graph_question))
        if similarity > highest_score:
            highest_score = similarity
            most_similar = graph[graph_question]  # Replace `graph.neighbors(graph_question)` with `graph[graph_question]`
            most_similar_question = graph_question

    if highest_score <= 0.75:
        return "I'm sorry, we don't have an answer for this."
    else:
        print(f"The answer is similar to the question: {most_similar_question} with a score of {highest_score}")
        return next(iter(most_similar))


# Loop to continuously prompt the user for input and return chatbot responses
print("ask me a question:\nexample:")
print(data.head())
while True:
    user_input = input("Question: ")
    chatbot_response = get_response(user_input)
    if not chatbot_response:
        break
    print("Chatbot: " + chatbot_response)

print("Thanks for chatting with my bot")