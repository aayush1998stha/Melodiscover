import pytest
from app import app, db, Playlist, ListeningHistory

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_index_returns_200(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Melodiscover' in response.data

def test_play_song_returns_json(client):
    response = client.get('/play/1')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id'] == '1'
    assert 'title' in json_data

def test_create_playlist(client):
    response = client.post('/playlist/create', data={'name': 'My Faves'}, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        playlist = Playlist.query.filter_by(name='My Faves').first()
        assert playlist is not None
        assert playlist.name == 'My Faves'

def test_add_song_to_playlist(client):
    client.post('/playlist/create', data={'name': 'Test Playlist'})
    with app.app_context():
        playlist = Playlist.query.filter_by(name='Test Playlist').first()
        playlist_id = playlist.id
    response = client.post(f'/playlist/{playlist_id}/add', data={'song_id': '1'}, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        updated_playlist = Playlist.query.get(playlist_id)
        assert len(updated_playlist.songs) == 1
        assert updated_playlist.songs[0].song_id == '1'

def test_play_logs_history(client):
    client.get('/play/1')
    with app.app_context():
        history = ListeningHistory.query.all()
        assert len(history) == 1
        assert history[0].song_id == '1'

def test_stats_page_returns_200(client):
    client.get('/play/1')
    client.get('/play/2')
    response = client.get('/stats')
    assert response.status_code == 200
    assert b'Listening Statistics' in response.data