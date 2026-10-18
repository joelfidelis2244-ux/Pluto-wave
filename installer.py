import os
os.makedirs('static/music', exist_ok=True)
os.makedirs('static/covers', exist_ok=True)
os.makedirs('templates', exist_ok=True)

app_code = '''
from flask import Flask, render_template, request, redirect, session
import os, sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = 'pluto_wave_secret_2026'
def init_db():
    conn = sqlite3.connect('pluto.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT)")
    conn.commit(); conn.close()
init_db()
playlists = [{"id":1, "name":"Pluto Hits", "desc":"Hottest waves"}, {"id":2, "name":"Street Anthems", "desc":"For the street"}, {"id":3, "name":"Chill Vibes", "desc":"Late night mood"}]
artists = [{"id":1, "name":"Pluto Wave"}, {"id":2, "name":"Wizzy Pluto"}, {"id":3, "name":"Young Blaze"}]
songs = [{"id":1, "title":"For The Wave", "artist":"Pluto Wave", "file":"song1.mp3"}, {"id":2, "title":"No Leaking", "artist":"Wizzy Pluto", "file":"song2.mp3"}]
def login_required(f):
    def wrap(*a, **k):
        if 'user' not in session: return redirect('/login')
        return f(*a, **k)
    wrap.__name__=f.__name__
    return wrap
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        email=request.form['email'].strip().lower(); password=request.form['password']
        if not email.endswith('@gmail.com'): return render_template('signup.html', error='Use Gmail only!')
        try:
            conn=sqlite3.connect('pluto.db'); c=conn.cursor()
            c.execute("INSERT INTO users (email,password) VALUES (?,?)", (email, generate_password_hash(password)))
            conn.commit(); conn.close(); session['user']=email; return redirect('/')
        except: return render_template('signup.html', error='Gmail already exists!')
    return render_template('signup.html')
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['email'].strip().lower(); password=request.form['password']
        conn=sqlite3.connect('pluto.db'); c=conn.cursor(); c.execute("SELECT * FROM users WHERE email=?", (email,)); user=c.fetchone(); conn.close()
        if user and check_password_hash(user[2], password): session['user']=email; return redirect('/')
        else: return render_template('login.html', error='Wrong Gmail or password!')
    return render_template('login.html')
@app.route('/logout')
def logout(): session.pop('user',None); return redirect('/login')
@app.route('/')
@login_required
def home(): return render_template('index.html', playlists=playlists, artists=artists, songs=songs, page='home', user=session['user'])
@app.route('/search')
@login_required
def search():
    q=request.args.get('q','').lower(); result=[s for s in songs if q in s['title'].lower() or q in s['artist'].lower()] if q else songs
    return render_template('search.html', songs=result, page='search', user=session['user'])
@app.route('/library')
@login_required
def library(): return render_template('library.html', playlists=playlists, songs=songs, page='library', user=session['user'])
@app.route('/artist/<int:artist_id>')
@login_required
def artist_page(artist_id):
    artist=next((a for a in artists if a['id']==artist_id), artists[0]); artist_songs=[s for s in songs if s['artist']==artist['name']]
    return render_template('artist.html', artist=artist, songs=artist_songs, user=session['user'])
@app.route('/playlist/<int:pid>')
@login_required
def playlist_page(pid):
    pl=next((p for p in playlists if p['id']==pid), playlists[0])
    return render_template('playlist.html', playlist=pl, songs=songs, user=session['user'])
@app.route('/upload', methods=['GET','POST'])
@login_required
def upload():
    global songs
    if request.method=='POST':
        title=request.form['title']; artist=request.form['artist']
        file=request.files.get('music'); cover=request.files.get('cover')
        filename=file.filename if file and file.filename else 'song1.mp3'
        covername=cover.filename if cover and cover.filename else 'cover1.jpg'
        if file and file.filename: file.save(os.path.join('static/music', filename))
        if cover and cover.filename: cover.save(os.path.join('static/covers', covername))
        songs.append({"id":len(songs)+1,"title":title,"artist":artist,"file":filename}); return redirect('/')
    return render_template('upload.html', user=session['user'])
if __name__=='__main__': app.run(host='0.0.0.0', port=5000, debug=True)
'''
open('app.py','w').write(app_code)
print("app.py created")
