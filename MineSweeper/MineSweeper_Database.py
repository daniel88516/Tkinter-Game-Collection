import sqlite3
from MineSweeper_Difficulty import DifficultyConfig
class Database:
    def __init__(self, db_name='minesweeper.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        """建立成績表格，包含難度欄位"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                score TEXT NOT NULL,  -- 格式為 'mm ss sss'
                difficulty TEXT NOT NULL  -- 簡單、普通、困難
            )
        ''')
        self.connection.commit()

    def insert_score(self, name, minutes, seconds, millis, config: DifficultyConfig) -> bool:
        """插入成績，若玩家名稱已存在，覆蓋表現較差的成績"""
        score = f"{minutes:02d} {seconds:02d} {millis:03d}"

        # 檢查是否已存在該玩家的記錄
        self.cursor.execute('''
            SELECT id, score FROM scores WHERE name = ? AND difficulty = ?
        ''', (name, config.name))
        existing_record = self.cursor.fetchone()

        if existing_record:
            # 比較新成績與舊成績的優劣
            existing_id, existing_score = existing_record
            existing_minutes, existing_seconds, existing_millis = map(int, existing_score.split())
            if (minutes, seconds, millis) < (existing_minutes, existing_seconds, existing_millis):
                # 新成績更好，更新記錄
                self.cursor.execute('''
                    UPDATE scores SET score = ? WHERE id = ?
                ''', (score, existing_id))
                self.connection.commit()
                return True
            else:
                return False
        else:
            # 插入新記錄
            self.cursor.execute('''
                INSERT INTO scores (name, score, difficulty) VALUES (?, ?, ?)
            ''', (name, score, config.name))
            self.connection.commit()
            return True

    def get_total_records(self, difficulty):
        """獲取指定難度的總記錄數"""
        self.cursor.execute('''
            SELECT COUNT(*) FROM scores WHERE difficulty = ?
        ''', (difficulty,))
        return self.cursor.fetchone()[0]

    def get_scores_by_page(self, difficulty, start_idx, per_page):
        """獲取指定難度的分頁成績"""
        self.cursor.execute('''
            SELECT name, score FROM scores 
            WHERE difficulty = ? 
            ORDER BY 
                CAST(SUBSTR(score, 1, 2) AS INTEGER) ASC,  -- 按分鐘排序
                CAST(SUBSTR(score, 4, 2) AS INTEGER) ASC,  -- 按秒排序
                CAST(SUBSTR(score, 7, 3) AS INTEGER) ASC   -- 按毫秒排序
            LIMIT ? OFFSET ?
        ''', (difficulty, per_page, start_idx))
        return self.cursor.fetchall()

    def delete_all_scores(self):
        """刪除所有成績"""
        self.cursor.execute('DELETE FROM scores')
        self.connection.commit()

    def parse_score(self, score):
        """解析成績格式 'mm ss sss'"""
        minutes, seconds, millis = map(int, score.split())
        return f"{minutes:02d}:{seconds:02d}.{millis:03d}"

    def close(self):
        """關閉資料庫連線"""
        self.connection.close()
if __name__ == "__main__": 
    db = Database()
    db.delete_all_scores()
    db.close()