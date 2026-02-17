from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "khab_secret"

# Crear base si no existe
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        password TEXT
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

    # Usuario por defecto
    cursor.execute("SELECT * FROM usuarios WHERE usuario='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (usuario,password) VALUES ('admin','1234')")

    conn.commit()
    conn.close()

init_db()

# LOGIN
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = request.form["usuario"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND password=?", (user,password))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            session["user"] = user
            return redirect("/dashboard")

    return render_template("login.html")

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")

# CLIENTES
@app.route("/clientes", methods=["GET","POST"])
def clientes():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        contrato = request.form["contrato"]
        correo = request.form["correo"]
        telefono = request.form["telefono"]
        direccion = request.form["direccion"]
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

        cursor.execute("""
        INSERT INTO clientes (nombre, contrato, correo, telefono, direccion, fecha)
        VALUES (?,?,?,?,?,?)
        """,(nombre,contrato,correo,telefono,direccion,fecha))

        conn.commit()

    cursor.execute("SELECT * FROM clientes ORDER BY id DESC")
    clientes = cursor.fetchall()
    conn.close()

    return render_template("clientes.html", clientes=clientes)

# EDITAR CLIENTE
@app.route("/editar/<int:id>", methods=["GET","POST"])
def editar(id):
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
        UPDATE clientes SET nombre=?, contrato=?, correo=?, telefono=?, direccion=?
        WHERE id=?
        """,(request.form["nombre"],
             request.form["contrato"],
             request.form["correo"],
             request.form["telefono"],
             request.form["direccion"],
             id))
        conn.commit()
        return redirect("/clientes")

    cursor.execute("SELECT * FROM clientes WHERE id=?", (id,))
    cliente = cursor.fetchone()
    conn.close()

    return render_template("clientes.html", editar=cliente)

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)