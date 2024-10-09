from flask import Flask, jsonify

# from flask_cors import CORS
import sqlite3

app = Flask(__name__)
# CORS(app)


@app.route('/api/updates', methods=['GET'])
def get_updates():
    conn = sqlite3.connect('./db/services.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, last_update FROM services")
    services = cursor.fetchall()
    conn.close()

    data = [
        {'name': name, 'last_update': last_update} for name, last_update in services
    ]
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
