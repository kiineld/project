from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Line
from kivy.uix.widget import Widget
from kivy.uix.image import Image

from config import host, port, user, passkey, database
import re
import pymysql.cursors

connection = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=passkey,
    database=database,
    cursorclass=pymysql.cursors.DictCursor
)
Window.maximize()


class RegistrationScreen(Screen):
    def do_registration(self, instance):
        in_data_base = False
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        email = self.ids.email_input.text

        # if len(username.split()) != 2:
        #     print("Имя пользователя должно состоять из 2-ух слов: фамилии и имени")
        #     return
        # if not username.split()[0].isalpha() or not username.split()[1].isalpha():
        #     print("Имя пользователя не может включать символы помимо букв")
        #     return

        # if len(password) < 6:
        #     print("Пароль должен содержать не менее 6 символов")
        #     return

        # if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        #     print("Неправильный формат адреса электронной почты")
        #     return

        print(f"Зарегистрирован {username} с паролем: {password} и почтой: {email}")

        with (connection.cursor() as cursor):
            check_query = """SELECT * FROM users"""
            cursor.execute(check_query)
            rows = cursor.fetchall()
            for row in rows:
                if username == row['name'] or password == row['password'] or email == row['email']:
                    print("user in database")
                    in_data_base = True
                    break

        with connection.cursor() as cursor:
            if not in_data_base:
                insert_query = f"INSERT INTO users (name, password, email) VALUES ('{username}','{password}','{email}')"
                cursor.execute(insert_query)
            connection.commit()

        app = MDApp.get_running_app()
        if not in_data_base:
            app.root.current = "section_selection"
        else:
            app.root.current = "login"


class LoginScreen(Screen):
    def do_login(self, instance):
        app = MDApp.get_running_app()
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        with (connection.cursor() as cursor):
            check_query = """SELECT * FROM users"""
            cursor.execute(check_query)
            rows = cursor.fetchall()
            for row in rows:
                if username == row['name']:
                    if password == row['password']:
                        print(f"success, пользователь {username} с паролем: {password}")
                        app.root.current = "section_selection"
                        break


class ScreenSelection(Screen):
    def open_section1(self):
        self.manager.current = "mechanics"
        print("Open section: Mechanics")

    def open_section2(self):
        self.manager.current = "electricity"
        print("Open section: Electricity")

    def open_section3(self):
        self.manager.current = "optics"
        print("Open section: Optics")


class PaintWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 1, 1, 1)
            self.line = Line(points=())

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            with self.canvas:
                Color(0, 0, 0, 1)
                self.line.points += (touch.x, touch.y)
                touch.ud['line'] = self.line
            return True

    def on_touch_move(self, touch):
        if 'line' in touch.ud:
            touch.ud['line'].points += (touch.x, touch.y)


class DraggableElement(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (50, 50)  #размер элемента
        self.dragging = False  #флаг перетаскивания элемента
        self.touch_offset = None  #смещение при перетаскивании

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dragging = True
            self.touch_offset = (self.pos[0] - touch.pos[0], self.pos[1] - touch.pos[1])
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if hasattr(self, 'dragging') and self.dragging:
            self.pos = (touch.pos[0] + self.touch_offset[0], touch.pos[1] + self.touch_offset[1])
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if hasattr(self, 'dragging') and self.dragging:
            self.dragging = False
            return True
        return super().on_touch_up(touch)


class PaintElectricity(MDApp):
    def build(self):
        root = BoxLayout(orientation='vertical')
        paint_widget = PaintWidget()
        root.add_widget(paint_widget)
        icons_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        for i in range(4):
            icon = DraggableElement(source=f'icon{i}.png')
            icons_box.add_widget(icon)
        root.add_widget(icons_box)
        return root


class MechanicsScreen(Screen):
    pass


class ElectricityScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.icons = []

        resistor = DraggableElement(source='C:\\Users\\Саша\\Downloads\\resistor.png')
        resistor.pos = (10, 10)
        self.add_widget(resistor)
        self.icons.append(resistor)

        voltmeter = DraggableElement(source='C:\\Users\\Саша\\Downloads\\voltmeter.png')
        voltmeter.pos = (70, 10)
        self.add_widget(voltmeter)
        self.icons.append(voltmeter)

        ammeter = DraggableElement(source='C:\\Users\\Саша\\Downloads\\ammeter.png')
        ammeter.pos = (130, 10)
        self.add_widget(ammeter)
        self.icons.append(ammeter)

        source = DraggableElement(source='C:\\Users\\Саша\\Downloads\\source.png')
        source.pos = (190, 10)
        self.add_widget(source)
        self.icons.append(source)


class OpticsScreen(Screen):
    pass


class RegistrationApp(MDApp):
    def build(self):
        screen_manager = ScreenManager()

        login_screen = LoginScreen(name="login")
        screen_manager.add_widget(login_screen)

        registration_screen = RegistrationScreen(name="registration")
        screen_manager.add_widget(registration_screen)

        mechanics_screen = MechanicsScreen(name="mechanics")
        screen_manager.add_widget(mechanics_screen)

        electricity_screen = ElectricityScreen(name="electricity")
        screen_manager.add_widget(electricity_screen)

        optics_screen = OpticsScreen(name="optics")
        screen_manager.add_widget(optics_screen)

        section_selection = ScreenSelection(name="section_selection")
        screen_manager.add_widget(section_selection)

        return screen_manager


if __name__ == '__main__':
    RegistrationApp().run()
    