import string
from flask import Flask, render_template, request, jsonify
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

app = Flask(__name__)

# Fetch dataset and initialize vectorizer and LSA
newsgroups = fetch_20newsgroups(subset='all')
stop_words = stopwords.words('english')

def preprocess_text(text):
    """
    Preprocess the input text by lowercasing, removing punctuation, and filtering out stopwords.
    """
    # Remove punctuation and lowercase
    text = ''.join([char for char in text if char not in string.punctuation])
    return ' '.join([word.lower() for word in text.split() if word.lower() not in stop_words])

# Preprocess the newsgroups data
processed_data = [preprocess_text(doc) for doc in newsgroups.data]

# Vectorize the preprocessed text
vectorizer = TfidfVectorizer(max_features=5000)
X_tfidf = vectorizer.fit_transform(processed_data)

# Apply LSA using TruncatedSVD
lsa = TruncatedSVD(n_components=100)
X_lsa = lsa.fit_transform(X_tfidf)

def search_engine(query):
    """
    Function to search for top 5 similar documents given a query
    Input: query (str)
    Output: documents (list), similarities (list), indices (list)
    """
    # Preprocess the query
    preprocessed_query = preprocess_text(query)
    
    # Vectorize the preprocessed query and apply LSA transformation
    query_tfidf = vectorizer.transform([preprocessed_query])
    query_lsa = lsa.transform(query_tfidf)
    
    # Compute cosine similarity between the query and all documents
    similarities = cosine_similarity(query_lsa, X_lsa)[0]
    
    # Get top 5 similar documents
    top_indices = np.argsort(similarities)[-5:][::-1]
    top_similarities = similarities[top_indices].tolist()  # Convert to list
    top_documents = [newsgroups.data[i] for i in top_indices]

    return top_documents, top_similarities, top_indices.tolist()  # Ensure all outputs are lists


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    documents, similarities, indices = search_engine(query)
    return jsonify({'documents': documents, 'similarities': similarities, 'indices': indices})

if __name__ == '__main__':
    app.run(debug=True)
