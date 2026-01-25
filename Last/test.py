"""
山梨県空き家データ分析プロジェクトのテストスイート
全ての機能テストをこのファイルで実行します
"""

import unittest
import os
import sqlite3
from db_manage import VacantHouseDB


class TestDatabase(unittest.TestCase):
    """データベース機能のテストケース"""
    
    @classmethod
    def setUpClass(cls):
        """テストクラス全体の初期化"""
        cls.test_db_path = "test_vacant_house.db"
    
    def setUp(self):
        """各テストメソッドの前に実行"""
        # テスト用DBのリセット
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        self.db = VacantHouseDB(self.test_db_path)
        self.db.initialize_database()
    
    def tearDown(self):
        """各テストメソッドの後に実行"""
        # テスト用DBの削除
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_database_initialization(self):
        """データベースとテーブルが正しく作成されるかテスト"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # テーブルの存在確認
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('city_town', 'vacant_houses', 'house_age')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            self.assertIn('city_town', tables)
            self.assertIn('vacant_houses', tables)
            self.assertIn('house_age', tables)
    
    def test_insert_city_town(self):
        """市町村データの挿入テスト"""
        # テストデータの挿入
        self.db.insert_city_town("19201", "甲府市")
        self.db.insert_city_town("19202", "富士吉田市")
        
        # データの取得
        cities = self.db.get_all_cities()
        
        # 検証
        self.assertEqual(len(cities), 2)
        self.assertIn(("19201", "甲府市"), cities)
        self.assertIn(("19202", "富士吉田市"), cities)
    
    def test_insert_duplicate_city(self):
        """重複する市町村コードの挿入テスト（INSERT OR IGNORE）"""
        self.db.insert_city_town("19201", "甲府市")
        self.db.insert_city_town("19201", "甲府市")
        
        cities = self.db.get_all_cities()
        
        # 1件のみ登録されていることを確認
        self.assertEqual(len(cities), 1)
        self.assertEqual(cities[0][1], "甲府市")  # 名前が保持されていること    
    def test_insert_vacant_houses(self):
        """空き家データの挿入テスト"""
        # 事前に市町村を登録
        self.db.insert_city_town("19201", "甲府市")
        
        # テストデータの作成
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
        self.db.insert_vacant_houses(vacant_data)
        
        #DBからデータ取得
        result = self.db.get_vacant_houses_by_city("19201")
        
        # 結果の検証
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], '19201')  # c_t_code
        self.assertEqual(result[0][1], 2023)     # year
        self.assertEqual(result[0][2], 100000)   # total_house
        self.assertEqual(result[0][3], 15000)    # total_vacant
    
    def test_insert_house_age(self):
        """築年数データの挿入テスト"""
        # 事前に市町村を登録
        self.db.insert_city_town("19201", "甲府市")
        
        # 築年数データの作成
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
        self.db.insert_house_age(age_data)
        
        # DBからデータ取得
        result = self.db.get_house_age_by_city("19201")
        
        # 結果の検証
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], '19201')  # c_t_code
        self.assertEqual(result[0][2], 10000)    # pre_1970
        self.assertEqual(result[0][3], 15000)    # y1971_1980
    
    def test_update_vacant_houses(self):
        """空き家データの更新テスト（INSERT OR REPLACE）"""
        self.db.insert_city_town("19201", "甲府市")
        
        # 初期データの挿入
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
        self.db.insert_vacant_houses(vacant_data)
        
        # 更新用データ
        vacant_data_updated = {
            'c_t_code': '19201',
            'year': 2023,
            'total_house': 105000,
            'total_vacant': 16000,
            'rent': 5500,
            'sale': 2200,
            'second_use': 3100,
            'other_vacant': 5200
        }
        self.db.insert_vacant_houses(vacant_data_updated)
        
        # 
        result = self.db.get_vacant_houses_by_city("19201")
        
        # 1件のみ存在し、値が更新されていることを確認
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][2], 105000)  # total_house
        self.assertEqual(result[0][3], 16000)   # total_vacant
    
    def test_data_consistency(self):
        """データの一貫性テスト"""
        # 市町村登録
        self.db.insert_city_town("19201", "甲府市")
        
        # 住宅データの挿入
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
        self.db.insert_vacant_houses(vacant_data)
        
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
        self.db.insert_house_age(age_data)
        
        # データの整合性チェック (住宅総数 = 築年数別の合計)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    vh.total_house,
                    (ha.pre_1970 + ha.y1971_1980 + ha.y1981_1990 + 
                     ha.y1991_2000 + ha.y2001_2010 + ha.y2011_2020 + ha.y2021_2023) as age_total
                FROM vacant_houses vh
                JOIN house_age ha 
                ON vh.c_t_code = ha.c_t_code AND vh.year = ha.year
                WHERE vh.c_t_code = '19201'
            """)
            result = cursor.fetchone()
            
            total_house = result[0]
            age_total = result[1]
            
            # 合計が一致することを検証
            self.assertEqual(total_house, age_total, 
                           f"住宅総数({total_house})と築年数合計({age_total})が一致しません")
    
    def test_multiple_years_data(self):
        """複数年のデータ挿入テスト"""
        self.db.insert_city_town("19201", "甲府市")
        
        # 複数年（2018年、2023年）のデータを挿入
        for year in [2018, 2023]:
            vacant_data = {
                'c_t_code': '19201',
                'year': year,
                'total_house': 100000 + (year - 2018) * 5000,
                'total_vacant': 15000 + (year - 2018) * 1000,
                'rent': 5000,
                'sale': 2000,
                'second_use': 3000,
                'other_vacant': 5000 + (year - 2018) * 1000
            }
            self.db.insert_vacant_houses(vacant_data)
        
        # DBから全期間のデータを取得
        result = self.db.get_vacant_houses_by_city("19201")
        
        # 2年分存在することを確認
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][1], 2018)
        self.assertEqual(result[1][1], 2023)
    
    def test_foreign_key_constraint(self):
        """外部キー制約のテスト"""
        vacant_data = {
            'c_t_code': '99999',  # 存在しない地域コード
            'year': 2023,
            'total_house': 100000,
            'total_vacant': 15000,
            'rent': 5000,
            'sale': 2000,
            'second_use': 3000,
            'other_vacant': 5000
        }
        
        with self.db.get_connection() as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            
            with self.assertRaises(sqlite3.IntegrityError):
                cursor.execute("""
                    INSERT INTO vacant_houses 
                    (c_t_code, year, total_house, total_vacant, rent, sale, 
                     second_use, other_vacant)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    vacant_data['c_t_code'],
                    vacant_data['year'],
                    vacant_data['total_house'],
                    vacant_data['total_vacant'],
                    vacant_data['rent'],
                    vacant_data['sale'],
                    vacant_data['second_use'],
                    vacant_data['other_vacant']
                ))
    
    def test_empty_database(self):
        """空のデータベースのクエリテスト"""
        cities = self.db.get_all_cities()
        self.assertEqual(len(cities), 0)
        
        result = self.db.get_vacant_houses_by_city("19201")
        self.assertEqual(len(result), 0)


class TestScraper(unittest.TestCase):
    """スクレイピング機能のテストケース（後で実装）"""
    
    def test_placeholder(self):
        """プレースホルダー"""
        self.assertTrue(True)


def run_all_tests():
    """全テストを実行する関数"""
    print("="*70)
    print(" - ")
    print("="*70)
    print()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestScraper))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print("")
    print("="*70)
    print(f": {result.testsRun}")
    print(f": {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f": {len(result.failures)}")
    print(f": {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n[SUCCESS] 全てのユニットテストに合格しました！")
        
        # 
        import sqlite3
        db_path = "vacant_house.db"
        if os.path.exists(db_path):
            print("\n" + "="*70)
            print("実データ整合性チェック (山梨県全体 vs 市町村合計)")
            print("="*70)
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # --- 1. 空き家総数の整合性チェック ---
                print("\n1. 空き家総数 (total_vacant) の照合")
                cursor.execute("SELECT total_vacant FROM vacant_houses WHERE c_t_code = '19000' AND year = 2023")
                pref_row = cursor.fetchone()
                pref_val = pref_row[0] if pref_row else 0
                
                cursor.execute("SELECT SUM(total_vacant) FROM vacant_houses WHERE c_t_code != '19000' AND year = 2023")
                cities_sum = cursor.fetchone()[0] or 0
                
                print(f"山梨県(19000) 公表値 : {pref_val:10,}")
                print(f"市町村合計 算出値     : {cities_sum:10,}")
                print(f"差異                : {pref_val - cities_sum:10,}")

                # --- 2. 空き家の内訳合計チェック ---
                print("\n2. 空き家の種類別内訳の整合性チェック")
                print("(各市町村: 空き家総数 = 賃貸 + 売却 + 二次的 + その他)")
                
                cursor.execute("""
                    SELECT c_t_code, total_vacant, (rent + sale + second_use + other_vacant) as calculated_sum 
                    FROM vacant_houses 
                    WHERE year = 2023
                """)
                rows = cursor.fetchall()
                errors = 0
                for code, actual, calc in rows:
                    if actual != calc:
                        print(f"不一致検出 [{code}]: 公表値={actual:8,}, 算出合計={calc:8,}, 差異={actual-calc:5,}")
                        errors += 1
                
                if errors == 0:
                    print("全ての市町村で内訳の合計が一致しました。")
                else:
                    print(f"注意: {errors} 件の市町村で内訳の合計に差異があります（統計上の端数処理等の可能性があります）。")

                # --- 3. 築年数データの整合性チェック ---
                print("\n3. 築年数データ（1970年以前）の照合")
                cursor.execute("SELECT pre_1970 FROM house_age WHERE c_t_code = '19000' AND year = 2023")
                pref_row = cursor.fetchone()
                pref_val = pref_row[0] if pref_row else 0
                
                cursor.execute("SELECT SUM(pre_1970) FROM house_age WHERE c_t_code != '19000' AND year = 2023")
                cities_sum = cursor.fetchone()[0] or 0
                
                print(f"山梨県(19000) 公表値 : {pref_val:10,}")
                print(f"市町村合計 算出値     : {cities_sum:10,}")
                print(f"差異                : {pref_val - cities_sum:10,}")
                
                conn.close()
            except Exception as e:
                print(f" : {e}")
    else:
        print("\n ")
    
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)