import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, send_from_directory
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

import os
from os.path import exists

from flask_login import login_required, current_user, login_user, logout_user

from models import UserModel, db, load_user, login

import random

from datetime import datetime

import requests

def get_db_connection():
    conn = sqlite3.connect('datas.db')
    conn.row_factory = sqlite3.Row
    return conn

def magic(text):
  text2 = text.split(" ")
  for i, el in enumerate(text2):
    if el.startswith("http") == False:
      if len(el) >= 34:
        el = el[0:int(len(el)/4)] + " " + el[int(len(el)/4):int(len(el)/2)] + el[int(len(el)/2):3*int(len(el)/4)]  + el[int(len(el)/4):-1]
        text2[i] = el
      if len(el) >= 17:
        el = el[0:int(len(el)/2)] + " " + el[int(len(el)/2):-1]
        text2[i] = el
  text = ' '.join(text2)
  return text

app = Flask(__name__)
app.secret_key = "Tourtle4Ever"

app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login.init_app(app)
login.login_view = 'login'

def numberOfDays(y, m):
    leap = 0
    if y% 400 == 0:
        leap = 1
    elif y % 100 == 0:
        leap = 0
    elif y% 4 == 0:
        leap = 1
    if m==2:
        return 28 + leap
    list = [1,3,5,7,8,10,12]
    if m in list:
        return 31
    return 30

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
            return render_template("login.html", message="Mot de passe ou utilisateur incorrect", email=email)
     
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
        password2 = request.form['password2']
 
        if UserModel.query.filter_by(email=email).first():
            return render_template('register.html', message="Le compte existe déjà", email=email)
        
        if password != password2:
            return render_template('register.html', message="Les mots de passe sont différents")
             
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
    unread = False
    messages = []
    if current_user.messages.split(" ")[0]:
        messages = [get_message(id) for id in current_user.messages.split(" ")]
    for message in messages:
      if message:
        if message[3] == current_user.id and message[8] == False:
            unread = True
            break
    if current_user.admin == 1:
        return render_template("admin.html", unread=unread)
    else:
        redirect(url_for('index'))


@app.route('/', methods=('GET', 'POST'))
@login_required
def index():
    unread = False
    messages = []
    if current_user.messages.split(" ")[0]:
        messages = [get_message(id) for id in current_user.messages.split(" ")]
    for message in messages:
      if message:
        if message[3] == current_user.id and message[8] == False:
            unread = True
            break
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM blog').fetchall()
    conn.close()
    return render_template('index.html', posts=posts[::-1], unread=unread)

@app.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    unread = False
    messages = []
    if current_user.messages.split(" ")[0]:
        messages = [get_message(id) for id in current_user.messages.split(" ")]
    for message in messages:
      if message:
        if message[3] == current_user.id and message[8] == False:
            unread = True
            break
    users = UserModel.query.all()
    conn = get_db_connection()
    blogs = conn.execute('SELECT * FROM blog').fetchall()
    events = conn.execute('SELECT * FROM calendar').fetchall()
    dsts = conn.execute('SELECT * FROM dst').fetchall()
    follow = conn.execute('SELECT * FROM follow').fetchall()
    conn.close()
    return render_template('search.html', users=users, blogs=blogs, events=events, dsts=dsts, follow=follow, unread=unread)

@app.route('/conditions', methods=('GET', 'POST'))
def conditions():
  return render_template('conditions.html')
  
@app.route('/livres', methods=('GET', 'POST'))
@login_required
def livres():
    unread = False
    messages = []
    if current_user.messages.split(" ")[0]:
        messages = [get_message(id) for id in current_user.messages.split(" ")]
    for message in messages:
      if message:
        if message[3] == current_user.id and message[8] == False:
            unread = True
            break
    return render_template('livres.html', unread=unread)

@app.route('/<int:id>/userInfos', methods=('GET', 'POST'))
@login_required
def userInfos(id):
    unread = False
    messages = []
    if current_user.messages.split(" ")[0]:
        messages = [get_message(id) for id in current_user.messages.split(" ")]
    for message in messages:
      if message:
        if message[3] == current_user.id and message[8] == False:
            unread = True
            break
    user = load_user(id)
    try:
      user.pp
    except:
      return render_template('userInfos.html', user="NOPE", unread=unread)
    return render_template('userInfos.html', user=user, unread=unread)

@app.route('/<int:id>/modify_user', methods=('GET', 'POST'))
@login_required
def modifyUser(id):
    unread = False
    messages = []
    if current_user.messages.split(" ")[0]:
        messages = [get_message(id) for id in current_user.messages.split(" ")]
    for message in messages:
      if message:
        if message[3] == current_user.id and message[8] == False:
            unread = True
            break
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
        spes = magic(spes)
        description = magic(description)
        classe = magic(classe)
        parcours = magic(parcours)
        q_a = magic(q_a)
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
    return render_template('modify_user.html', user=user, follow=follow, unread=unread)

