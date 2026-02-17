from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "khab_secret"

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        password TEXT,
        rol TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        contrato TEXT,
        correo TEXT,
        telefono TEXT,
        direccion TEXT,
        fecha TEXT
    )
    """)

    # Crear admin por defecto si no existe
    cursor.execute("SELECT * FROM usuarios WHERE usuario='admin'")
    if not cursor.fetchone():
        password_hash = generate_password_hash("1234")
        cursor.execute("INSERT INTO usuarios (usuario,password,rol) VALUES (?,?,?)",
                       ("admin", password_hash, "admin"))

    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = request.form["usuario"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario=?", (user,))
        usuario = cursor.fetchone()
        conn.close()

        if usuario and check_password_hash(usuario[2], password):
            session["user"] = usuario[1]
            session["rol"] = usuario[3]
            return redirect("/dashboard")

    return render_template("login.html")