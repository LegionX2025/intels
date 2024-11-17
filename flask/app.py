from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_paginate import Pagination, get_page_parameter
import json
import os
from math import ceil

app = Flask(__name__)

def load_darknet_data():
    """Loads and cleans Darknet data from a JSON file."""
    data = []
    if os.path.exists('static/Darknet_Data.json'):
        with open('static/Darknet_Data.json', 'r', encoding='utf-8') as file:
            for line in file:
                cleaned_line = clean_json_line(line)
                try:
                    data.append(json.loads(cleaned_line))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON line: {cleaned_line}, Error: {e}")
    return data

def clean_json_line(line):
    """Cleans malformed JSON lines."""
    line = line.strip()
    if line.endswith(','):
        line = line[:-1]
    if not line.startswith('{'):
        line = '{' + line
    if not line.endswith('}'):
        line = line + '}'
    return line

def filter_data(data, query):
    """Filters Darknet data based on the search query."""
    filtered_data = []

    if query is None or query.strip() == "":
        return []

    # Normalize the query to lowercase for case-insensitive search
    query = query.lower()

    # Search all fields (no filter logic)
    for entry in data:
        if (query in entry.get('Title', '').lower() or
            query in entry.get('Description', '').lower() or
            query in entry.get('Content', '').lower() or  # Added search for 'Content' field
            any(query in item.lower() for item in entry.get('Wallet Addresses', [])) or
            any(query in item.lower() for item in entry.get('Usernames', [])) or
            any(query in keyword.lower() for keyword in entry.get('Entities', {}).get('Keywords', []))):
            filtered_data.append(entry)

    return filtered_data



def get_search_results(query, entity_filter):
    """Retrieves search results based on the query from the Darknet data."""
    data = load_darknet_data()
    results = filter_data(data, query, entity_filter)
    return results

@app.route('/')
def index():
    """Renders the landing page."""
    return render_template('landing_page.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')  # Use GET to access the query
    page = request.args.get('page', 1, type=int)  # Get the page number from the query parameters
    results_per_page = 10  # Number of results per page

    # Perform the search
    data = load_darknet_data()  # Load the data from the JSON file
    search_results = filter_data(data, query)

    # Pagination logic
    total_results = len(search_results)
    total_pages = ceil(total_results / results_per_page)
    start = (page - 1) * results_per_page
    end = start + results_per_page
    paginated_results = search_results[start:end]

    pagination = Pagination(page=page, total=total_results, per_page=results_per_page, css_framework='bootstrap5')

    return render_template('search.html', results=paginated_results, query=query, pagination=pagination)


@app.route('/visualization', methods=['GET'])
def visualization():
    """Displays relationship graph of clicked entry."""
    entity = request.args.get('entity')

    if entity:
 W       entities = entity.split(',')
        nodes = []
        links = []
        entity_map = {}

        for i, entity in enumerate(entities):
            node = {'id': entity, 'group': 1 if 'email' in entity or 'wallet' in entity else 2}
            nodes.append(node)
            entity_map[entity] = i

        for src_entity in entities:
            for target_entity in entities:
                if src_entity != target_entity:
                    links.append({'source': entity_map[src_entity], 'target': entity_map[target_entity]})

        return render_template('visualization.html', nodes=nodes, links=links)

    return "No entity selected for visualization"



if __name__ == '__main__':
    app.run(debug=True)
