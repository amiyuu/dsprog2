#天気予報の詳細画面

import sys
from pathlib import Path

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
import flet as ft
from services.jma_api import JmaApiService
from datetime import datetime


class WeatherDetailView(ft.View):
    #天気予報詳細画面のクラス
    
    def __init__(self, page: ft.Page,area_code : str, on_back):
        
        #viewの初期化
        super().__init__(
            route = "/weather_view/{area_code}",
            controls = []
            )
        
        # ページとコールバックを保存
        self.page = page
        self.area_code = area_code
        self.on_back = on_back
        
        #天気予報データ
        self.weather_data = None
        
        #ui要素
        self.build_ui()
        
        #天気予報データを読み込み
        self._load_weather()
    
    def build_ui(self):
        #ui要素を構築

        #タイトルバー
        title_bar = ft.Row(
            controls = [
                ft.IconButton(
                    icon = ft.Icons.ARROW_BACK,
                    on_click = lambda e: self.on_back(),
                    tooltip = "地域選択に戻る",
                ),
                ft.Text(
                    "天気予報",
                    size = 24,
                    weight = ft.FontWeight.BOLD
                    ),
            ],
            alignment = ft.MainAxisAlignment.START,
        )
        
        #コンテンツエリア（ローディング表示）
        self.content_column = ft.Column(
            controls = [
                ft.ProgressRing(),
                ft.Text("天気予報を読み込んでいます..."),
            ],
            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            spacing = 20,
        )    
    
        # 全てのコントロールをViewに追加
        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        title_bar,
                        ft.Divider(),
                        self.content_column,
                    ],
                    spacing=20,
                ),
                padding=20,
            )
        ]
        
    def _load_weather(self):
        #天気予報データを読み込む
        print(f"🌤️ 天気予報を取得中: {self.area_code}")
        self.weather_data = JmaApiService().get_weather_forecast(self.area_code)
        
        if self.weather_data:
            print(" 天気予報取得成功")
            self._display_weather()
        else:
            print("❌ 天気予報取得失敗")
            self.content_column.controls = [
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=ft.Colors.RED),
                ft.Text(
                    "天気予報の取得に失敗しました",
                    size=18,
                    color=ft.Colors.RED,
                ),
                ft.ElevatedButton(
                    "地域選択に戻る",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: self.on_back(),
                ),
            ]
            self._safe_update()
            
    def _display_weather(self):
        #天気予報を表示
        
        self.content_column.controls.clear()
        
        #地域名を取得
        area_name = "不明な地域"
        if self.weather_data and len(self.weather_data) > 0:
            first_forecast = self.weather_data[0]
            publishing_office = first_forecast.get('publishingOffice', '')
            area_name = first_forecast.get('targetArea', area_name)
        
        # 地域名表示
        self.content_column.controls.append(
            ft.Text(
                f"{area_name}",
                size=20,
                weight=ft.FontWeight.BOLD,
            )
        )
        
        # 発表者情報
        if publishing_office:
            self.content_column.controls.append(
                ft.Text(
                    f"発表: {publishing_office}",
                    size=12,
                    color=ft.Colors.GREY_700,
                )
            )
        
        self.content_column.controls.append(ft.Divider())
        
        # 天気予報がない場合
        if not self.weather_data or len(self.weather_data) == 0:
            self.content_column.controls.append(
                ft.Text("この地域の天気予報は利用できません")
            )
            self._safe_update()
            return
        
        # 各予報期間の情報を表示
        for forecast in self.weather_data[:3]:  # 最大3件表示
            forecast_card = self._create_forecast_card(forecast)
            self.content_column.controls.append(forecast_card)
        
        # 更新ボタン
        self.content_column.controls.append(
            ft.ElevatedButton(
                "天気予報を更新",
                icon=ft.Icons.REFRESH,
                on_click=self._on_refresh_clicked, 
            )
        )
        
        self._safe_update()
        
    def _on_refresh_clicked(self, e):
        """更新ボタンがクリックされた時の処理"""
        print("🔄 更新ボタンがクリックされました")
    
        # ローディング表示に戻す
        self.content_column.controls = [
            ft.ProgressRing(),
            ft.Text("天気予報を更新中..."),
        ]
        self._safe_update()
    
        # 天気予報を再取得
        self._load_weather()
        
    def _create_forecast_card(self, forecast):
        """予報カードを作成"""
        
        # 期間情報
        time_defines = forecast.get('timeDefines', [])
        date_str = "日時不明"
        if time_defines and len(time_defines) > 0:
            try:
                dt = datetime.fromisoformat(time_defines[0].replace('Z', '+00:00'))
                date_str = dt.strftime('%m月%d日 %H:%M')
            except:
                date_str = time_defines[0]
        
        # 天気情報
        weathers = forecast.get('weathers', ['情報なし'])
        weather_text = weathers[0] if weathers else '情報なし'
        
        # 風情報
        winds = forecast.get('winds', ['情報なし'])
        wind_text = winds[0] if winds else '情報なし'
        
        # 波情報
        waves = forecast.get('waves', ['情報なし'])
        wave_text = waves[0] if waves else '情報なし'
        
        # カードを作成
        card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            date_str,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Divider(height=1),
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.WB_SUNNY, size=20),
                                ft.Text(f"天気: {weather_text}"),
                            ],
                        ),
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.AIR, size=20),
                                ft.Text(f"風: {wind_text}"),
                            ],
                        ),
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.WAVES, size=20),
                                ft.Text(f"波: {wave_text}"),
                            ],
                        ),
                    ],
                    spacing=10,
                ),
                padding=15,
            ),
        )
        
        return card
    
    def _safe_update(self):
        """安全にページを更新"""
        try:
            if self.page:
                self.page.update()
            else:
                self.update()
        except Exception as e:
            print(f"⚠️ 更新エラー: {e}")

# テストコード
if __name__ == "__main__":
    def test_back():
        """テスト用の戻るボタン"""
        print("⬅️ 戻るボタンがクリックされました")
    
    def main(page: ft.Page):
        """テスト用のメイン関数"""
        page.title = "天気予報詳細画面テスト"
        page.window.width = 600
        page.window.height = 800
        
        # 天気予報画面を作成（東京を例に）
        weather_view = WeatherDetailView(page, "130000", test_back)
        
        # ページに追加
        page.views.append(weather_view)
        page.update()
    
    # アプリを起動
    ft.app(target=main)