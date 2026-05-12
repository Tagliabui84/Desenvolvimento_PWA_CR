from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import datetime
import json

app = Flask(__name__)
CORS(app)

# ====================== BANCO DE DADOS ======================
def init_db():
    conn = sqlite3.connect('cidadereal.db')
    c = conn.cursor()

    # Usuários
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                 username TEXT PRIMARY KEY, password TEXT, role TEXT, 
                 nome TEXT, setor TEXT)''')

    # Boletins
    c.execute('''CREATE TABLE IF NOT EXISTS boletins (
                 id INTEGER PRIMARY KEY, data TEXT, usuario TEXT, conteudo TEXT)''')

    # Viagens Perdidas
    c.execute('''CREATE TABLE IF NOT EXISTS viagens (
                 id INTEGER PRIMARY KEY, data TEXT, usuario TEXT, setor TEXT, 
                 linha TEXT, carro TEXT, motivo TEXT)''')

    # Fiscalizações
    c.execute('''CREATE TABLE IF NOT EXISTS fiscalizacoes (
                 id INTEGER PRIMARY KEY, data TEXT, usuario TEXT, setor TEXT, 
                 tipo TEXT, descricao TEXT)''')

    # Usuários padrão
    usuarios = [
        ("gestor", "1234", "gestor", "Gestor Operacional", ""),
        ("fiscal1", "1234", "fiscal", "Fiscal ERIL", "ERIL"),
        ("instrutor1", "1234", "instrutor", "Instrutor BINGEM", "BINGEM")
    ]
    for u in usuarios:
        c.execute("INSERT OR REPLACE INTO usuarios VALUES (?,?,?,?,?)", u)

    conn.commit()
    conn.close()
    print("✅ Banco de dados carregado!")

init_db()

# ====================== ROTAS ======================
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = sqlite3.connect('cidadereal.db')
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE username=? AND password=?", 
              (data['username'], data['password']))
    user = c.fetchone()
    conn.close()
    if user:
        return jsonify({"success": True, "username": user[0], "role": user[2], "nome": user[3], "setor": user[4]})
    return jsonify({"success": False, "msg": "Usuário ou senha incorretos"}), 401

@app.route('/api/boletim', methods=['POST'])
def salvar_boletim():
    data = request.json
    conn = sqlite3.connect('cidadereal.db')
    c = conn.cursor()
    c.execute("INSERT INTO boletins (data, usuario, conteudo) VALUES (?, ?, ?)",
              (datetime.datetime.now().isoformat(), data.get('usuario'), json.dumps(data)))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "msg": "Boletim salvo com sucesso!"})

@app.route('/api/viagem', methods=['POST'])
def salvar_viagem():
    data = request.json
    conn = sqlite3.connect('cidadereal.db')
    c = conn.cursor()
    c.execute("INSERT INTO viagens (data, usuario, setor, linha, carro, motivo) VALUES (?, ?, ?, ?, ?, ?)",
              (datetime.datetime.now().isoformat(), data.get('usuario'), data.get('setor'), 
               data.get('linha'), data.get('carro'), data.get('motivo')))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "msg": "Viagem registrada!"})

@app.route('/api/fiscalizacao', methods=['POST'])
def salvar_fiscalizacao():
    data = request.json
    conn = sqlite3.connect('cidadereal.db')
    c = conn.cursor()
    c.execute("INSERT INTO fiscalizacoes (data, usuario, setor, tipo, descricao) VALUES (?, ?, ?, ?, ?)",
              (datetime.datetime.now().isoformat(), data.get('usuario'), data.get('setor'), 
               data.get('tipo'), data.get('descricao')))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "msg": "Registro salvo!"})

@app.route('/api/relatorios', methods=['GET'])
def relatorios():
    conn = sqlite3.connect('cidadereal.db')
    c = conn.cursor()
    c.execute("SELECT id, data, usuario, conteudo FROM boletins ORDER BY id DESC LIMIT 20")
    boletins = c.fetchall()
    conn.close()
    return jsonify({"boletins": boletins})

if __name__ == '__main__':
    print("="*70)
    print("🚀 CIDADE REAL - SISTEMA OPERACIONAL")
    print("🔗 PC: http://localhost:5000")
    print("📱 Celular: http://192.168.1.2:5000  (ou seu IP)")
    print("="*70)
    app.run(debug=True, host='0.0.0.0', port=5000)