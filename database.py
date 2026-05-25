import sqlite3

DB_NAME = 'users.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_xp (
            user_id INTEGER PRIMARY KEY,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

def get_user_xp(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT xp, level FROM user_xp WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def update_xp(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    row = get_user_xp(user_id)
    if row is None:
        new_xp = max(0, amount)
        level = (new_xp // 100) + 1
        cursor.execute('INSERT INTO user_xp (user_id, xp, level) VALUES (?, ?, ?)', (user_id, new_xp, level))
    else:
        new_xp = max(0, row[0] + amount)
        level = (new_xp // 100) + 1
        cursor.execute('UPDATE user_xp SET xp = ?, level = ? WHERE user_id = ?', (new_xp, level, user_id))
    conn.commit()
    conn.close()
    return new_xp, level

# 순위표 데이터를 가져오는 함수 추가!
def get_top_users(limit=10):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, xp, level FROM user_xp ORDER BY xp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows