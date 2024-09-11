from flask import Flask, request, jsonify, render_template
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the dataset into memory when the server starts
df = pd.read_csv('drugsComTrain_raw.csv')
disease_names = df['condition'].dropna().str.lower().tolist()

# Function to recommend drugs based on disease condition
def recommend_drug(condition):
    # Filter the dataset for the given condition
    condition_data = df[df['condition'].str.lower() == condition.lower()]
    
    if condition_data.empty:
        return "No data available for this condition"

    # Sort based on rating, usefulCount, and sentiment (if available)
    condition_data['combined_score'] = condition_data[['rating', 'usefulCount']].sum(axis=1)
    top_drugs = condition_data.nlargest(2, 'combined_score').drop_duplicates('drugName')

    return top_drugs['drugName'].tolist()

@app.route('/')
def home():
    return render_template('index.html')  # Render the frontend HTML

@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify([])

    # Remove duplicates by converting to a set and back to a list
    unique_disease_names = list(set(disease_names))

    # Find all unique disease names that start with the query
    suggestions = [name.title() for name in unique_disease_names if name.startswith(query)]
    
    return jsonify(suggestions[:10])


@app.route('/recommend', methods=['GET'])
def recommend():
    condition = request.args.get('condition', '').strip()
    if not condition:
        return jsonify({"error": "Condition is required"}), 400

    # Get drug recommendations based on the condition
    recommended_drugs = recommend_drug(condition)
    
    if isinstance(recommended_drugs, str):  # If there's an error message
        return jsonify({"error": recommended_drugs}), 404
    
    return jsonify({"condition": condition, "recommended_drugs": recommended_drugs})

if __name__ == '__main__':
    app.run(debug=True)
