from flask import Flask, request
from flask import render_template
import nlp
import kb
import psycopg2

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/get")
def get_bot_response():
    what_to_respond()
    response = kb.response
    # Reference from: https://pynative.com/python-postgresql-insert-update-delete-table-data-to-perform-crud-operations/
    try:
        userText = request.args.get('msg')
        conn = psycopg2.connect(database='ai', user='postgres', password='password', host='127.0.0.1', port='5432')
        cursor = conn.cursor()
        query = """INSERT INTO conversationdetails (user_input, response) VALUES (%s, %s) """
        data = (userText, response)
        cursor.execute(query, data)
        conn.commit()
        print("Insert data successfully")

    except (Exception, psycopg2.Error) as error:
        print("Failed executing query", error)
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Database connection close")
    return response

def what_to_respond():
    userText = request.args.get('msg')
    if userText in nlp.greeting_input:
        kb.process_entities('greeting')
    else:
        kb.response = ("Don't understand")

if __name__ == '__main__':
    app.run()
