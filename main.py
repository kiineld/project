from kivy.animation import Animation
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.lang import Builder
from config import host, port, user, passkey, database
from kivy.config import Config
import re
import pymysql.cursors
import win32gui

Builder.load_file('registration.kv')
Builder.load_file('login.kv')
Builder.load_file('selection.kv')
Builder.load_file('mainField.kv')
Builder.load_file('set_selection_electricity.kv')
Builder.load_file('set_selection_mechanics.kv')
Builder.load_file('set_selection_optics.kv')
Config.set('input', 'mouse', 'mouse, multitouch_on_demand')

title = None

connection = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=passkey,
    database=database,
    cursorclass=pymysql.cursors.DictCursor
)

Window.maximize()
icons = []


class RegistrationScreen(Screen):
    def do_registration(self, instance):
        in_data_base = False
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        email = self.ids.email_input.text

        # проверка вводимой информации
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

        # поиск совпадений в базе данных
        with connection.cursor() as cursor:
            check_query = """SELECT * FROM users"""
            cursor.execute(check_query)
            rows = cursor.fetchall()
            for row in rows:
                if username == row['name'] or password == row['password'] or email == row['email']:
                    print("user in database")
                    in_data_base = True
                    break

       # запись нового пользователя в базу данных
        with connection.cursor() as cursor:
            if not in_data_base:
                insert_query = f"INSERT INTO users (name, password, email) VALUES ('{username}','{password}','{email}')"
                cursor.execute(insert_query)
            connection.commit()

        # переключение на следующий экран
        app = MDApp.get_running_app()
        if not in_data_base:
            app.root.current = "section_selection"
            app.root.transition.direction = "left"
        else:
            app.root.current = "login"
            app.root.transition.direction = "left"


class LoginScreen(Screen):
    def do_login(self, instance):
        app = MDApp.get_running_app()
        # получение введенного имени и пароля
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        # проверка вводимых данных
        with (connection.cursor() as cursor):
            check_query = """SELECT * FROM user_data"""
            cursor.execute(check_query)
            rows = cursor.fetchall()
            for row in rows:
                if username == row['name']:
                    if password == row['password']:
                        print(f"success, пользователь {username} с паролем: {password}")
                        app.root.current = "section_selection"
                        app.root.transition.direction = "left"
                        break


class ScreenSelection(Screen):
    pass


class DraggableElement(Image):
    global icons
    initial_position = None  # начальная позиция первого элемента
    dragged_elements = []  # cписок для хранения уже перетащенных элементов
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (50, 50)  # размер элемента
        self.dragging = False  # флаг перетаскивания
        self.touch_offset = None  # смещение при перетаскивании

    # def create_duplicate(self):
    #     # создание дупликата
    #     duplicate = DraggableElement(source=self.source)
    #     duplicate.size = self.size
    #     duplicate.pos = self.initial_position
    #     return duplicate

    def on_touch_down(self, touch):
        # обработка клика на элемент
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                self.dragging = False
                self.angle += 90
                self.angle = (self.angle % 360)

            if touch.button == 'right':
                # print("KRASNYA POINT")
                self.dragging = False
                self.parent.remove_widget(self)
                icons.remove(self)

            else:
                self.dragging = True
                self.touch_offset = (self.pos[0] - touch.pos[0], self.pos[1] - touch.pos[1])
                if not self.initial_position:
                    self.initial_position = tuple(self.pos)

        else:
            if touch.button == 'right':
                # print("KRASNYA POINT")
                self.dragging = False

    def on_touch_move(self, touch):
        # обработка перемещения
        if self.dragging and touch.button == "left":
            # print("MOVING")
            for icon in icons:
                print(icon.pos, end=' ')
            print()
            self.pos = (touch.pos[0] + self.touch_offset[0], touch.pos[1] + self.touch_offset[1])

    def on_touch_up(self, touch):
        # обработка отпускания
        if self.collide_point(*touch.pos):
            self.dragging = False
            self.dragged_elements.append(self)
            # округление координат к ближайшим точкам сетки
            cell_size = 50
            if self.pos[0] % cell_size >= cell_size / 2:
                new_x = (int(self.pos[0] / cell_size) + 1) * cell_size
            else:
                new_x = int(self.pos[0] / cell_size) * cell_size
            if self.pos[1] % cell_size >= cell_size / 2:
                new_y = (int(self.pos[1] / cell_size) + 1) * cell_size
            else:
                new_y = int(self.pos[1] / cell_size) * cell_size
            self.pos = (new_x, new_y) # перемещение элемента в ближайшую точку сетки
            # создание дубликата элемента на первоначальном месте
            # duplicate_element = self.create_duplicate()
            # self.parent.add_widget(duplicate_element)


