import sqlite3

# DB 파일 연결
DB_NAME = 'users.db'

# 테이블 초기화 (봇 시작 시 한 번 호출)
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # 사용자 ID, 경험치, 레벨을 저장할 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_xp (
            user_id INTEGER PRIMARY KEY,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

# 유저 데이터 가져오기
def get_user_xp(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT xp, level FROM user_xp WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row  # 없으면 None 반환

# 기존 update_xp 함수를 아래처럼 반환값이 있게 수정하세요
def update_xp(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    row = get_user_xp(user_id)
    
    if row is None:
        new_xp = max(0, amount)
        level = 1
        cursor.execute('INSERT INTO user_xp (user_id, xp, level) VALUES (?, ?, ?)', (user_id, new_xp, level))
    else:
        new_xp = max(0, row[0] + amount)
        level = (new_xp // 100) + 1 # 100XP당 1레벨
        cursor.execute('UPDATE user_xp SET xp = ?, level = ? WHERE user_id = ?', (new_xp, level, user_id))
        
    conn.commit()
    conn.close()
    return new_xp, level # <--- 이 부분만 추가/수정됨