import sqlite3

DATABASE = 'app.db'
db = sqlite3.connect(DATABASE)

cursor = db.cursor()

# Creation of table 'pictures. If it exists already, we delete the table and create a new one
cursor.execute('DROP TABLE IF EXISTS pictures')
cursor.execute('''CREATE TABLE pictures (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title VARCHAR(200) NOT NULL,
                            post_date DATE NOT NULL,
                            description VARCHAR(2000),
                            img_path VARCHAR(500) NOT NULL
                            )''')


cursor.execute('DROP TABLE IF EXISTS categories')
cursor.execute("""CREATE TABLE categories (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nom VARCHAR(200) NOT NULL
                            )""")


cursor.execute('DROP TABLE IF EXISTS tags')
cursor.execute("""CREATE TABLE tags (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nom VARCHAR(200) NOT NULL
                            )""")


cursor.execute('DROP TABLE IF EXISTS comments')
cursor.execute("""CREATE TABLE comments (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            content VARCHAR(2000) NOT NULL,
                            id_img INTEGER NOT NULL,
                            CONSTRAINT fk_img_com
                              FOREIGN KEY (id_img) REFERENCES pictures(id)
                              )""")


cursor.execute('DROP TABLE IF EXISTS img_cat')
cursor.execute("""CREATE TABLE img_cat (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_img INTEGER NOT NULL,
                            id_cat INTEGER NOT NULL,
                            CONSTRAINT fk_img_cat
                              FOREIGN KEY (id_img) REFERENCES pictures(id),
                            CONSTRAINT fk_img
                              FOREIGN KEY (id_cat) REFERENCES categories(id))""")


cursor.execute('DROP TABLE IF EXISTS img_tag')
cursor.execute("""CREATE TABLE img_tag (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_img INTEGER NOT NULL,
                            id_tag INTEGER NOT NULL,
                            CONSTRAINT fk_img_cat
                              FOREIGN KEY (id_img) REFERENCES pictures(id),
                            CONSTRAINT fk_img
                              FOREIGN KEY (id_tag) REFERENCES tags(id))""")


cursor.execute('DROP TABLE IF EXISTS img_note')
cursor.execute("""CREATE TABLE img_note (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            note FLOAT,
                            votants INTEGER NOT NULL,
                            id_img INTEGER NOT NULL,
                            CONSTRAINT fk_img_note_id
                              FOREIGN KEY (id_img) REFERENCES pictures(id))""")


for data in [
        ("Animal"),
        ("Travel"),
        ("Street photography"),
        ("Arts & Culture"),
        ("Nature"),
        ("Health & Wellness"),
        ("People"),
        ("Fashion"),
        ("Food & Drink"),
        ]:
    if data[-1] is None:
        cursor.execute(
            "INSERT INTO  (nom) VALUES (?)", data[0])
    else:
        cursor.execute(
            "INSERT INTO categories (nom) VALUES (?)", [data])


for data in [
        ("Insect", "2009-12-01", "a zoom of black insect",
        "animal_insect_black.jpg"),
        ("Reptil", "2009-12-01", "nice lizard",
        "animal_nature.jpg"),
        ("Baby bunny", "2011-11-01", "a sweet baby bynny",
        "baby_bunny.jpg"),
        ("Kitten", "2011-12-01", "the kitten and the tech",
        "baby_cat_scary_feelings_.jpg"),
        ]:
    if data[-1] is None:
        cursor.execute(
            "INSERT INTO  (title, post_date, description, img_path) VALUES\
            (?, ?, ?, ?)", data[0:3])
    else:
        cursor.execute(
            "INSERT INTO pictures (title, post_date, description, img_path)\
            VALUES (?, ?, ?, ?)", data)


for data in [
        ("Une bien belle photo", 1),
        ("C'est moi qui l'ai prise", 1),
        ("Xahou, splennnnnndide!", 2),
        ("Gratin Chicon ou Chicon Gratin ?", 3),
        ]:
    if data[-1] is None:
        cursor.execute(
            "INSERT INTO  comments (content, id_img) VALUES (?, ?)", data[0:1])
    else:
        cursor.execute(
            "INSERT INTO  comments (content, id_img) VALUES (?, ?)", data)


for data in [
        (1, 1),
        (1, 2),
        (1, 3),
        (2, 1),
        (2, 2),
        (3, 1),
        (4, 2),
        ]:
    if data[-1] is None:
        cursor.execute(
            "INSERT INTO (id_img, id_cat) VALUES (?, ?)", data[0:1])
    else:
        cursor.execute(
            "INSERT INTO img_cat (id_img, id_cat) VALUES (?, ?)", data)


# We save our changes into the database file
db.commit()

# We close the connection to the database
db.close()