class MechanicsScreen(Screen):
    pass


class ElectricityScreen(Screen):
    global icons

    def __init__(self, **kwargs):
        global title
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.title = self.ids.top_bar.title
        self.canvas.before.add(Color(0.9, 0.9, 0.9, 1))
        self.canvas.before.add(Line(width=1.5))

        cell_size = 50  # размер ячейки сетки
        win_width, win_height = Window.size

        for i in range(int(win_width / cell_size) + 1):  # вертикальные линии
            x = i * cell_size
            self.canvas.before.add(Line(points=[x, 0, x, win_height], width=1))
        for i in range(int(win_height / cell_size) + 1):  # горизонтальные линии
            y = i * cell_size
            self.canvas.before.add(Line(points=[0, y, win_width, y], width=1))

        # horizontal_wire = DraggableElement(source="images/horizontal_wire.png")
        # horizontal_wire.pos = (250, 10)
        # self.add_widget(horizontal_wire)
        # self.icons.append(horizontal_wire)
        #
        # vertical_wire = DraggableElement(source="images/vertical_wire.png")
        # vertical_wire.pos = (310, 10)
        # self.add_widget(vertical_wire)
        # self.icons.append(vertical_wire)
        #
        # resistor = DraggableElement(source="images/resistor.png")
        # resistor.pos = (10, 10)
        # self.add_widget(resistor)
        # self.icons.append(resistor)
        #
        # voltmeter = DraggableElement(source="images/voltmeter.png")
        # voltmeter.pos = (70, 10)
        # self.add_widget(voltmeter)
        # self.icons.append(voltmeter)
        #
        # ammeter = DraggableElement(source="images/ammeter.png")
        # ammeter.pos = (130, 10)
        # self.add_widget(ammeter)
        # self.icons.append(ammeter)
        #
        # source = DraggableElement(source="images/source.png")
        # source.pos = (190, 10)
        # self.add_widget(source)
        # self.icons.append(source)

    def go_back(self):
        print("logout")
        app = MDApp.get_running_app()
        app.root.transition.direction = "right"
        app.root.current = "set_selection_electricity"

    def open_account(self):
        print("account")

    def change(self, number):
        self.ids.top_bar.title = str(number)

    def check_scheme(self):
        popup = Popup(title='Ошибка', content=Label(text='Неправильная схема!'), size_hint=(None, None), size=(200, 100))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168/255, 228/255, 160/255, 1).rgba
        popup.open()

    def make_element(self, element_path):
        element = DraggableElement(source=element_path)
        window_handle = win32gui.FindWindow(None, "Physics")
        window_rect = win32gui.GetWindowRect(window_handle)
        width = window_rect[2] - window_rect[0]
        height = window_rect[3] - window_rect[1]
        element.pos = [width / 2, height / 2]
        self.add_widget(element)
        for icon in icons:
            if element.pos == icon.pos:
                element.pos = [icon.pos[0], icon.pos[1] + 50]
        icons.append(element)


class OpticsScreen(Screen):
    pass


class SetScreenElectricity(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SetScreenMechanics(Screen):
    pass


class SetScreenOptics(Screen):
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

        set_selection_electricity = SetScreenElectricity(name="set_selection_electricity")
        screen_manager.add_widget(set_selection_electricity)

        set_selection_mechanics = SetScreenMechanics(name="set_selection_mechanics")
        screen_manager.add_widget(set_selection_mechanics)

        set_selection_optics = SetScreenOptics(name="set_selection_optics")
        screen_manager.add_widget(set_selection_optics)

        return screen_manager


if __name__ == '__main__':
    PhysicsApp().run()
