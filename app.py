from flask import Flask, request
from flask import render_template
import nlp

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    
    return userText
    

if __name__ == '__main__':
    app.run()