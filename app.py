from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "🌍 Silicic Earth API", "status": "online"})

@app.route('/estadisticas')
def stats():
    return jsonify({"total_evaluaciones": 0, "puntuacion_promedio": 0})

if __name__ == '__main__':
    app.run()