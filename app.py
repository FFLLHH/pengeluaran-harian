from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables (berguna untuk testing lokal)
load_dotenv()

app = Flask(__name__)

# Mengambil URL Database dari Environment Variable (Aman dari hard-code)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model Database
class Pengeluaran(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keterangan = db.Column(db.String(200), nullable=False)
    jumlah = db.Column(db.Float, nullable=False)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'keterangan': self.keterangan,
            'jumlah': self.jumlah,
            'tanggal': self.tanggal.strftime('%Y-%m-%d %H:%M:%S')
        }

# Membuat tabel database sebelum request pertama
with app.app_context():
    db.create_all()

# 1. Health Check
@app.route('/kesehatan', methods=['GET'])
def kesehatan():
    return jsonify({'status': 'sehat', 'pesan': 'Sistem berjalan normal'})

# 2. Create (POST)
@app.route('/pengeluaran', methods=['POST'])
def tambah_pengeluaran():
    data = request.get_json()
    if not data or not 'keterangan' in data or not 'jumlah' in data:
        return jsonify({'error': 'Data tidak lengkap, pastikan ada keterangan dan jumlah'}), 400
    
    pengeluaran_baru = Pengeluaran(keterangan=data['keterangan'], jumlah=data['jumlah'])
    db.session.add(pengeluaran_baru)
    db.session.commit()
    return jsonify({'pesan': 'Pengeluaran berhasil dicatat', 'data': pengeluaran_baru.to_dict()}), 201

# 3. Read (GET)
@app.route('/pengeluaran', methods=['GET'])
def lihat_pengeluaran():
    semua_pengeluaran = Pengeluaran.query.all()
    return jsonify([p.to_dict() for p in semua_pengeluaran])

# 4. Update (PUT)
@app.route('/pengeluaran/<int:id>', methods=['PUT'])
def update_pengeluaran(id):
    pengeluaran = Pengeluaran.query.get_or_404(id)
    data = request.get_json()
    
    if 'keterangan' in data:
        pengeluaran.keterangan = data['keterangan']
    if 'jumlah' in data:
        pengeluaran.jumlah = data['jumlah']
        
    db.session.commit()
    return jsonify({'pesan': 'Pengeluaran berhasil diupdate', 'data': pengeluaran.to_dict()})

# 5. Delete (DELETE)
@app.route('/pengeluaran/<int:id>', methods=['DELETE'])
def hapus_pengeluaran(id):
    pengeluaran = Pengeluaran.query.get_or_404(id)
    db.session.delete(pengeluaran)
    db.session.commit()
    return jsonify({'pesan': 'Pengeluaran berhasil dihapus'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)