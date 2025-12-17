import flet as ft
from views.area_list import AreaListView
from views.weather_detail import WeatherDetailView


class WeatherApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "天気予報アプリ"
        self.page.window.width = 600
        self.page.window.height = 800
        
        # 最初は地域選択画面を表示
        self.show_area_selection()
    
    def show_area_selection(self):
        print(" 地域選択画面を表示")
        
        # 既存のビューをクリア
        self.page.views.clear()
        
        # 地域選択画面を作成
        area_view = AreaListView(
            self.page,
            on_area_selected=self.show_weather_detail
        )
        
        # ビューを追加
        self.page.views.append(area_view)
        self.page.update()
    
    def show_weather_detail(self, area_code: str):
        print(f"🌤️ 天気詳細画面を表示: {area_code}")
        
        # 天気詳細画面を作成
        weather_view = WeatherDetailView(
            self.page,
            area_code,
            on_back=self.show_area_selection
        )
        
        # ビューを追加
        self.page.views.append(weather_view)
        self.page.update()


def main(page: ft.Page):
    app = WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)