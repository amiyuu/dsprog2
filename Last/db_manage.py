import sqlite3
from typing import List, Tuple, Optional
from contextlib import contextmanager

class VacantHouseDB:
    """山梨県空き家データベース管理クラス"""
    
    def __init__(self, db_path: str = "vacant_house.db"):
        """
        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """データベース接続のコンテキストマネージャー"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def initialize_database(self):
        """データベースとテーブルを初期化"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # city_townテーブル作成
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS city_town (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL
                )
            """)
            
            # vacant_housesテーブル作成
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vacant_houses (
                    c_t_code TEXT,
                    year INTEGER,
                    total_house INTEGER,
                    total_vacant INTEGER,
                    rent INTEGER,
                    sale INTEGER,
                    second_use INTEGER,
                    other_vacant INTEGER,
                    PRIMARY KEY (c_t_code, year),
                    FOREIGN KEY (c_t_code) REFERENCES city_town(code)
                )
            """)
            
            # house_ageテーブル作成
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS house_age (
                    c_t_code TEXT,
                    year INTEGER,
                    pre_1970 INTEGER,
                    y1971_1980 INTEGER,
                    y1981_1990 INTEGER,
                    y1991_2000 INTEGER,
                    y2001_2010 INTEGER,
                    y2011_2020 INTEGER,
                    y2021_2023 INTEGER,
                    PRIMARY KEY (c_t_code, year),
                    FOREIGN KEY (c_t_code) REFERENCES city_town(code)
                )
            """)
            
            print("データベースとテーブルを初期化しました")
    
    def insert_city_town(self, code: str, name: str):
        """市町村データを挿入
        
        Args:
            code: 地域コード
            name: 市町村名
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO city_town (code, name)
                VALUES (?, ?)
            """, (code, name))
    
    def insert_vacant_houses(self, data: dict):
        """空き家データを挿入
        
        Args:
            data: 空き家データの辞書
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO vacant_houses 
                (c_t_code, year, total_house, total_vacant, rent, sale, 
                 second_use, other_vacant)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['c_t_code'],
                data['year'],
                data['total_house'],
                data['total_vacant'],
                data['rent'],
                data['sale'],
                data['second_use'],
                data['other_vacant']
            ))
    
    def insert_house_age(self, data: dict):
        """築年数データを挿入
        
        Args:
            data: 築年数データの辞書
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO house_age 
                (c_t_code, year, pre_1970, y1971_1980, y1981_1990, 
                 y1991_2000, y2001_2010, y2011_2020, y2021_2023)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['c_t_code'],
                data['year'],
                data['pre_1970'],
                data['y1971_1980'],
                data['y1981_1990'],
                data['y1991_2000'],
                data['y2001_2010'],
                data['y2011_2020'],
                data['y2021_2023']
            ))
    
    def get_all_cities(self) -> List[Tuple[str, str]]:
        """全市町村を取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT code, name FROM city_town")
            return cursor.fetchall()
    
    def get_vacant_houses_by_city(self, c_t_code: str) -> List[Tuple]:
        """指定市町村の空き家データを取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM vacant_houses 
                WHERE c_t_code = ?
                ORDER BY year
            """, (c_t_code,))
            return cursor.fetchall()
    
    def get_house_age_by_city(self, c_t_code: str) -> List[Tuple]:
        """指定市町村の築年数データを取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM house_age 
                WHERE c_t_code = ?
                ORDER BY year
            """, (c_t_code,))
            return cursor.fetchall()
    
    def drop_all_tables(self):
        """全テーブルを削除（開発用）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS house_age")
            cursor.execute("DROP TABLE IF EXISTS vacant_houses")
            cursor.execute("DROP TABLE IF EXISTS city_town")
            print("全テーブルを削除しました")


# 使用例
if __name__ == "__main__":
    # データベース初期化
    db = VacantHouseDB()
    
    # 既存のテーブルを削除（初回のみ）
    # db.drop_all_tables()
    
    # テーブル作成
    db.initialize_database()
    
    # サンプルデータの挿入
    print("\n--- サンプルデータを挿入 ---")
    
    # 市町村データ
    db.insert_city_town("19201", "甲府市")
    db.insert_city_town("19202", "富士吉田市")
    
    # 空き家データ（サンプル）
    vacant_data = {
        'c_t_code': '19201',
        'year': 2023,
        'total_house': 100000,
        'total_vacant': 15000,
        'rent': 5000,
        'sale': 2000,
        'second_use': 3000,
        'other_vacant': 5000
    }
    db.insert_vacant_houses(vacant_data)
    
    # 築年数データ（サンプル）
    age_data = {
        'c_t_code': '19201',
        'year': 2023,
        'pre_1970': 10000,
        'y1971_1980': 15000,
        'y1981_1990': 20000,
        'y1991_2000': 18000,
        'y2001_2010': 22000,
        'y2011_2020': 13000,
        'y2021_2023': 2000
    }
    db.insert_house_age(age_data)
    
    # データ確認
    print("\n--- 登録された市町村一覧 ---")
    cities = db.get_all_cities()
    for code, name in cities:
        print(f"{code}: {name}")
    
    print("\n--- 甲府市の空き家データ ---")
    vacant_houses = db.get_vacant_houses_by_city("19201")
    for row in vacant_houses:
        print(row)
    
    print("\n--- 甲府市の築年数データ ---")
    house_ages = db.get_house_age_by_city("19201")
    for row in house_ages:
        print(row)