from flask import Flask, g, render_template, request, redirect, send_from_directory, flash
import sqlite3
import os
import random
from werkzeug.utils import secure_filename

app = Flask(__name__)
DATABASE = 'app.db'


#IMAGE_FOLDER  = 'images'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['uploads'] = 'uploads'


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# extraire liste pictures et liste categories
# ajout de fetchall
@app.route('/')
def homepage():
    db = get_db()
    pictures = db.execute('SELECT id, img_path FROM pictures')
    categories = db.execute('SELECT nom FROM categories')
    all_pictures = pictures.fetchall()
    category_list = []  
    for cat in categories:
        category_list.append(cat[0])
    return render_template('homepage.html', all_pictures=all_pictures, all_categories=category_list)

@app.route('/uploads/<filename>')
def show_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# --------------------------------------------------------------

# @app.route('/detail/<id>')
# def image(id):
#     db = get_db()
#     pictures = db.execute('SELECT pictures.id, pictures.img_path FROM pictures WHERE pictures.id = ?', [id])
#     image = pictures.fetchone()
#     return render_template('display.html', id=image)

# @app.route('/detail/<id>', methods=["GET", "POST"])
# def image(id):
#     if request.method == 'POST':
#         commentaire = request.form['comment']
#         db = get_db()
#         pictures = db.execute('INSERT INTO comments (content, id_img) VALUES (?, ?)', [commentaire, id])
#         db.commit()
#     db = get_db()
#     pictures = db.execute('SELECT pictures.id, pictures.img_path, pictures.title, pictures.description, pictures.post_date FROM pictures WHERE pictures.id = ?', [id])
#     comments = db.execute('SELECT content FROM comments WHERE id_img = ?', [id])
#     image = pictures.fetchone()
#     comm = comments.fetchall()
#     return render_template('display.html', id=image, com=comm)

@app.route('/detail/<id>', methods=["GET", "POST"])
def image(id):
    if request.method == 'POST':
        commentaire = request.form['comment']
        db = get_db()
        pictures = db.execute('INSERT INTO comments (content, id_img) VALUES (?, ?)', [commentaire, id])
        db.commit()
    db = get_db()
    pictures = db.execute('SELECT pictures.id, pictures.img_path, pictures.title, pictures.description, pictures.post_date FROM pictures WHERE pictures.id = ?', [id])
    comments = db.execute('SELECT content FROM comments WHERE id_img = ?', [id])
    categs = db.execute("SELECT categories.nom FROM categories INNER JOIN img_cat ON categories.id = img_cat.id_cat INNER JOIN pictures ON pictures.id = img_cat.id_img WHERE pictures.id = ?", [id])
    image = pictures.fetchone()
    comm = comments.fetchall()
    return render_template('display.html', id=image, com=comm, categ=categs)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=["GET", "POST"])
def upload_file():
    message = "Please feed us with your images ..."
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        title = request.form['title']
        new_cat = request.form['new_cat']
        multiselect = request.form.getlist('multiselect')
        post_date = request.form['post_date']
        description = request.form['description']
        if not file or title == "" or post_date == "" or file.filename == '' or not allowed_file(file.filename):
            message = "Please insert a Title and a Date and select a valid image"
            return render_template('upload.html', return_message=message)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            basedir = os.path.abspath(os.path.dirname(__file__))
            basepath = os.path.join(basedir, app.config['uploads'])
            for filenamme in os.listdir(basepath):
                if filenamme == filename:
                    filename = (filename + str(random.randint(0, 999999999999)))
            file.save(os.path.join(basedir, app.config['uploads'], filename))
            db = get_db()
            liste_title = db.execute('SELECT title FROM pictures WHERE title = ?', [title])
            list_title = liste_title.fetchone()
            if list_title:
                title = (title + str(random.randint(0, 999999999999)))
            db.execute('INSERT INTO pictures (title, post_date, description, img_path) VALUES (?, ?, ?, ?)', [title, post_date, description, filename])
            db.commit()
            db = get_db()
            for select in multiselect:
                verif = db.execute('SELECT nom FROM categories WHERE nom = ?', [select])
                ver = verif.fetchone()
                db.commit()
                if ver is None:
                    db = get_db()
                    db.execute('INSERT INTO categories (nom) VALUES (?)', [select])
                    db.commit()
                db = get_db()
                categ = db.execute('SELECT id FROM categories WHERE nom = ?', [select])
                idimg = db.execute('SELECT id FROM pictures WHERE title = ?', [title])
                categi = categ.fetchone()
                idimgi = idimg.fetchone()
                db.execute('INSERT INTO img_cat (id_img, id_cat) VALUES (?, ?)', [idimgi[0], categi[0]])
                db.commit()
            verif = db.execute('SELECT nom FROM categories WHERE nom = ?', [new_cat])
            ver = verif.fetchone()
            db.commit()
            if ver is None:
                db = get_db()
                db.execute('INSERT INTO categories (nom) VALUES (?)', [new_cat])
                db.commit()
            db = get_db()
            categ = db.execute('SELECT id FROM categories WHERE nom = ?', [new_cat])
            idimg = db.execute('SELECT id FROM pictures WHERE title = ?', [title])
            categi = categ.fetchone()
            idimgi = idimg.fetchone()
            db.execute('INSERT INTO img_cat (id_img, id_cat) VALUES (?, ?)', [idimgi[0], categi[0]])
            db.commit()
            message = "Well Done Your Photo is our property now"
    db = get_db()     
    cats = db.execute('SELECT nom FROM categories')
    catts = cats.fetchall()
    return render_template('upload.html', return_message=message, all_cat=catts)


# la route pour sélectionner les categories
@app.route("/categories/<categ>")
def index_images_cat(categ):
    db = get_db()
    cursor = db.execute("SELECT pictures.id, pictures.img_path FROM pictures INNER JOIN img_cat ON pictures.id = img_cat.id_img INNER JOIN categories ON categories.id = img_cat.id_cat WHERE categories.nom = ?", [categ])
    all_picture = cursor.fetchall()
    return render_template('homepage.html', all_pictures=all_picture, all_categories=[categ])


# -------------------------------------------------------------------


# @app.route('/uploads/<name>')
# def download_file(name):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], name)

# @app.route('/uploads/<filename>')
# def upload_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# @app.route('/', methods = ['POST'])
# def create():
#     if 'file' not in request.files:
        # return redirect('/')
    # attention, titre, caption et autres inputs, sont à récupérer via request.form
    # file = request.files['file']
    # gestion des erreurs et utilisateurs malicieux
    # if file.filename != '':
    #     filename = secure_filename(file.filename)
    #     file.save(os.path.join(UPLOAD_FOLDER, filename))
    #     db = get_db()
    #     db.execute('INSERT INTO pictures (path) VALUES (?)', [file.filename])
    #     db.commit()
    # return redirect('/')

# créer table categories
# ajouter photos par categories
# ajouter commentaires
# ajouter tags

if __name__ == '__main__':
    app.run(debug=True)
