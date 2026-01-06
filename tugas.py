import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Diperlukan untuk flash messages
DB_NAME = "books.db"

def connectdb():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connectdb()
    conn.execute('''CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    judul VARCHAR(100) NOT NULL,
                    penulis VARCHAR(100) NOT NULL
                )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = connectdb()
    books = conn.execute("SELECT * FROM books ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('index.html', books=books)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        judul = request.form['judul'].strip()
        penulis = request.form['penulis'].strip()
        
        if judul and penulis:  # Validasi input
            conn = connectdb()
            conn.execute("INSERT INTO books (judul, penulis) VALUES (?, ?)", 
                        (judul, penulis))
            conn.commit()
            conn.close()
            flash('Buku berhasil ditambahkan!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Judul dan penulis harus diisi!', 'error')
    
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = connectdb()
    
    # Cek buku ada atau tidak
    book = conn.execute("SELECT * FROM books WHERE id = ?", (id,)).fetchone()
    if not book:
        conn.close()
        flash('Buku tidak ditemukan!', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        judul = request.form['judul'].strip()
        penulis = request.form['penulis'].strip()
        
        if judul and penulis:
            conn.execute("UPDATE books SET judul = ?, penulis = ? WHERE id = ?", 
                        (judul, penulis, id))
            conn.commit()
            conn.close()
            flash('Buku berhasil diupdate!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Judul dan penulis harus diisi!', 'error')
    
    conn.close()
    return render_template('edit.html', book=book)

@app.route('/delete/<int:id>')
def delete(id):
    conn = connectdb()
    # Cek apakah ID ada sebelum delete
    book = conn.execute("SELECT * FROM books WHERE id = ?", (id,)).fetchone()
    if book:
        conn.execute("DELETE FROM books WHERE id = ?", (id,))
        conn.commit()
        flash('Buku berhasil dihapus!', 'success')
    else:
        flash('Buku tidak ditemukan!', 'error')
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()  # INISIALISASI DATABASE PENTING!
    app.run(debug=True, host='0.0.0.0', port=5000)
