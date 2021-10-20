from flask import Flask, render_template
from pymongo import MongoClient

# DB Setup
client = MongoClient()
db = client.Playlister
playlists = db.playlists

app = Flask(__name__)


# Routes
@app.route('/')
def playlists_index():
    return render_template('playlists_index.html', playlists=playlists.find())


if __name__ == "__main__":
    app.run(debug=True)
