from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import json
import random
from datetime import datetime

# ------------------------------
# APP INITIALISATION
# ------------------------------
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ------------------------------
# DATABASE MODELS
# ------------------------------
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    songs = db.relationship('PlaylistSong', backref='playlist', lazy=True, cascade='all, delete-orphan')

class PlaylistSong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    song_id = db.Column(db.String(50), nullable=False)
    song_title = db.Column(db.String(200), nullable=False)
    song_artist = db.Column(db.String(200), nullable=False)
    song_genre = db.Column(db.String(100), nullable=False)
    song_album_art = db.Column(db.String(500), nullable=True)

class ListeningHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.String(50), nullable=False)
    song_title = db.Column(db.String(200), nullable=False)
    song_artist = db.Column(db.String(200), nullable=False)
    song_genre = db.Column(db.String(100), nullable=False)
    listened_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables automatically
with app.app_context():
    db.create_all()

# ------------------------------
# SAMPLE SONG DATA
# ------------------------------
SONGS = [
    {"id": "1", "title": "Blinding Lights", "artist": "The Weeknd", "genre": "Pop", "album_art": "https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36"},
    {"id": "2", "title": "Levitating", "artist": "Dua Lipa", "genre": "Pop", "album_art": "https://i.scdn.co/image/ab67616d0000b2737fcead687e99558f9d4b3e2b"},
    {"id": "3", "title": "Save Your Tears", "artist": "The Weeknd", "genre": "Pop", "album_art": "https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36"},
    {"id": "4", "title": "Peaches", "artist": "Justin Bieber", "genre": "Pop", "album_art": "https://i.scdn.co/image/ab67616d0000b2739b9e7c9f6f4e8f3b5c7e5d4a"},
    {"id": "5", "title": "Montero", "artist": "Lil Nas X", "genre": "Hip-Hop", "album_art": "https://i.scdn.co/image/ab67616d0000b2733f2b5c2f4e8d6a7b8c9d0e1f"},
    {"id": "6", "title": "Good 4 U", "artist": "Olivia Rodrigo", "genre": "Rock", "album_art": "https://i.scdn.co/image/ab67616d0000b2731f2b3c4d5e6f7a8b9c0d1e2f"},
    {"id": "7", "title": "Kiss Me More", "artist": "Doja Cat", "genre": "R&B", "album_art": "https://i.scdn.co/image/ab67616d0000b2732a3b4c5d6e7f8a9b0c1d2e3f"},
    {"id": "8", "title": "Industry Baby", "artist": "Lil Nas X", "genre": "Hip-Hop", "album_art": "https://i.scdn.co/image/ab67616d0000b2733b4c5d6e7f8a9b0c1d2e3f4a"},
    {"id": "9", "title": "Stay", "artist": "The Kid LAROI", "genre": "Pop", "album_art": "https://i.scdn.co/image/ab67616d0000b2734c5d6e7f8a9b0c1d2e3f4a5b"},
    {"id": "10", "title": "Butter", "artist": "BTS", "genre": "Pop", "album_art": "https://i.scdn.co/image/ab67616d0000b2735d6e7f8a9b0c1d2e3f4a5b6c"},
    {"id": "11", "title": "Bad Habits", "artist": "Ed Sheeran", "genre": "Pop", "album_art": "https://i.scdn.co/image/ab67616d0000b2736e7f8a9b0c1d2e3f4a5b6c7d"},
    {"id": "12", "title": "Permission to Dance", "artist": "BTS", "genre": "Pop", "album_art": "https://i.scdn.co/image/ab67616d0000b2737f8a9b0c1d2e3f4a5b6c7d8e"},
]

PREVIEW_URLS = [
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
]

def get_song_by_id(song_id):
    for song in SONGS:
        if song["id"] == song_id:
            return song
    return None

def get_random_preview_url():
    return random.choice(PREVIEW_URLS)

# ------------------------------
# V1.0 - BROWSE & PLAY
# ------------------------------
@app.route('/')
def index():
    search_query = request.args.get('q', '').strip().lower()
    if search_query:
        filtered_songs = [s for s in SONGS if search_query in s['title'].lower() or search_query in s['artist'].lower()]
    else:
        filtered_songs = SONGS
    for song in filtered_songs:
        song['preview_url'] = get_random_preview_url()
    return render_template('index.html', songs=filtered_songs, search_query=search_query)