@app.route('/dst', methods=('GET', 'POST'))
@login_required
def dst():
    unread = False
    messages = []
    if current_user.messages.split(" ")[0]:
        messages = [get_message(id) for id in current_user.messages.split(" ")]
    for message in messages:
      if message:
        if message[3] == current_user.id and message[8] == False:
            unread = True
            break
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM dst').fetchall()
    conn.close()
    return render_template('dst.html', posts=posts[::-1], unread=unread)

@app.route('/<int:id_month>/calendar', methods=('GET', 'POST'))
@login_required
def calendar(id_month):
    unread = False
    messages = []
    if current_user.messages.split(" ")[0]:
        messages = [get_message(id) for id in current_user.messages.split(" ")]
    for message in messages:
      if message:
        if message[3] == current_user.id and message[8] == False:
            unread = True
            break
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM calendar').fetchall()
    conn.close()
    
    suscribers = []
    
    current_dateTime = datetime.now()
    year = current_dateTime.year
    id_month_2 = id_month + current_dateTime.month
    while id_month_2 - 12 > 0:
      year += 1
      id_month_2 -= 12
      
    month_ = (current_dateTime.month + id_month)%12
    if month_ == 0:
      month_ = 12
    current_dateTime = current_dateTime.replace(day = 1, month=month_, year=year)
    
    allDays = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    allMonts = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Décembre"]
    
    weekday = allDays[current_dateTime.weekday()]
    
    if id_month%12 == 0:
      day = "{} {} {} {}".format(weekday, datetime.now().day, allMonts[current_dateTime.month-1], current_dateTime.year)
    else:
      day = "{} {}".format(allMonts[current_dateTime.month-1], current_dateTime.year)
    
    month_len = numberOfDays(current_dateTime.year, current_dateTime.month)
    first_day = current_dateTime.replace(day=1)
    first_week_day = first_day.weekday()
    last_month_day_number = numberOfDays(current_dateTime.year, current_dateTime.month-1)
    month =[]
    for i in range(first_week_day):
        month.append({"day": str(last_month_day_number-i), "lastMonth":True, "events":''})
    month = month[::-1]

    today = datetime.now()
    month_ = (today.month+id_month)%12
    if month_ == 0:
      month_ = 12
    today = today.replace(day=1, month=month_, year=year)
    today = today.date()
    
    for i in range(1, month_len+1):
        events = ""
        date = today.replace(day=i)
        for event in posts:
            if str(event[7]) == str(date):
                events = event[0]
        if len(str(i)) == 1:
            i = str("0{}".format(i))
        month.append({"day": str(i), "lastMonth":False, "event":events})

    i = 1
    while len(month) < 7*6:
        j = i
        if len(str(j)) == 1:
            j = str("0{}".format(j))
        month.append({"day": str(j), "lastMonth":True, "event":""})
        i += 1
        
    for p in posts:
        p = list(p)
        u = []
        for i in p[6].split(" "):
          if i.isdigit():
            try:
              u.append(load_user(int(i)))
            except:
              pass
        suscribers.append(u)
    return render_template('calendar.html', posts=posts[::-1], suscribers=suscribers[::-1], day=day, date=current_dateTime, month_len=month_len, month=month, unread=unread, id_month=id_month)

