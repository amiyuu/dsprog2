"""
山梨県空き家データ収集・格納の統合スクリプト（Excel対応版）
URL取得 → ダウンロード → DB格納を一括実行
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import pandas as pd
import time
import os
from pathlib import Path
from db_manage import VacantHouseDB


class VacantHouseDataCollector:
    """空き家データを収集・格納するクラス"""
    
    def __init__(self, headless=True, download_dir="data", db_path="vacant_house.db"):
        """
        初期化
        
        Args:
            headless (bool): 
            download_dir (str): 
            db_path (str): 
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.db = VacantHouseDB(db_path)
        
        # Chrome
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--blink-settings=imagesEnabled=false') # 
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        print("Chromeを起動中...")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(60)
        self.wait = WebDriverWait(self.driver, 45)
        print("ブラウザの準備が完了しました\n")
    
    def get_file_url(self, page_url, file_link_selector, wait_selector=None):
        """
        ExcelファイルのダウンロードURLを取得
        
        Args:
            page_url (str): URL
            file_link_selector (str): CSS
            wait_selector (str, optional): 
        
        Returns:
            str: URLNone
        """
        try:
            print(f"ページを読み込み中...")
            print(f"URL: {page_url}")
            self.driver.get(page_url)
            
            if wait_selector:
                print(f"要素の出現を待機中: {wait_selector}")
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
                )
            
            time.sleep(3)
            
            print(f"ダウンロードリンクを探索中: {file_link_selector}")
            file_link = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, file_link_selector))
            )
            
            file_url = file_link.get_attribute('href')
            
            if file_url:
                print(f"URLの取得に成功しました!")
                print(f"対象URL: {file_url}")
                return file_url
            else:
                print("エラー: 対象URLが見つかりませんでした")
                return None
        
        except Exception as e:
            print(f"URL取得中にエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def download_excel(self, url, filename):
        """
        URLからExcelファイルをダウンロード
        
        Args:
            url (str): URL
            filename (str): 
        
        Returns:
            str: 保存したファイルのパス（失敗時はNone）
        """
        try:
            print(f"ダウンロード開始: {filename}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
            
            output_path = self.download_dir / filename
            
            # Excelファイルを保存
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            file_size = output_path.stat().st_size
            print(f"保存完了: {output_path.name} ({file_size:,} bytes)")
            
            return str(output_path)
        
        except Exception as e:
            print(f"ダウンロードエラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def import_vacant_houses(self, excel_path, sheet_name=0):
        """空き家データのExcelをインポート (Table 1-2: 種類別)"""
        print(f": {excel_path}")
        try:
            # 
            raw_df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
            
            # 0_22_
            header_start_idx = None
            for i, row in raw_df.iterrows():
                row_str = " ".join(str(v) for v in row.values)
                # 0_, 22_, 221_
                if ("0_" in row_str or "22_" in row_str) and ("221_" in row_str or "222_" in row_str):
                    header_start_idx = i
                    break
            
            if header_start_idx is None:
                print("エラー: ヘッダー開始行が見つかりませんでした")
                return False

            print(f"ヘッダー開始行: {header_start_idx}")
            
            # データフレームとして読み込み
            df = pd.read_excel(
                excel_path, 
                sheet_name=sheet_name, 
                skiprows=header_start_idx + 1
            )
            # 列名を設定
            df.columns = [str(c) for c in raw_df.iloc[header_start_idx].values]
            
            print(f"総列数: {len(df.columns)}")
            print(f"最初の10列:")
            for i, col in enumerate(df.columns[:10]):
                print(f"  [{i}] {col}")
            
            # 
            import re
            
            def find_col_by_number(num_str):
                """"""
                pattern = rf'^{num_str}_'
                for col in df.columns:
                    if re.match(pattern, str(col)):
                        return col
                return None
            
            # 
            total_col = find_col_by_number("0")
            vacant_total_col = find_col_by_number("22")
            rent_col = find_col_by_number("222")
            sale_col = find_col_by_number("223")
            second_col = find_col_by_number("224")
            other_col = find_col_by_number("221")

            print(f"\n :")
            print(f"- (0_): {total_col}")
            print(f"- (22_): {vacant_total_col}")
            print(f"- (222_): {rent_col}")
            print(f"- (223_): {sale_col}")
            print(f"- (224_): {second_col}")
            print(f"- (221_): {other_col}")


            count = 0
            for i, row in df.iterrows():
                # 
                area_val = None
                for val in row.values:
                    s_val = str(val).strip()
                    if "_" in s_val and s_val.startswith("19"):
                        area_val = s_val
                        break
                
                if not area_val: continue

                code, name = area_val.split("_", 1)
                city_code = code.strip().zfill(5)[:5]
                city_name = name.strip()

                if any(k in city_name for k in ["県外", "不詳", "その他"]): continue

                self.db.insert_city_town(city_code, city_name)
                
                try:
                    def get_val(col_name):
                        if col_name is None: return 0
                        val = row.get(col_name)
                        if pd.isna(val): return 0
                        return self.to_int(val)

                    data = {
                        'c_t_code': city_code,
                        'year': 2023,
                        'total_house': get_val(total_col),
                        'total_vacant': get_val(vacant_total_col),
                        'rent': get_val(rent_col),
                        'sale': get_val(sale_col),
                        'second_use': get_val(second_col),
                        'other_vacant': get_val(other_col)
                    }

                    # 詳細ログ
                    if city_code in ["19000", "19201"]:
                        print(f"\nDEBUG [{city_name}]: code={city_code}")
                        print(f"- 総数: {data['total_house']}")
                        print(f"- 空き家数: {data['total_vacant']}")
                        print(f"- 内訳 (賃貸: {data['rent']}, 売却: {data['sale']}, 二次的: {data['second_use']}, その他: {data['other_vacant']})")
                        calc_sum = data['rent'] + data['sale'] + data['second_use'] + data['other_vacant']
                        print(f"- 算出合計: {calc_sum}")
                        print(f"- 差異: {data['total_vacant'] - calc_sum}")

                    self.db.insert_vacant_houses(data)
                    count += 1
                except Exception as e:
                    print(f"エラー（{city_name}）: {e}")
                    continue
            
            print(f"\nインポート完了: {count}件")
            return True
        except Exception as e:
            print(f": {e}")
            import traceback
            traceback.print_exc()
            return False

    def import_house_age(self, excel_path, sheet_name=0):
        """築年数データのExcelをインポート (Table 5-3: 縦並び・D列ターゲット)"""
        print(f": {excel_path}")
        try:
            raw_df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
            
            # 1. データ開始行を特定 (19xxx_ 形式の地域コードを探す)
            data_start_idx = None
            for i, row in raw_df.iterrows():
                row_str = " ".join(str(v) for v in row.values)
                if "19" in row_str and "_" in row_str:
                    data_start_idx = i
                    break
            
            if data_start_idx is None:
                print("エラー: 19xxx_ 形式のデータ開始行が見つかりませんでした")
                return False

            # 2. 対象列の特定 (D列 = インデックス3)
            target_col_idx = 3 # D列: 住宅数
            print(f"抽出対象: D列 (Index:3)")

            records = {} # {city_code: {fields...}}
            
            for i in range(data_start_idx, len(raw_df)):
                row = raw_df.iloc[i]
                
                # 19xxx_
                area_val = None
                for val in row.values:
                    s_val = str(val)
                    if "_" in s_val and s_val.startswith("19"):
                        area_val = s_val
                        break
                
                if not area_val: continue
                
                code, name = area_val.split("_", 1)
                city_code = code.strip().zfill(5)[:5]
                
                # ラベルの抽出 (年、以前、以降などのキーワードで判定)
                age_label = ""
                for val in row.values:
                    s_val = str(val)
                    if "年" in s_val or "以前" in s_val:
                        age_label = s_val
                        break
                
                if not age_label: continue

                # D列から数値を取得
                try:
                    raw_value = row[target_col_idx]
                    value = self.to_int(raw_value)
                except:
                    value = 0
                
                if city_code not in records:
                    records[city_code] = {
                        'c_t_code': city_code, 'year': 2023, 
                        'pre_1970':0, 'y1971_1980':0, 'y1981_1990':0, 
                        'y1991_2000':0, 'y2001_2010':0, 'y2011_2020':0, 'y2021_2023':0
                    }

                # カテゴリごとに振り分け
                if "1970" in age_label and "以前" in age_label: records[city_code]['pre_1970'] = value
                elif "1971" in age_label: records[city_code]['y1971_1980'] = value
                elif "1981" in age_label: records[city_code]['y1981_1990'] = value
                elif "1991" in age_label: records[city_code]['y1991_2000'] = value
                elif "2001" in age_label: records[city_code]['y2001_2010'] = value
                elif "2011" in age_label: records[city_code]['y2011_2020'] = value
                elif "2021" in age_label or "2023" in age_label: records[city_code]['y2021_2023'] = value

            # 3. DBへ一括登録
            count = 0
            for city_code, data in records.items():
                self.db.insert_house_age(data)
                count += 1
            
            print(f"DB格納完了: {count}件")
            return True
            
        except Exception as e:
            print(f"インポート中にエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            return False

    def to_int(self, val):
        """数値を安全に変換 (小数点やカンマに対応)"""
        import re
        try:
            if pd.isna(val) or val == "-" or val == "..." or val == "":
                return 0
            # 数値以外の文字を除去
            s_val = str(val).replace(',', '').strip()
            # 正規表現で数値を抽出
            match = re.search(r'([-+]?\d*\.?\d+)', s_val)
            if match:
                # 整数に変換
                return int(round(float(match.group(1))))
            return 0
        except:
            return 0
    
    def process_data(self, data_config):
        """
        データの取得・ダウンロード・格納を実行
        
        Args:
            data_config (dict): データ設定
                {
                    'page_url': 'https://...',
                    'file_link_selector': 'a[href$=".xlsx"]',
                    'wait_selector': 'table',
                    'filename': 'vacant_houses.xlsx',
                    'sheet_name': 0 or 'シート名',
                    'data_type': 'vacant_houses' or 'house_age',
                    'description': '空き家の種類別データ'
                }
        
        Returns:
            bool: 処理が成功した場合はTrue、失敗した場合はFalse
        """
        print("="*70)
        print(f"{data_config['description']}")
        print("="*70)
        print()
        
        # 1: URL
        print("1: ExcelURL")
        print("-" * 70)
        file_url = self.get_file_url(
            page_url=data_config['page_url'],
            file_link_selector=data_config['file_link_selector'],
            wait_selector=data_config.get('wait_selector')
        )
        
        if not file_url:
            print("エラー: ExcelファイルのURL取得に失敗しました")
            return False
        
        print()
        
        # 2: Excel
        print("2: Excel")
        print("-" * 70)
        file_path = self.download_excel(file_url, data_config['filename'])
        
        if not file_path:
            print("")
            return False
        
        print()
        
        # 3: 
        print("3: ")
        print("-" * 70)
        
        sheet_name = data_config.get('sheet_name', 0)
        
        if data_config['data_type'] == 'vacant_houses':
            success = self.import_vacant_houses(file_path, sheet_name)
        elif data_config['data_type'] == 'house_age':
            success = self.import_house_age(file_path, sheet_name)
        else:
            print(f": {data_config['data_type']}")
            return False
        
        if not success:
            print("エラー: データのインポートに失敗しました")
            return False
        
        print()
        print("データ処理が全て完了しました!")
        print()
        
        return True
    
    def close(self):
        """ブラウザを閉じる"""
        print("ブラウザを終了しています...")
        self.driver.quit()
        print("ブラウザを正常に終了しました\n")


def main():
    """メイン実行関数"""
    print("="*70)
    print("山梨県空き家データ自動収集システム")
    print("="*70)
    print()
    
    # ===================================================
    #  
    # ===================================================
    
    # 
    data_configs = [
        {
            # statInfId: 000040209842
            'page_url': 'https://www.e-stat.go.jp/stat-search/files?page=4&layout=dataset&stat_infid=000040209842',
            # 'file-download' 
            'file_link_selector': 'a[href*="file-download"][href*="000040209842"]',
            'wait_selector': 'body',
            'filename': 'vacant_houses.xlsx',
            'sheet_name': 0,
            'data_type': 'vacant_houses',
            'description': '空き家の種類別データの取得'
        },
        {
            # ID
            'page_url': 'https://www.e-stat.go.jp/stat-search/files?page=4&layout=dataset&stat_infid=000040209851',
            'file_link_selector': 'a[href*="file-download"][href*="000040209851"]',
            'wait_selector': 'body',
            'filename': 'house_age.xlsx',
            'sheet_name': 0,
            'data_type': 'house_age',
            'description': '住宅の建築時期別データの取得'
        }
    ]
    
    # ===================================================
    #  
    # ===================================================
    
    # 
    # データベースの初期化
    print("データベースを初期化中...")
    db = VacantHouseDB()
    db.initialize_database()
    print("データベースの準備が完了しました")
    print()
    
    # 
    # headless=False 
    collector = VacantHouseDataCollector(headless=True)
    
    try:
        # 
        success_count = 0
        
        for i, config in enumerate(data_configs, 1):
            print(f"\n{'='*70}")
            print(f"{i}/{len(data_configs)}")
            print(f"{'='*70}\n")
            
            if collector.process_data(config):
                success_count += 1
            
            # 
            if i < len(data_configs):
                time.sleep(3)
        
        # 実行結果のサマリー
        print("\n" + "="*70)
        print("処理結果サマリー")
        print("="*70)
        print(f"成功: {success_count}/{len(data_configs)} 件")
        print(f"失敗: {len(data_configs) - success_count}/{len(data_configs)} 件")
        
        if success_count == len(data_configs):
            print("\n全てのデータの取得・格納が完了しました。")
            print()
            print("確認コマンド:")
            print("python test.py を実行してデータの整合性を確認してください。")
        else:
            print("\n一部の処理でエラーが発生しました。ログを確認してください。")
    
    finally:
        collector.close()


if __name__ == "__main__":
    main()