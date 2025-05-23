from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'The Bot is running.... Hosted by Darkboy'


if __name__ == "__main__":
    app.run()