@app.route('/add_event', methods=('GET', 'POST'))
@login_required
def add_event():
    unread = False
    messages = []
    if current_user.messages.split(" ")[0]:
        messages = [get_message(id) for id in current_user.messages.split(" ")]
    for message in messages:
      if message:
        if message[3] == current_user.id and message[8] == False:
            unread = True
            break
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
        title = magic(title)
        conn = get_db_connection()
        conn.execute('INSERT INTO calendar (title, dates, description_, types, creator_id, creator_name, participants) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (title, dates, description, types, creator_id, current_user.username, ""))
        conn.commit()
        conn.close()

        return redirect(url_for('calendar', id_month=0))
    return render_template('add_event.html', follow=follow, unread=unread)

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
    return redirect(url_for('calendar', id_month=0))

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
    return redirect(url_for('calendar', id_month=0))

@app.route('/<int:id>/delete_event', methods=('GET', 'POST'))
@login_required
def delete_event(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM calendar WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('calendar', id_month=0))

@app.route('/add_dst', methods=('GET', 'POST'))
@login_required
def add():
    unread = False
    messages = []
    if current_user.messages.split(" ")[0]:
        messages = [get_message(id) for id in current_user.messages.split(" ")]
    for message in messages:
      if message:
        if message[3] == current_user.id and message[8] == False:
            unread = True
            break
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
        images = ' '.join(images)
        title = magic(title)
        conn = get_db_connection()
        conn.execute('INSERT INTO dst (title, images) VALUES (?, ?)',
                     (title, images))
        conn.commit()
        conn.close()
        return redirect(url_for('dst'))


    return render_template('add_dst.html', unread=unread)

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
    unread = False
    messages = []
    if current_user.messages.split(" ")[0]:
        messages = [get_message(id) for id in current_user.messages.split(" ")]
    for message in messages:
      if message:
        if message[3] == current_user.id and message[8] == False:
            unread = True
            break
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
            images = ' '.join(images)
        except:
            post_type = "VIDEO"
        if images.split(' ') == [""]:
            post_type = "VIDEO"
        conn = get_db_connection()
        if post_type == "ARTICLE":
            title = magic(title)
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
            if link.startswith('http'):
              r = requests.get(link)
              if "Video unavailable" not in r.text:
                conn.execute('INSERT INTO blog (title, content, images, author_id, author_name, types, link) VALUES (?, ?, ?, ?, ?, ?, ?)',
                         ("", "", "", current_user.id, current_user.username, types, link))
              else:
                redirect(url_for("write_blog"))
            else:
              redirect(url_for("write_blog"))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))


    return render_template('write_blog.html', follow=follow, unread=unread)

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
    unread = False
    messages = []
    if current_user.messages.split(" ")[0]:
        messages = [get_message(id) for id in current_user.messages.split(" ")]
    for message in messages:
      if message:
        if message[3] == current_user.id and message[8] == False:
            unread = True
            break
    users = []
    utilisateurs = UserModel.query.all()
    if current_user.messages.split(" ")[0]:
        messages = [get_message(id) for id in current_user.messages.split(" ")]
    else:
        messages = []
    conversations = []
    ids = [current_user.id]
    for message in messages[::-1]:
      if message != None:
        if message[2] not in ids:
          try:
            users.append(load_user(message[2]).pp)
            ids.append(message[2])
            conversations.append(message)
          except:
            users.append("")
            ids.append(message[2])
            conversations.append(message)
        if message[3] not in ids:
          try:
            users.append(load_user(message[3]).pp)
            ids.append(message[3])
            conversations.append(message)
          except:
            users.append("")
            ids.append(message[3])
            conversations.append(message)
    return render_template('messages.html', conversations=conversations, users=users, utilisateurs=utilisateurs, unread=unread)

@app.route('/<int:id>/send', methods=('GET', 'POST'))
@login_required
def send(id):
    messages = []
    receiver =load_user(id)
    try:
      receiver.pp
    except:
      receiver = {"pp":"", "username":"Compte supprimé"}
      
    if current_user.messages.split(" ")[0]:
        for id_ in current_user.messages.split(" "):
            message = get_message(id_)
            if message != None:
              if str(message[2]) == str(id) or str(message[3]) == str(id):
                if str(current_user.id) == str(message[3]):
                    conn = get_db_connection()
                    conn.execute('UPDATE messages SET read = ? WHERE id = ?', (True, message[0],))
                    conn.commit()
                    conn.close()
                messages.append(message)
        
    if request.method == 'POST':
        content = request.form['content']
        author_id = current_user.id
        receiver_id = id
        try:
          load_user(receiver_id).pp
        except:
          return redirect(url_for("send", id=receiver_id))
        receiver_name = receiver.username
        author_name = current_user.username
        content = magic(content)
        
        files = request.files.getlist('file')
        images = []
        for f2 in files:
            if f2.filename:
                path = "static/images/" + secure_filename(f2.filename)
                while exists(path):
                    path = path.split(".")
                    path[0] += str(random.randint(0, 9))
                    path = ".".join(path)
                f2.save(path)
                images.append(path)
        images = ' '.join(images)

        contentWithoutSpace = content.split(" ")
        contentWithoutSpace = "".join(contentWithoutSpace)
        if len(contentWithoutSpace)==0 and len(images)==0:
          return(redirect(url_for("send", id=id)))
        
        conn = get_db_connection()
        conn.execute('INSERT INTO messages (content, author_id, receiver_id, author_name, receiver_name, images, read) VALUES (?, ?, ?, ?, ?, ?, ?)', (content, author_id, receiver_id, author_name, receiver_name, images, False))
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
        messages = []
        receiver = UserModel.query.filter_by(id=id).first()
        if current_user.messages.split(" ")[0]:
            for id_ in current_user.messages.split(" "):
                message = get_message(id_)
                if message != None:
                    if str(message[2]) == str(id) or str(message[3]) == str(id):
                        messages.append(message)
        return render_template('send.html', receiver = receiver, messages=messages)
    
    
    return render_template('send.html', receiver = receiver, messages=messages)


if __name__ == "__main__":
    app.run(threaded=True, debug=True, host='0.0.0.0')

