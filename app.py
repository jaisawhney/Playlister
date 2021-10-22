from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

# DB Setup
client = MongoClient()
db = client.Playlister
playlists = db.playlists

app = Flask(__name__)


def video_url_creator(id_lst):
    videos = []
    for vid_id in id_lst:
        video = "https://youtube.com/embed/" + vid_id
        videos.append(video)
    return videos


# Routes
@app.route("/")
def playlists_index():
    return render_template("playlists_index.html", playlists=playlists.find())


@app.route("/playlists/new")
def playlists_new():
    return render_template("playlists_new.html")


@app.route("/playlists", methods=["POST"])
def playlists_submit():
    video_ids = request.form.get("video_ids").split()
    videos = video_url_creator(video_ids)
    playlist = {
        "title": request.form.get("title"),
        "description": request.form.get("description"),
        "videos": videos,
        "video_ids": video_ids
    }
    playlists.insert_one(playlist)
    return redirect(url_for("playlists_index"))


@app.route("/playlists/<string:playlist_id>")
def playlist(playlist_id):
    playlist = playlists.find_one({"_id": ObjectId(playlist_id)})
    return render_template("playlists_show.html", playlist=playlist)


if __name__ == "__main__":
    app.run(debug=True)
