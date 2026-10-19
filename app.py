import os
from flask import Flask, redirect, url_for, session, request, send_from_directory
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from werkzeug.utils import secure_filename

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "pluto-wave-2024-super-secret")
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

CSS = """
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto}
body{background:#0a0a0a;color:white;min-height:100vh}
.nav{display:flex;justify-content:space-between;align-items:center;padding:20px 5%;background:#111;border-bottom:1px solid #222}
.logo{font-size:24px;font-weight:900;letter-spacing:2px} .logo span{color:#7c3aed}
.btn{padding:12px 24px;border-radius:30px;border:none;font-weight:700;cursor:pointer}
.btn-primary{background:white;color:black}
.btn-purple{background:#7c3aed;color:white;width:100%;padding:16px;font-size:16px;margin-top:10px}
.container{max-width:1100px;margin:0 auto;padding:30px 5%}
.hero{padding:60px 0;text-align:center}
.hero h1{font-size:55px;font-weight:900;line-height:1.1;margin-bottom:15px}
.hero p{color:#888;font-size:18px;margin-bottom:30px}
.card{background:#18181b;border:1px solid #27272a;border-radius:20px;padding:25px}
.upload-box{border:2px dashed #3f3f46;border-radius:20px;padding:50px 20px;text-align:center;background:#121214;cursor:pointer;transition:0.2s}
.upload-box:hover{border-color:#7c3aed;background:#1a1a1e}
.grid{display:grid;grid-template-columns:1fr 350px;gap:25px;margin-top:30px}
@media(max-width:800px){.grid{grid-template-columns:1fr} .hero h1{font-size:35px}}
.file-item{background:#27272a;padding:12px 16px;border-radius:12px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center}
.player{width:100%;margin-top:10px}
</style>
"""

def get_files():
    files=[]
    if os.path.exists(UPLOAD_FOLDER):
        for f in os.listdir(UPLOAD_FOLDER):
            if not f.startswith('.'):
                files.append(f)
    return files[::-1]

@app.route('/')
def home():
    if 'user' in session:
        return redirect('/dashboard')
    return f"""
    <html><head><meta name="viewport" content="width=device-width,initial-scale=1">{CSS}</head>
    <body>
      <div class="nav"><div class="logo">PLUTO <span>WAVE</span></div><a href="/auth/google"><button class="btn btn-primary">Login with Google</button></a></div>
      <div class="container">
        <div class="hero">
          <h1>UPLOAD.<br>EDIT. <span style="color:#7c3aed">WAVE.</span></h1>
          <p>The next-gen audio platform for creators. Fast, clean, pro.</p>
          <a href="/auth/google"><button class="btn btn-primary" style="padding:18px 40px;font-size:18px">Start Creating Free →</button></a>
        </div>
        <div class="card"><h3>🎵 What you get</h3><br><p style="color:#aaa">• One-click Google login<br>• Drag & drop upload<br>• Built-in player & editing<br>• Shareable link</p></div>
      </div>
    </body></html>
    """

@app.route('/auth/google')
def auth_google():
    redirect_uri=url_for('auth_callback',_external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_callback():
    token=google.authorize_access_token()
    user_info=token.get('userinfo')
    if user_info:
        session['user']=user_info
    return redirect('/dashboard')

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    user=session.get('user')
    if not user:
        return redirect('/')
    email=user.get('email','User')
    name=user.get('name','Creator')
    msg=""
    if request.method=='POST':
        f=request.files.get('file')
        if f and f.filename:
            filename=secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            msg=f"<div style='background:#15803d;padding:12px;border-radius:10px;margin-bottom:15px'>✅ Uploaded <b>{filename}</b> successfully!</div>"
    
    files=get_files()
    files_html=""
    for fn in files:
        files_html+=f"""
        <div class="file-item">
          <div><b>{fn}</b><br><small style="color:#888">{fn.split('.')[-1].upper()} file</small></div>
          <audio controls class="player" style="width:140px"><source src="/uploads/{fn}"></audio>
        </div>
        """

    if not files_html:
        files_html="<p style='color:#666;text-align:center;padding:20px'>No uploads yet. Upload your first track!</p>"

    return f"""
    <html><head><meta name="viewport" content="width=device-width,initial-scale=1">{CSS}</head>
    <body>
      <div class="nav"><div class="logo">PLUTO <span>WAVE</span></div><div style="display:flex;gap:15px;align-items:center"><small style="color:#aaa">{email}</small><a href="/logout" style="color:#888;text-decoration:none">Logout</a></div></div>
      <div class="container">
        <h2 style="font-size:28px;margin-bottom:5px">Welcome back, {name} 👋</h2>
        <p style="color:#777;margin-bottom:25px">Ready to make some wave?</p>
        {msg}
        <div class="grid">
          <div>
            <div class="card">
              <h3 style="margin-bottom:15px">Upload Track</h3>
              <form method="post" enctype="multipart/form-data" id="uploadForm">
                <label for="fileInput"><div class="upload-box"><div style="font-size:40px">☁️</div><h3>Drop audio here or click to browse</h3><p style="color:#777;margin-top:8px">MP3, WAV, MP4, M4A up to 100MB</p></div></label>
                <input type="file" name="file" id="fileInput" hidden required onchange="document.getElementById('uploadForm').submit()">
                <div id="fileName" style="margin-top:15px;color:#7c3aed;font-weight:600"></div>
              </form>
              <div style="margin-top:25px;display:grid;grid-template-columns:1fr 1fr;gap:10px">
                <input placeholder="Track Title" style="padding:12px;background:#27272a;border:1px solid #3f3f46;border-radius:10px;color:white">
                <input placeholder="Artist Name" style="padding:12px;background:#27272a;border:1px solid #3f3f46;border-radius:10px;color:white">
              </div>
              <button class="btn btn-purple">✨ Edit & Enhance</button>
            </div>
          </div>
          <div>
            <div class="card"><h3 style="margin-bottom:15px">Your Waves 🌊 ({len(files)})</h3>{files_html}</div>
            <div class="card" style="margin-top:15px;background:linear-gradient(135deg,#7c3aed,#4f46e5)"><h3>Pro Tip 💡</h3><p style="margin-top:8px;font-size:14px;opacity:0.9">After upload, you can trim, add cover art, and get shareable link. Coming next!</p></div>
          </div>
        </div>
      </div>
      <script>document.getElementById('fileInput').addEventListener('change',e=>{{document.getElementById('fileName').innerText='Selected: '+e.target.files[0].name}})</script>
    </body></html>
    """

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
