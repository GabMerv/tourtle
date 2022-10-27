import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, send_from_directory
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

import os
from os.path import exists

from flask_login import login_required, current_user, login_user, logout_user

from models import UserModel, db, load_user, login

import random

def get_db_connection():
    conn = sqlite3.connect('datas.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
app.secret_key = "Tourtle4Ever"

app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login.init_app(app)
login.login_view = 'login'



db.init_app(app)
@app.before_first_request
def create_table():
    db.create_all()

def get_message(message_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM messages WHERE id = ?',
                        (message_id,)).fetchone()
    conn.close()
    return post

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
     
    if request.method == 'POST':
        email = request.form['email']
        user = UserModel.query.filter_by(email = email).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/')
        else:
            return render_template("login.html", message="Mot de passe ou utilisateur incorrect")
     
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
     
    if request.method == 'POST':
        admin = 0
        email = request.form['email']
        if email == "gabrielmerville@gmail.com":
            admin = 1
        username = request.form['username']
        password = request.form['password']
 
        if UserModel.query.filter_by(email=email).first():
            return render_template('register.html', message="Le compte existe déjà")
             
        user = UserModel(email=email, username=username, spes="", description="", classe="", parcours="", q_a="", pp="", follow="", messages="", admin=admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/<int:id>/delete_user', methods=['POST', 'GET'])
def delete_user(id):
    if current_user.admin == True or current_user.id == id:
        user = load_user(id)
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/admin.html', methods=('GET', 'POST'))
@login_required
def admin():
    if current_user.admin == 1:
        return render_template("admin.html")
    else:
        redirect(url_for('index'))


@app.route('/', methods=('GET', 'POST'))
@login_required
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM blog').fetchall()
    conn.close()
    return render_template('index.html', posts=posts[::-1])

@app.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    users = UserModel.query.all()
    conn = get_db_connection()
    blogs = conn.execute('SELECT * FROM blog').fetchall()
    events = conn.execute('SELECT * FROM calendar').fetchall()
    dsts = conn.execute('SELECT * FROM dst').fetchall()
    conn.close()
    return render_template('search.html', users=users, blogs=blogs, events=events, dsts=dsts)

@app.route('/livres', methods=('GET', 'POST'))
@login_required
def livres():
    return render_template('livres.html')

@app.route('/<int:id>/userInfos', methods=('GET', 'POST'))
@login_required
def userInfos(id):
    user = load_user(id)
    return render_template('userInfos.html', user=user)

@app.route('/<int:id>/modify_user', methods=('GET', 'POST'))
@login_required
def modifyUser(id):
    user = load_user(current_user.id)
    conn = get_db_connection()
    follow = conn.execute('SELECT * FROM follow').fetchall()
    conn.close()
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        spes = request.form['spes']
        description = request.form['description']
        classe = request.form['classe']
        parcours = request.form['parcours']
        q_a = request.form['q_a']
        files = request.files.getlist('file')
        images = []
        for f in files:
            try:
                path = "static/images/" + secure_filename(f.filename)
                f.save(path)
                images.append(path)
                os.remove(user.pp)
            except:
                pp = user.pp
        if images:
            pp = ' '.join(images)
        fo = []
        for f in follow:
            name = list(f)[2]
            try:
                follow = request.form[name]
                fo.append(name)
            except:
                pass
        user.email = email
        user.username = username
        user.spes = spes
        user.description = description
        user.classe = classe
        user.parcours = parcours
        user.q_a = q_a
        user.pp = pp
        user.follow = " ".join(fo)
        
        if password:
            user.set_password(password)
        db.session.commit()
        return redirect(url_for('userInfos', id=current_user.id))
    return render_template('modify_user.html', user=user, follow=follow)

@app.route('/dst', methods=('GET', 'POST'))
@login_required
def dst():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM dst').fetchall()
    conn.close()
    return render_template('dst.html', posts=posts[::-1])

@app.route('/calendar', methods=('GET', 'POST'))
@login_required
def calendar():
    print("CALENDAR")
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM calendar').fetchall()
    conn.close()
    suscribers = []
    for p in posts:
        p = list(p)
        u = [load_user(int(i)).username for i in p[6].split(' ') if i.isdigit()]
        print(u)
        suscribers.append(u)
    return render_template('calendar.html', posts=posts[::-1], suscribers=suscribers[::-1])

@app.route('/add_event', methods=('GET', 'POST'))
@login_required
def add_event():
    conn = get_db_connection()
    follow = conn.execute('SELECT * FROM follow').fetchall()
    conn.close()
    if request.method == 'POST':
        title = request.form["title"]
        dates = request.form["dates"]
        description = request.form["description"]
        creator_id = current_user.id
        fo = []
        for f in follow:
            name = list(f)[2]
            try:
                follow = request.form[name]
                fo.append(name)
            except:
                pass
        types = ' '.join(fo)
        conn = get_db_connection()
        conn.execute('INSERT INTO calendar (title, dates, description_, types, creator_id, creator_name, participants) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (title, dates, description, types, creator_id, current_user.username, ""))
        conn.commit()
        conn.close()

        return redirect(url_for('calendar'))
    return render_template('add_event.html', follow=follow)

@app.route('/<int:id>/suscribe', methods=('GET', 'POST'))
@login_required
def suscribe(id):
    conn = get_db_connection()
    cal = list(conn.execute('SELECT * FROM calendar WHERE id = ?', (id,)).fetchall()[0])
    part = cal[6].split(" ")
    part.append(str(current_user.id))
    part = " ".join(part)
    conn.execute('UPDATE calendar SET participants = ? WHERE id = ?', (part, id,))
    conn.commit()
    conn.close()
    return redirect(url_for('calendar'))

@app.route('/<int:id>/unsuscribe', methods=('GET', 'POST'))
@login_required
def unsuscribe(id):
    conn = get_db_connection()
    cal = list(conn.execute('SELECT * FROM calendar WHERE id = ?', (id,)).fetchall()[0])
    part = cal[6].split(" ")
    del part[part.index(str(current_user.id))]
    part = " ".join(part)
    conn.execute('UPDATE calendar SET participants = ? WHERE id = ?', (part, id,))
    conn.commit()
    conn.close()
    return redirect(url_for('calendar'))

@app.route('/<int:id>/delete_event', methods=('GET', 'POST'))
@login_required
def delete_event(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM calendar WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('calendar'))

@app.route('/add_dst', methods=('GET', 'POST'))
@login_required
def add():
    if request.method == 'POST':
        files = request.files.getlist('file')
        images = []
        for f in files:
            title = request.form['title']
            path = "static/images/" + secure_filename(f.filename)
            while exists(path):
                path = path.split(".")
                path[0] += str(random.randint(0, 9))
                path = ".".join(path)
            f.save(path)
            images.append(path)
        images = '.'.join(images)
        conn = get_db_connection()
        conn.execute('INSERT INTO dst (title, images) VALUES (?, ?)',
                     (title, images))
        conn.commit()
        posts = conn.execute('SELECT * FROM dst').fetchall()
        conn.close()
        return redirect(url_for('dst'))


    return render_template('add_dst.html')

@app.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    conn = get_db_connection()
    dst = conn.execute('SELECT * FROM dst WHERE id = ?', (id,)).fetchall()
    conn.execute('DELETE FROM dst WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    for ds in list(dst[0])[3].split(' '):
        os.remove(ds)
    return redirect(url_for('dst'))

@app.route('/write_blog', methods=('GET', 'POST'))
@login_required
def write_blog():
    post_type = "ARTICLE"
    conn = get_db_connection()
    follow = conn.execute('SELECT * FROM follow').fetchall()
    conn.close()
    if request.method == 'POST':
        try:
            title = request.form['title']
            content = request.form['content']
        except:
            post_type = "IMAGE"
        images = []
        try:
            files = request.files.getlist('file')
            fo = []
            for f in follow:
                name = list(f)[2]
                try:
                    follow = request.form[name]
                    fo.append(name)
                except:
                    pass
            types = ' '.join(fo)
            for f in files:
                    path = "static/images/" + secure_filename(f.filename)
                    while exists(path):
                        path = path.split(".")
                        path[0] += str(random.randint(0, 9))
                        path = ".".join(path)
                    f.save(path)
                    images.append(path)
            images = '.'.join(images)
        except:
            post_type = "VIDEO"
        if images.split(' ') == [""]:
            post_type = "VIDEO"
        conn = get_db_connection()
        if post_type == "ARTICLE":
            conn.execute('INSERT INTO blog (title, content, images, author_id, author_name, types, link) VALUES (?, ?, ?, ?, ?, ?, ?)',
                         (title, content, images, current_user.id, current_user.username, types, ""))
        elif post_type == "IMAGE":
            conn.execute('INSERT INTO blog (title, content, images, author_id, author_name, types, link) VALUES (?, ?, ?, ?, ?, ?, ?)',
                         ("", "", images, current_user.id, current_user.username, types, ""))
        else:
            link = request.form['link']
            if "youtu.be" in link:
                code = link.split('/')[-1]
                link = "https://www.youtube.com/embed/{}?autoplay=0&mute=0".format(code)
            elif "youtube" in link:
                link = link.split("watch?v=")
                link = "embed/".join(link)
                link += "?autoplay=0&mute=0"

            conn.execute('INSERT INTO blog (title, content, images, author_id, author_name, types, link) VALUES (?, ?, ?, ?, ?, ?, ?)',
                         ("", "", "", current_user.id, current_user.username, types, link))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))


    return render_template('write_blog.html', follow=follow)

@app.route('/<int:id>/delete_blog', methods=('POST',))
@login_required
def delete_blog(id):
    conn = get_db_connection()
    blog = conn.execute('SELECT * FROM blog WHERE id = ?', (id,)).fetchall()
    conn.execute('DELETE FROM blog WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    for image in list(blog[0])[4].split(' '):
        try:
            os.remove(image)
        except:
            pass
    return redirect(url_for('index'))

@app.route('/messages', methods=('GET', 'POST'))
@login_required
def messages():
    users = []
    utilisateurs = UserModel.query.all()
    if current_user.messages.split(" ")[0]:
        messages = [get_message(id) for id in current_user.messages.split(" ")]
    else:
        messages = []
    conversations = []
    ids = [current_user.id]
    for message in messages[::-1]:
        if message[2] not in ids:
            users.append(load_user(message[2]).pp)
            ids.append(message[2])
            conversations.append(message)
        if message[3] not in ids:
            users.append(load_user(message[3]).pp)
            ids.append(message[3])
            conversations.append(message)
    return render_template('messages.html', conversations=conversations, users=users, utilisateurs=utilisateurs)

@app.route('/<int:id>/send', methods=('GET', 'POST'))
@login_required
def send(id):
    receiver = UserModel.query.filter_by(id=id).first()
    if current_user.messages.split(" ")[0]:
        messages = []
        for id_ in current_user.messages.split(" "):
            message = get_message(id_)
            if str(message[2]) == str(id) or str(message[3]) == str(id):
                messages.append(message)
    else:
        messages = []
    if request.method == 'POST':
        content = request.form['content']
        author_id = current_user.id
        receiver_id = id
        receiver_name = receiver.username
        author_name = current_user.username
        conn = get_db_connection()
        conn.execute('INSERT INTO messages (content, author_id, receiver_id, author_name, receiver_name) VALUES (?, ?, ?, ?, ?) returning id',
                         (content, author_id, receiver_id, author_name, receiver_name))
        msgs = conn.execute('SELECT * FROM messages').fetchall()
        ids = [int(message[0]) for message in msgs]
        m = max(ids)
        conn.commit()
        conn.close()

        msg = current_user.messages.split(" ")
        msg.append(str(m))
        if msg[0] == "":
            del msg[0]
        msg = " ".join(msg)
        current_user.messages = msg
        

        msg = receiver.messages.split(" ")
        msg.append(str(m))
        if msg[0] == "":
            del msg[0]
        msg = " ".join(msg)
        receiver.messages = msg
        

        db.session.commit()
        receiver = UserModel.query.filter_by(id=id).first()
        if current_user.messages.split(" ")[0]:
            messages = []
            for id_ in current_user.messages.split(" "):
                message = get_message(id_)
                if str(message[2]) == str(id) or str(message[3]) == str(id):
                    messages.append(message)
        else:
            messages = []
        return render_template('send.html', receiver = receiver, messages=messages)
    

    
    return render_template('send.html', receiver = receiver, messages=messages)

if __name__ == "__main__":
    app.run(threaded=True, debug=True, host='0.0.0.0')

