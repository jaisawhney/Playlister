from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

import os

# DB Setup
host = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/Playlister")
client = MongoClient(host=host)
db = client.Playlister

playlists = db.playlists
comments = db.comments

app = Flask(__name__)


def video_url_creator(id_lst):
    videos = []
    for vid_id in id_lst:
        video = f"https://youtube.com/embed/{vid_id}"
        videos.append(video)
    return videos


# Routes
@app.route("/")
def playlists_index():
    return render_template("playlists_index.html", playlists=playlists.find())


@app.route("/playlists/new")
def playlists_new():
    return render_template("playlists_new.html", playlist=None, title="New Playlist")


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
def playlist_show(playlist_id):
    playlist = playlists.find_one({"_id": ObjectId(playlist_id)})
    playlist_comments = comments.find({"playlist_id": playlist_id})
    return render_template("playlists_show.html", playlist=playlist, comments=playlist_comments)


@app.route("/playlists/<string:playlist_id>", methods=["POST"])
def update_playlist(playlist_id):
    video_ids = request.form.get("video_ids").split()

    updated_playlist = {
        "title": request.form.get("title"),
        "description": request.form.get("description"),
        "videos": video_url_creator(video_ids),
        "video_ids": video_ids
    }

    playlists.update_one(
        {"_id": ObjectId(playlist_id)},
        {"$set": updated_playlist})

    return redirect(url_for("playlist_show", playlist_id=playlist_id))


@app.route("/playlists/<string:playlist_id>/edit")
def edit_playlist(playlist_id):
    playlist = playlists.find_one({"_id": ObjectId(playlist_id)})
    return render_template("playlist_edit.html", playlist=playlist, title="Edit Playlist")


@app.route("/playlists/<string:playlist_id>/delete", methods=["POST"])
def delete_playlist(playlist_id):
    playlists.delete_one({"_id": ObjectId(playlist_id)})
    return redirect(url_for("playlists_index"))


@app.route("/playlists/comments", methods=["POST"])
def comments_new():
    comment = {
        "playlist_id": request.form.get("playlist_id"),
        "title": request.form.get("title"),
        "content": request.form.get("content")
    }
    comments.insert_one(comment)
    return redirect(url_for("playlist_show", playlist_id=request.form.get("playlist_id")))


@app.route("/playlists/comments/<string:comment_id>/delete", methods=["POST"])
def delete_comment(comment_id):
    comments.delete_one({"_id": ObjectId(comment_id)})
    return redirect(url_for("playlist_show", playlist_id=request.form.get("playlist_id")))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=os.environ.get("PORT", 5000))
