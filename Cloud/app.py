from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_PATH = 'zombie_rand.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores (  --  確認表名是 scores
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    time INT,
                    score INT)''')
    conn.commit()
    conn.close()

@app.route('/submit_score', methods=['POST'])
def submit_score():
    data = request.json
    name = data.get('name')
    score = data.get('score')
    play_time = data.get('time')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 先查詢是否已經有這個玩家的紀錄
    c.execute('SELECT score FROM scores WHERE name = ? AND time = ?', (name, play_time))
    result = c.fetchone()

    if result:
        old_score = result[0]
        # 只有新分數比較高時才更新
        if score > old_score:
            c.execute('UPDATE scores SET score = ? WHERE name = ? AND time = ?', (score, name, play_time))
    else:
        # 沒有紀錄就插入
        c.execute('INSERT INTO scores (name, time, score) VALUES (?, ?, ?)', (name, play_time, score))

    conn.commit()
    conn.close()
    return jsonify({"status": "success"})


@app.route('/get_ranking', methods=['GET'])
def get_ranking():
    try:
        play_time = int(request.args.get('time', 30))
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT name, score FROM scores WHERE time = ? ORDER BY score DESC LIMIT 100', (play_time,)) 
        data = c.fetchall()
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080)
