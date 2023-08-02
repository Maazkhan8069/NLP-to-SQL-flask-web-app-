#"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"
#"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"
from flask import Flask, render_template, request, jsonify , send_from_directory
import openai
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text
import json
import traceback
import os


app = Flask(__name__, static_url_path='/static')

# Set up OpenAI API key
openai.api_key = "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"

# Prompt to define table structure for GPT

def create_table_definition_prompt(df):
    columns = ",".join(f"`{column}` TEXT" for column in df.columns)
    prompt = f"### sqlite SQL table, with its properties:\n\n# Data({columns})\n\n"
    return prompt

# Combine prompts for GPT

def combine_prompts(df, query_prompt):
    definition = create_table_definition_prompt(df)
    query_init_string = f"### A query to answer: {query_prompt}\nSELECT"
    return definition + query_init_string

# Handle GPT response

def handle_response(response):
    query = response["choices"][0]["text"]
    if query.startswith(" "):
        query = "SELECT" + query
    return query

# Flask route to render the HTML template

@app.route('/')
def index():
    return render_template('index.html')

# Flask route to handle NLP-to-SQL conversion

@app.route('/convert', methods=['POST'])
def convert_text_to_sql():
    try:
        # Retrieve the input data from the request
        nlp_text = request.form.get('text')
        csv_file = request.files.get('csv')

        if not csv_file:
            return jsonify({'error': 'No CSV file selected.'}), 400

        # Read the CSV file
        try:
            df = pd.read_csv(csv_file)
            print("DataFrame Contents:", df.head())  # Add this line to check the DataFrame

        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': 'Failed to read CSV file.'}), 400
        
        if df.empty:
            return jsonify({"error": "The DataFrame is empty."}), 400

        # Set up SQL database
        temp_db = create_engine('sqlite:///:memory:', echo=True)
        df.to_sql(name='Data', con=temp_db, index=False)

        # Set up GPT prompt
        prompt = combine_prompts(df, nlp_text)

        # Call OpenAI API to generate SQL query
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0,
            max_tokens=150,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["#", ";"]
        )

        # Convert GPT response to SQL query
        sql_query = handle_response(response)

        # Execute SQL query in the database
        with temp_db.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = result.fetchall()

        # Convert rows to list of dictionaries
        columns = result.keys()
        results = [dict(zip(columns, row)) for row in rows]

        # Return the SQL query and results as a JSON response
        return jsonify({'sql_query': sql_query, 'results': results})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An error occurred during the conversion process.'}), 500

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

