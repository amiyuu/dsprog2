#地域選択画面

import sys
from pathlib import Path

# このファイルを直接実行する場合、親ディレクトリをパスに追加
if __name__ == "__main__":
    # 現在のファイルの親の親ディレクトリ（weather-forecast-app）をパスに追加
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

import flet as ft
from services.jma_api import JmaApiService

class AreaListView(ft.View):
    #地域選択画面のクラス
    
    def __init__(self, page: ft.Page, on_area_selected):
        
        #viewの初期化（最初に呼ぶ）
        super().__init__(
            route="/area-list",
            controls=[]
        )
        
        #ページとコールバックを保存
        self.page = page
        self.on_area_selected = on_area_selected
        
        #地域データ
        self.areas_data = None
        self.selected_area_code = None
        
        #検索用
        self.search_query = ""
        
        #UI要素
        self.search_field = None
        self.area_list_column = None
        self.select_button = None
        
        #UIを構築
        self.build_ui()
        
        #地域データの読み込み
        self._load_areas()
        
    def build_ui(self):
        #uiの構築
        
        title = ft.Text(
            "地域を選択してください",
            size = 24,
            weight = ft.FontWeight.BOLD,
        )
        
        #検索ボックス
        self.search_field = ft.TextField(
            label = '地域名で検索',
            prefix_icon=ft.Icons.SEARCH,
            on_change = self._on_search_changed,
            width = 400,         
            
        )
        
        #地域名リストのカラム
        self.area_list_column = ft.Column(
            controls =[
                ft.ProgressRing()
            ],
        scroll = ft.ScrollMode.AUTO,
        height = 400,
        )
        
        #選択ボタン
        self.select_button = ft.ElevatedButton(
            text = 'この地域の天気を見る',
            icon = ft.Icons.ARROW_FORWARD,
            on_click = self._on_select_clicked,
            disabled = True,#最初は無効
        )
        
        #全てのコントロールをViewに追加
        self.controls = [
            ft.Container(
                content = ft.Column(
                    controls = [
                        title,
                        ft.Divider(),
                        self.search_field,
                        self.area_list_column,
                        ft.Divider(),
                        self.select_button,
                    ],
                    spacing = 20,
                    horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                ),
                padding = 20,
            )
        ]
        
    def _load_areas (self):
        #地域データの読み込み（FROM　API）
        self.areas_data = JmaApiService.get_area_list()
        
        if self.areas_data:
            
            self._display_areas()
        else:
            self.area_list_column.controls = [
                ft.Text(
                    "地域リストの取得に失敗しました",
                    color = ft.colors.RED,
                )
            ]
            self._safe_update()
            
    def _display_areas(self):
        #地域リストを表示
        
        self.area_list_column.controls.clear()
        
        # centersから有効な地域コードを取得
        centers = self.areas_data.get('centers', {})
        valid_codes = set()
        for center_info in centers.values():
            valid_codes.update(center_info.get('children', []))
        
        # officesから地域を取得（有効なコードのみ）
        offices = self.areas_data.get('offices',{})
        offices = {
            code: info 
            for code, info in offices.items() 
            if code in valid_codes
        }
        
        #検索フィルターを適用
        if self.search_query:
            offices = {
                code: info 
                for code , info in offices.items()
                if self.search_query.lower() in info['name'].lower()
            }
            
        #地域が見つからないとき
        if not offices:
            self.area_list_column.controls.append(
                ft.Text("該当する地域が見つかりません")
            )
            self._safe_update()
            return
        
        #地域ごとにリストアイテムを作成
        for code, info in list(offices.items())[:20]:
            area_tile = ft.ListTile(
                title = ft.Text(info['name']),
                subtitle = ft.Text(f"コード：{code}"),
                leading = ft.Icon(ft.Icons.LOCATION_ON),
                on_click = lambda e, area_code = code: self._on_area_clicked(area_code),  
            )
            self.area_list_column.controls.append(area_tile)
            
            self._safe_update()
            
    def _on_area_clicked(self, area_code):
        #地域がクリックされた時
        
        
        #地域コードを保存
        self.selected_area_code = area_code
        
        #選択ボタンを有効化
        self.select_button.disabled = False
        
        #リストの選択状態を更新
        for control in self.area_list_column.controls:
            if isinstance(control, ft.ListTile):
                
                #選択された項目をハイライト
                if control.subtitle.value == f"コード：{area_code}":
                    control.bgcolor = ft.Colors.BLUE_100
                else:
                    control.bgcolor = None
        
        self._safe_update()
        
        
    def _on_search_changed(self,e):
        #検索ボックスの内容が変更されたとき
        
        self.search_query = e.control.value
        self._display_areas()
        
    def _on_select_clicked(self,e):
        #選択ボタンがクリックされた時
        
        if self.selected_area_code and self.on_area_selected:
            #コールバック関数を呼び出す
            self.on_area_selected(self.selected_area_code)
            
    def _safe_update(self):
        """安全にページを更新"""
        try:
            if self.page:
                self.page.update()
            else:
                self.update()
        except Exception as e:
            print(f"⚠️ 更新エラー: {e}")
            
#テストコード
if __name__ == "__main__":
    def test_area_selected(area_code):
        """テスト用のコールバック関数"""
        print(f"✅ 地域が選択されました: {area_code}")
    
    def main(page: ft.Page):
        """テスト用のメイン関数"""
        page.title = "地域選択画面テスト"
        page.window.width = 500
        page.window.height = 700
        
        # 地域選択画面を作成
        area_list_view = AreaListView(page, test_area_selected)
        
        # ページに追加
        page.views.append(area_list_view)
        page.update()
    
    # アプリを起動
    ft.app(target=main)