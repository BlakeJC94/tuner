from flask import Flask, render_template

app = Flask(__name__)


# Define pages
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload_instructions')
def upload_instructions():
    return "foo"
