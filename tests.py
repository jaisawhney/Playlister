from unittest import TestCase, main as unittest_main, mock
from bson.objectid import ObjectId
from app import app, video_url_creator

sample_id_list = ["hY7m5jjJ9mM", "CQ85sUNBK7w"]

sample_playlist_id = ObjectId("5d55cffc4a3d4031f42827a3")
sample_playlist = {
    "title": "Cat Videos",
    "description": "Cats acting weird",
    "videos": [
        "https://youtube.com/embed/hY7m5jjJ9mM",
        "https://youtube.com/embed/CQ85sUNBK7w"
    ],
    "video_ids": ["hY7m5jjJ9mM", "CQ85sUNBK7w"]
}
sample_form_data = {
    "title": sample_playlist["title"],
    "description": sample_playlist["description"],
    "video_ids": "\n".join(sample_playlist["video_ids"])
}


class PlaylistsTests(TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True

    def test_index(self):
        result = self.client.get("/")
        self.assertEqual(result.status, "200 OK")

        page_content = result.get_data(as_text=True)
        self.assertIn("Playlist", page_content)

    def test_new(self):
        result = self.client.get("/playlists/new")
        self.assertEqual(result.status, "200 OK")

        page_content = result.get_data(as_text=True)
        self.assertIn("New Playlist", page_content)

    def test_video_url_creator(self):
        expected_list = ["https://youtube.com/embed/hY7m5jjJ9mM", "https://youtube.com/embed/CQ85sUNBK7w"]
        output_list = video_url_creator(sample_id_list)
        self.assertEqual(expected_list, output_list)

    @mock.patch("pymongo.collection.Collection.find_one")
    def test_show_playlist(self, mock_find):
        mock_find.return_value = sample_playlist

        result = self.client.get(f"/playlists/{sample_playlist_id}")
        self.assertEqual(result.status, "200 OK")

        page_content = result.get_data(as_text=True)
        self.assertIn("Cat Videos", page_content)

    @mock.patch("pymongo.collection.Collection.insert_one")
    def test_submit_playlist(self, mock_insert):
        result = self.client.post("/playlists", data=sample_form_data)

        self.assertEqual(result.status, "302 FOUND")
        mock_insert.assert_called_with(sample_playlist)

    @mock.patch("pymongo.collection.Collection.update_one")
    def test_update_playlist(self, mock_update):
        result = self.client.post(f"/playlists/{sample_playlist_id}", data=sample_form_data)

        self.assertEqual(result.status, "302 FOUND")
        mock_update.assert_called_with({"_id": sample_playlist_id}, {"$set": sample_playlist})

    @mock.patch("pymongo.collection.Collection.delete_one")
    def test_delete_playlist(self, mock_delete):
        form_data = {"_method": "DELETE"}
        result = self.client.post(f"/playlists/{sample_playlist_id}/delete", data=form_data)
        self.assertEqual(result.status, "302 FOUND")
        mock_delete.assert_called_with({"_id": sample_playlist_id})


if __name__ == "__main__":
    unittest_main()
