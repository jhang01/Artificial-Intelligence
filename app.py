from flask import Flask, request
from flask import render_template
import nlp
import kb

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/get")
def get_bot_response():
    what_to_respond()
    response = kb.response
    return response

def what_to_respond():
    userText = request.args.get('msg')
    if userText in nlp.greeting_input:
        kb.process_entities('greeting')
    else:
        kb.response = ("Don't understand")


if __name__ == '__main__':
    app.run()
