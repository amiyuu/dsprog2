#科学計算機能を５つ以上実装する
#平方根 √x
#べき乗 x ^ 2
# 対数(log x)
# 三角関数（sin con tan）
# 円周率(π)

import flet as ft
import math

class CalcButton(ft.ElevatedButton):
    def __init__(self, text,button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text

class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.Colors.WHITE24
        self.color = ft.Colors.WHITE

class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.ORANGE
        self.color = ft.Colors.WHITE

class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.BLUE_GREY_100
        self.color = ft.Colors.BLACK
        
class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()

        self.power = False
        self.sqrt = False
        self.log = False
        self.sin = False
        self.cos = False
        self.tan = False
        
        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=20)
        self.width = 350
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),
                ft.Row(
                    controls=[
                        ExtraActionButton(
                            text="AC", button_clicked=self.button_clicked
                        ),
                        ExtraActionButton(
                            text="+/-", button_clicked=self.button_clicked
                        ),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="√x", button_clicked=self.button_clicked),
                        ExtraActionButton(text="x^2", button_clicked=self.button_clicked),
                        ExtraActionButton(text="logx", button_clicked=self.button_clicked),
                        ExtraActionButton(text="π", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="tanx", button_clicked=self.button_clicked),
                        ExtraActionButton(text="cosx", button_clicked=self.button_clicked),
                        ExtraActionButton(text="sinx", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(
                            text="0", expand=2, button_clicked=self.button_clicked
                        ),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
            ]
        )
        
    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data}")
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()

        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            if self.result.value == "0" or self.new_operand == True:
                self.result.value = data
                self.new_operand = False
            else:
                self.result.value = self.result.value + data         
                       
        elif data in ("+", "-", "*", "/"):
            self.result.value = self.calculate(
                self.operand1, float(self.result.value), self.operator
            )
            self.operator = data
            if self.result.value == "Error":
                self.operand1 = "0"
            else:
                self.operand1 = float(self.result.value)
            self.new_operand = True

        elif data in ("="):
            self.result.value = self.calculate(
                self.operand1, float(self.result.value), self.operator)
            
            if self.sqrt:   #平方根
                if float(self.result.value) >= 0:
                    self.result.value = math.sqrt(float(self.result.value))
                    self.reset()
                    self.sqrt = False
                else:
                    self.result.value = "Error"
                    self.reset()
                    self.sqrt = False
                    
            if self.power:  #２乗の計算
                self.result.value = float(self.result.value)**2
                self.reset()
                self.power = False
            
            if self.log:    #対数関数
                if float(self.result.value) >0:
                    self.result.value = math.log(float(self.result.value))
                    self.reset()
                    self.log = False
                else:
                    self.result.value = "Error"
                    self.reset()
                    self.log = False
                
            if self.sin:    #三角関数(sin)
                self.result.value = round(math.sin(math.radians(float(self.result.value))),10)
                self.reset()
                self.sin = False
                
            if self.cos:    #三角関数(cos)
                self.result.value = round(math.cos(math.radians(float(self.result.value))),10)
                self.reset()
                self.cos = False
                
            if self.tan:    #三角関数(tan)
                self.result.value = round(math.tan(math.radians(float(self.result.value))),10)
                self.reset()
                self.tan = False

        elif data in ("%"):
            self.result.value = float(self.result.value) / 100
            self.reset()

        elif data in ("+/-"):
            if float(self.result.value) > 0:
                self.result.value = "-" + str(self.result.value)

            elif float(self.result.value) < 0:
                self.result.value = str(
                    self.format_number(abs(float(self.result.value)))
                )
 
 
        elif data in ("√x"):
            self.sqrt = True
            self.new_operand = True    
            
        elif data in ("x^2"):
            self.power = True
            self.new_operand = True    
        
        elif data in ("logx"):
            self.log = True   
            self.new_operand = True    
        
        elif data in ("π"):     #円周率
            self.result.value = round(math.pi,5)
                
        elif data in ("sinx"):
            self.sin = True
            self.new_operand = True  
                
        elif data in ("cosx"):
            self.cos = True  
            self.new_operand = True
        
        elif data in ("tanx"):
            self.tan = True    
            self.new_operand = True      
        self.update()

    def format_number(self, num):
        if num % 1 == 0:
            return int(num)
        else:
            return num

    def calculate(self, operand1, operand2, operator):

        if operator == "+":
            return self.format_number(operand1 + operand2)

        elif operator == "-":
            return self.format_number(operand1 - operand2)

        elif operator == "*":
            return self.format_number(operand1 * operand2)

        elif operator == "/":
            if operand2 == 0:
                return "Error"
            else:
                return self.format_number(operand1 / operand2)

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True

def main(page: ft.Page):
    page.title = "Calc App"
    calc = CalculatorApp()
    page.add(calc)


ft.app(main)