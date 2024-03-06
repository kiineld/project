from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Line
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.utils import get_color_from_hex, get_hex_from_color
from kivy.lang import Builder
from config import host, port, user, passkey, database
import re
import pymysql.cursors

Builder.load_file('registration.kv')
Builder.load_file('login.kv')
Builder.load_file('selection.kv')

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

        if len(username.split()) != 2:
            print("Имя пользователя должно состоять из 2-ух слов: фамилии и имени")
            return
        if not username.split()[0].isalpha() or not username.split()[1].isalpha():
            print("Имя пользователя не может включать символы помимо букв")
            return

        if len(password) < 6:
            print("Пароль должен содержать не менее 6 символов")
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print("Неправильный формат адреса электронной почты")
            return

        print(f"Зарегистрирован {username} с паролем: {password} и почтой: {email}")

        with connection.cursor() as cursor:
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
            check_query = """SELECT * FROM user_data"""
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
    initial_position = None  # начальная позиция первого элемента
    dragged_elements = []  # cписок для хранения уже перетащенных элементов

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (50, 50)  # размер элемента
        self.dragging = False  # флаг перетаскивания элемента
        self.touch_offset = None  # смещение при перетаскивании

    def create_duplicate(self):
        duplicate = DraggableElement(source=self.source)
        duplicate.size = self.size
        duplicate.pos = self.initial_position
        return duplicate

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dragging = True
            self.touch_offset = (self.pos[0] - touch.pos[0], self.pos[1] - touch.pos[1])
            if not self.initial_position:
                self.initial_position = tuple(self.pos)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if hasattr(self, 'dragging') and self.dragging:
            self.pos = (touch.pos[0] + self.touch_offset[0], touch.pos[1] + self.touch_offset[1])
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.dragging = False
            self.dragged_elements.append(self)
            # Округление координат к ближайшим точкам сетки
            cell_size = 50
            if self.pos[0] % cell_size >= cell_size / 2:
                new_x = (int(self.pos[0] / cell_size) + 1) * cell_size
            else:
                new_x = int(self.pos[0] / cell_size) * cell_size

            if self.pos[1] % cell_size >= cell_size / 2:
                new_y = (int(self.pos[1] / cell_size) + 1) * cell_size
            else:
                new_y = int(self.pos[1] / cell_size) * cell_size
            # Перемещение элемента в ближайшую точку сетки
            self.pos = (new_x, new_y)
            # Создание дубликата элемента на первоначальном месте
            duplicate_element = self.create_duplicate()
            self.parent.add_widget(duplicate_element)
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

        self.orientation = "vertical"
        self.canvas.before.add(Color(0.9, 0.9, 0.9, 1))  # цвет фона
        self.canvas.before.add(Line(width=1.5))

        cell_size = 50  # размер ячейки сетки
        win_width, win_height = Window.size

        for i in range(int(win_width / cell_size) + 1):  # вертикальные линии
            x = i * cell_size
            self.canvas.before.add(Line(points=[x, 0, x, win_height], width=1))
        for i in range(int(win_height / cell_size) + 1):  # горизонтальные линии
            y = i * cell_size
            self.canvas.before.add(Line(points=[0, y, win_width, y], width=1))

        self.icons = []

        wire = DraggableElement(source="images/wire.png")
        wire.pos = (250, 10)
        self.add_widget(wire)
        self.icons.append(wire)

        resistor = DraggableElement(source="images/resistor.png")
        resistor.pos = (10, 10)
        self.add_widget(resistor)
        self.icons.append(resistor)

        voltmeter = DraggableElement(source="images/voltmeter.png")
        voltmeter.pos = (70, 10)
        self.add_widget(voltmeter)
        self.icons.append(voltmeter)

        ammeter = DraggableElement(source="images/ammeter.png")
        ammeter.pos = (130, 10)
        self.add_widget(ammeter)
        self.icons.append(ammeter)

        source = DraggableElement(source="images/source.png")
        source.pos = (190, 10)
        self.add_widget(source)
        self.icons.append(source)


class OpticsScreen(Screen):
    pass


class PhysicsApp(MDApp):
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
    PhysicsApp().run()
