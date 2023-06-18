# NLP chatbot

- Name: Samuel Brouwer
- Student number: 649186
- python version: 3.10.4

## description of the programme:

This program is a chatbot that uses a knowledge graph generated from a Wikipedia page to provide responses to user queries. The chatbot leverages several libraries such as NetworkX, pandas, spaCy, textacy, pickle, wikipediaapi, matplotlib, keytotext, and Spellchecker.

Here's a breakdown of the program:

Importing Libraries: The program starts by importing the necessary libraries, including NetworkX, pandas, spaCy, textacy, pickle, wikipediaapi, matplotlib, keytotext, and Spellchecker.

Setting up Language Models: Two language models are loaded: "k2t-base" from the keytotext library for generating answers, and "en_core_web_md" from spaCy for natural language processing tasks.

Variables and File Paths: The program defines variables for the Wikipedia page name, graph file path, and Wikipedia file path based on the page name.

Function: create_graph_from_wikipedia_page(): This function creates a knowledge graph from the Wikipedia page. It checks if the Wikipedia file already exists and reads the text from it. If not, it fetches the page text using the wikipediaapi library and saves it to the file. The function then extracts entities, relations, and objects from the text and creates a dataframe. It identifies the most common entity and filters the dataframe accordingly. It then creates a directed graph using NetworkX, saves it to a pickle file, and visualizes the graph using matplotlib.

Function: load_graph(file_path): This function loads a graph from a pickle file.

Function: preprocess_text(input_text): This function preprocesses the user's input text. It converts the text to lowercase, removes question marks, removes stopwords using spaCy's STOP_WORDS, performs spelling correction using the Spellchecker library, and returns the preprocessed text.

Function: generate_answer(graph, query): This function generates an answer to the user's query using the knowledge graph. It calculates the similarity between the query and each node in the graph using spaCy's similarity metric. It finds the node with the highest similarity score and retrieves the answer based on the outgoing edges of that node. It uses the keytotext pipeline to generate a response by providing the source, relation, and destination as input. The function returns the generated response.

Function: get_response(input_text): This function handles the user's input and generates the chatbot's response. If the input is 'exit', the function exits. It checks if the graph file exists and loads the graph if it does. If the graph file doesn't exist, it calls the create_graph_from_wikipedia_page() function to create the graph. It then preprocesses the user's input and calls the generate_answer() function to generate the chatbot's response. If no response is generated, a default message is returned. The function returns the chatbot's response.

Chatbot Loop: The program enters a loop that continuously prompts the user for input. It calls the get_response() function with the user's input and prints the chatbot's response. The loop continues until the user inputs 'exit'. Finally, a closing message is displayed.

Overall, the program creates a chatbot that uses a knowledge graph derived from a Wikipedia page to generate responses to user queries. It uses = natural language processing techniekes to provide answers to user questions.
