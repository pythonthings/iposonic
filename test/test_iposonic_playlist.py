from __future__ import unicode_literals

from iposonicdb import SqliteIposonicDB
from harnesses import harn_setup, harn_load_fs2
from test_iposonic import tmp_dir
from mediamanager import MediaManager
from iposonic import EntryNotFoundException


class TestPlaylistIposonicDB:
    dbhandler = SqliteIposonicDB
    # Harness
    id_songs = []
    id_artists = []
    id_albums = []

    def setup_playlist(self):
        item = self.db.Playlist("mock_playlist")
        songs = ",".join([str(x.get('id')) for x in self.db.get_songs()])
        item.update({'entry': songs})

        session = self.db.Session()
        session.add(item)
        session.commit()
        session.close()

    def setup(self):
        harn_setup(self, "/test/data")
        harn_load_fs2(self)

        self.setup_playlist()

    def test_get_playlists(self):
        items = self.db.get_playlists()
        item = items[0]
        assert item.get('name') == 'mock_playlist', "No playlists: %s" % item

    def test_get_playlist(self):
        eid = MediaManager.uuid('mock_playlist')
        ret = self.db.get_playlists(eid=eid)
        assert ret, "Can't find playlist %s" % eid
        assert ret.get('name') == 'mock_playlist', "No playlists: %s" % ret


class TestUserIposonicDB:
    dbhandler = SqliteIposonicDB
    # Harness
    id_songs = []
    id_artists = []
    id_albums = []

    def setup_user(self):
        session = self.db.Session()
        print ("setting up users...")
        for unames in ["mock_user%s" % s for s in ['', 1, 2, 3]]:
            item = self.db.User(unames)
            item.update({
                'password': 'mock_password',
                'scrobbleUser': 'ioggstream',
                'scrobblePassword': 'secret'
            })
            print ("setting up user...%s"% item)

            session.add(item)
        session.commit()
        session.close()

    def setup(self):
        harn_setup(self, tmp_dir, add_songs=False)
        self.setup_user()

    def test_get_users(self):
        items = self.db.get_users()
        print  items
        item = items[0]
        assert item.get('username') == 'mock_user', "No users: %s" % item

    def test_add_remove_user(self):
        u = {
            'username': 'mock_user',
            'password': 'mock_password',
            'scrobbleUser': 'ioggstream',
            'scrobblePassword': 'secret'
        }
        eid = self.db.add_user(u)
        assert eid, "Item not working"
        print ("retrieving item with id: %s" % eid)
        t = self.db.get_users(eid=eid)
        assert 'username' in t, "Created %s" % t

        self.db.delete_user(eid=eid)
        try:
            t = self.db.get_users(eid=eid)
            assert False, "can't find user"
        except EntryNotFoundException:
            pass

    def test_get_user(self):
        from mediamanager import MediaManager
        eid = MediaManager.uuid('mock_user')
        ret = self.db.get_users(eid)
        assert ret, "Can't find user %s" % eid
        assert ret.get('username') == 'mock_user', "No user: %s" % ret