@app.route('/play/<song_id>')
def play_song(song_id):
    song = get_song_by_id(song_id)
    if not song:
        return jsonify({"error": "Song not found"}), 404
    # Log to history for V3.0 recommendations
    history_entry = ListeningHistory(
        song_id=song['id'],
        song_title=song['title'],
        song_artist=song['artist'],
        song_genre=song['genre']
    )
    db.session.add(history_entry)
    db.session.commit()
    return jsonify({
        "id": song['id'],
        "title": song['title'],
        "artist": song['artist'],
        "preview_url": get_random_preview_url()
    })

# ------------------------------
# V2.0 - PLAYLIST CRUD
# ------------------------------
@app.route('/playlists')
def list_playlists():
    playlists = Playlist.query.all()
    return render_template('playlist.html', playlists=playlists)

@app.route('/playlist/create', methods=['POST'])
def create_playlist():
    name = request.form.get('name', '').strip()
    if name:
        playlist = Playlist(name=name)
        db.session.add(playlist)
        db.session.commit()
    return redirect(url_for('list_playlists'))

@app.route('/playlist/<int:playlist_id>')
def view_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    return render_template('playlist_detail.html', playlist=playlist, songs=SONGS)

@app.route('/playlist/<int:playlist_id>/add', methods=['POST'])
def add_to_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    song_id = request.form.get('song_id')
    song = get_song_by_id(song_id)
    if song:
        existing = PlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song_id).first()
        if not existing:
            ps = PlaylistSong(
                playlist_id=playlist_id,
                song_id=song['id'],
                song_title=song['title'],
                song_artist=song['artist'],
                song_genre=song['genre'],
                song_album_art=song.get('album_art', '')
            )
            db.session.add(ps)
            db.session.commit()
    return redirect(url_for('view_playlist', playlist_id=playlist_id))

@app.route('/playlist/<int:playlist_id>/remove/<int:ps_id>')
def remove_from_playlist(playlist_id, ps_id):
    ps = PlaylistSong.query.get_or_404(ps_id)
    db.session.delete(ps)
    db.session.commit()
    return redirect(url_for('view_playlist', playlist_id=playlist_id))

@app.route('/playlist/<int:playlist_id>/delete')
def delete_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    db.session.delete(playlist)
    db.session.commit()
    return redirect(url_for('list_playlists'))

# ------------------------------
# V3.0 - RECOMMENDATIONS & STATS
# ------------------------------
@app.route('/recommendations')
def recommendations():
    history = ListeningHistory.query.all()
    if not history:
        return render_template('recommendations.html', recommendations=[], has_history=False)
    
    genre_counts = {}
    for entry in history:
        genre_counts[entry.song_genre] = genre_counts.get(entry.song_genre, 0) + 1
    
    if genre_counts:
        top_genre = max(genre_counts, key=genre_counts.get)
        listened_ids = [h.song_id for h in history]
        recommendations_list = [s for s in SONGS if s['genre'] == top_genre and s['id'] not in listened_ids]
        if len(recommendations_list) < 3:
            additional = [s for s in SONGS if s['id'] not in listened_ids and s not in recommendations_list]
            recommendations_list.extend(additional[:3-len(recommendations_list)])
    else:
        recommendations_list = random.sample(SONGS, min(5, len(SONGS)))
    
    for song in recommendations_list:
        song['preview_url'] = get_random_preview_url()
    return render_template('recommendations.html', recommendations=recommendations_list, has_history=True)

@app.route('/stats')
def stats():
    history = ListeningHistory.query.all()
    total_plays = len(history)
    genre_counts = {}
    artist_counts = {}
    for entry in history:
        genre_counts[entry.song_genre] = genre_counts.get(entry.song_genre, 0) + 1
        artist_counts[entry.song_artist] = artist_counts.get(entry.song_artist, 0) + 1
    
    top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return render_template(
        'stats.html',
        total_plays=total_plays,
        top_genres=top_genres,
        top_artists=top_artists,
        genre_labels=json.dumps([g[0] for g in top_genres]),
        genre_data=json.dumps([g[1] for g in top_genres]),
        artist_labels=json.dumps([a[0] for a in top_artists]),
        artist_data=json.dumps([a[1] for a in top_artists])
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
