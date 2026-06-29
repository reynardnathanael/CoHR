import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer

# 1. Load your dataset
# Make sure the file is in the same directory as your script/notebook
df = pd.read_csv('../data/raw/azharali_train_parsed.csv')

# Drop any rows where 'experience' might be missing
text_data = df['experience'].dropna()

# 2. Extract N-Grams
# We configure CountVectorizer to look for bigrams and trigrams (2 to 3 words).
# 'stop_words' removes common English words (and, the, is, etc.).
# 'max_features' limits it to the top 40 most common n-grams to keep the graph readable.
vectorizer = CountVectorizer(ngram_range=(2, 3), stop_words='english', max_features=40)
X = vectorizer.fit_transform(text_data)

# 3. Create the Co-occurrence Matrix
# Matrix multiplication of the transposed Document-Term Matrix with itself
# gives us how many times term A and term B appear in the same resume.
co_occurrence_matrix = (X.T * X)

# Set the diagonal to 0 because we don't need to see a word co-occurring with itself
co_occurrence_matrix.setdiag(0)

# Get the actual n-gram text labels
terms = vectorizer.get_feature_names_out()
dense_matrix = co_occurrence_matrix.todense()

# 4. Build the Network Graph
G = nx.Graph()

# Change the threshold in your loop to a higher number (e.g., 10 or 15)
threshold = 12
# Add nodes (the n-grams) and edges (the co-occurrences)
for i in range(len(terms)):
    for j in range(i + 1, len(terms)):
        weight = dense_matrix[i, j]
        if weight > threshold:  
            G.add_edge(terms[i], terms[j], weight=weight)
G.remove_nodes_from(list(nx.isolates(G)))
# 5. Visualize the Graph
plt.figure(figsize=(14, 10))

# Spring layout calculates node positions to pull connected nodes closer together
# pos = nx.spring_layout(G, k=0.5, iterations=50)
pos = nx.spring_layout(G, k=0.9, iterations=100)

# Extract edge weights to adjust the thickness of the lines
edges = G.edges()
if edges:
    max_weight = max([G[u][v]['weight'] for u, v in edges])
    # Normalize weights so the thickest edge is width 5.0
    weights = [(G[u][v]['weight'] / max_weight) * 5.0 for u, v in edges]
else:
    weights = []

# Draw the network
# nx.draw_networkx_nodes(G, pos, node_size=1500, node_color='skyblue', alpha=0.8)
# nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif', font_weight='bold')
# When drawing, reduce the node_size and font_size
nx.draw_networkx_nodes(G, pos, node_size=800, node_color='lightblue', alpha=0.8)
nx.draw_networkx_edges(G, pos, edgelist=edges, width=weights, edge_color='gray', alpha=0.3)
nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif', font_weight='bold')

plt.title("N-Gram Co-occurrence Network (Experience)", fontsize=16)
plt.axis('off') # Hide the grid axis
plt.tight_layout()
plt.show()