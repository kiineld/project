import pymysql
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.lang import Builder
from config import host, port, user, passkey, database
from kivy.config import Config
import re
# import pymysql.cursors
# import pyautogui
import tkinter
# from ctypes import windll, wintypes, byref
# import win32api
# import win32gui

Builder.load_file('registration.kv')
Builder.load_file('login.kv')
Builder.load_file('selection.kv')
Builder.load_file('mainField.kv')
Builder.load_file('opticsField.kv')
Builder.load_file('set_selection_electricity.kv')
Builder.load_file('set_selection_mechanics.kv')
Builder.load_file('account.kv')
Config.set('input', 'mouse', 'mouse, multitouch_on_demand')

title = None

# sudo /usr/local/mysql/support-files/mysql.server start
# /usr/local/mysql/bin/mysql -u root -p
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
graph = []
previous = ""
userr = ""
variant = 0
lenses = None
exists = False
account = None


class RegistrationScreen(Screen):
    def do_registration(self, instance):
        global userr
        in_data_base = False
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        email = self.ids.email_input.text

        # проверка вводимой информации
        if len(username.split()) != 2:
            print("Имя пользователя должно состоять из 2-ух слов: фамилии и имени")
            popup = Popup(title='Ошибка', content=Label(text='Имя пользователя должно состоять из 2-ух слов: фамилии и имени!'), size_hint=(0.4, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()
            return
        if not username.split()[0].isalpha() or not username.split()[1].isalpha():
            print("Имя пользователя не может включать символы помимо букв")
            popup = Popup(title='Ошибка', content=Label(text='Имя пользователя не может включать символы помимо букв!'), size_hint=(0.4, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()
            return

        if len(password) < 6:
            print("Пароль должен содержать не менее 6 символов")
            popup = Popup(title='Ошибка', content=Label(text='Пароль должен содержать не менее 6 символов!'), size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print("Неправильный формат адреса электронной почты")
            popup = Popup(title='Ошибка', content=Label(text='Неправильный формат адреса электронной почты!'), size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()
            return

        print(f"Зарегистрирован {username} с паролем: {password} и почтой: {email}")

        # поиск совпадений в базе данных
        with connection.cursor() as cursor:
            check_query = """SELECT * FROM users"""
            cursor.execute(check_query)
            rows = cursor.fetchall()
            for row in rows:
                if username == row['name'] or email == row['email']:
                    print("user in database")
                    in_data_base = True
                    break

       #запись нового пользователя в базу данных
        with connection.cursor() as cursor:
            if not in_data_base:
                insert_query = f"INSERT INTO users (name, password, email) VALUES ('{username}','{password}','{email}')"
                cursor.execute(insert_query)
            else:
                popup = Popup(title='Ошибка', content=Label(text='Пользователь уже есть в базе!'), size_hint=(0.2, 0.16))
                popup.overlay_color = Color(1, 1, 1, 0).rgba
                popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
                popup.open()
            connection.commit()

        # переключение на следующий экран
        app = MDApp.get_running_app()
        if not in_data_base:
            app.root.current = "section_selection"
            app.root.transition.direction = "left"
        else:
            self.ids.username_input.text = ''
            self.ids.password_input.text = ''
            self.ids.email_input.text = ''

        userr = username


class LoginScreen(Screen):
    def guest(self):
        global userr
        app = MDApp.get_running_app()
        userr = "гость"
        app.root.current = "section_selection"
        app.root.transition.direction = "left"

    def do_login(self, instance):
        global userr
        found = False
        app = MDApp.get_running_app()
        # получение введенного имени и пароля
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        # проверка вводимых данных
        with (connection.cursor() as cursor):
            check_query = """SELECT * FROM users"""
            cursor.execute(check_query)
            rows = cursor.fetchall()
            for row in rows:
                if username == row['name']:
                    if password == row['password']:
                        found = True
                        print(f"success, пользователь {username} с паролем: {password}")
                        userr = username
                        break
        if not found:
            popup = Popup(title='Ошибка', content=Label(text='Неправильные данные!'), size_hint=(0.2, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()
        else:
            app.root.current = "section_selection"
            app.root.transition.direction = "left"


class ScreenSelection(Screen):
    def go_back(self):
        print("logout")
        app = MDApp.get_running_app()
        app.root.transition.direction = "right"
        app.root.current = "login"

    def open_account(self):
        global userr
        global account
        print("account")
        global previous
        previous = "section_selection"
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "account_screen"
        account.update(userr)
        print(userr)


class DraggableElement(Image):
    global icons
    initial_position = None  # начальная позиция первого элемента
    dragged_elements = []  # cписок для хранения уже перетащенных элементов
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.double_tapped = False
        self.size_hint = (None, None)
        self.size = (50, 50)  # размер элемента
        self.dragging = False  # флаг перетаскивания
        self.touch_offset = None  # смещение при перетаскивании

    def on_touch_down(self, touch):
        # обработка клика на элемент
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                print("SOSISKA", end=' ')
                self.double_tapped = True

            else:
                self.double_tapped = False

            if touch.button == 'right':
                # print("KRASNYA POINT")
                self.dragging = False
                self.parent.remove_widget(self)
                icons.remove(self)

            else:
                self.dragging = True
                if self.double_tapped:
                    self.dragging = False
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

        if self.double_tapped:
            element = DraggableElement(source='images/horizontal_wire.png')
            element.pos = [touch.pos[0], touch.pos[1]]
            cell_size = 50
            if self.pos[0] % cell_size >= cell_size / 2:
                new_x = (int(element.pos[0] / cell_size) + 1) * cell_size
            else:
                new_x = int(element.pos[0] / cell_size) * cell_size
            if self.pos[1] % cell_size >= cell_size / 2:
                new_y = (int(element.pos[1] / cell_size) + 1) * cell_size
            else:
                new_y = int(element.pos[1] / cell_size) * cell_size
            element.pos = (new_x, new_y)
            self.add_widget(element)
            icons.append(element)

    def on_touch_up(self, touch):
        # обработка отпускания
        self.dragging = False
        self.double_tapped = False
        if self.collide_point(*touch.pos):
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

        if self.double_tapped:
            node = DraggableElement(source='images/node.png')
            node.pos = (touch.pos[0], touch.pos[1])
            self.add_widget(node)
            icons.append(node)
            # создание дубликата элемента на первоначальном месте
            # duplicate_element = self.create_duplicate()
            # self.parent.add_widget(duplicate_element)


class MechanicsScreen(Screen):
    pass


class ElectricityScreen(Screen):
    global icons
    global graph

    def __init__(self, **kwargs):
        global variant
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.ids.top_bar.title = "Электричество, комплект " + str(variant)
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

    def go_back(self):
        print("logout")
        app = MDApp.get_running_app()
        app.root.transition.direction = "right"
        app.root.current = "set_selection_electricity"

    def open_account(self):
        global previous
        print("account")
        previous = "electricity"
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "account_screen"

    def changed(self):
        global variant
        self.ids.top_bar.title = "Электричество, комплект" + str(variant)

    def check_scheme(self):
        popup = Popup(title='Ошибка', content=Label(text='Неправильная схема!'), size_hint=(0.16, 0.16))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168/255, 228/255, 160/255, 1).rgba
        popup.open()

    def clear_scheme(self):
        for icon in icons:
            self.remove_widget(icon)
        icons.clear()

    def make_element(self, element_path):
        element = DraggableElement(source=element_path)
        # window_handle = win32gui.FindWindow(None, "Physics")
        # window_rect = win32gui.GetWindowRect(window_handle)
        # width = window_rect[2] - window_rect[0]
        # height = window_rect[3] - window_rect[1]
        width = 1920
        height = 1080
        element.pos = [width / 2, height / 2]
        self.add_widget(element)
        for icon in icons:
            if element.pos == icon.pos:
                element.pos = [icon.pos[0], icon.pos[1] + 50]
        icons.append(element)


class OpticsScreen(Screen):
    global lenses

    def __init__(self, **kwargs):
        global variant
        super().__init__(**kwargs)
        self.lens_type = None
        self.rays_type = None
        self.items = []
        self.items_path = []
        self.items_rays = []
        self.focus = Line()
        self.orientation = "vertical"
        self.ids.top_bar.title = "Оптика, комплект " + str(variant)
        self.focus_distance = 0
        self.focus_line_inversed = None
        self.focus_inversed = None
        self.focus_mark = None
        self.focus_mark_inversed = None
        self.focus_line = Line()
        self.center_x = Window.size[0] / 2
        self.center_y = Window.size[1] / 2
        self.arrow_size = 20
        self.canvas.before.add(Color(0, 0, 0, 1))
        self.canvas.before.add(Line(points=[self.center_x - 900, self.center_y, self.center_x + 900, self.center_y], width=5))

    def change_lens(self, lens_type):
        for item in self.items:
            self.canvas.before.remove(item)
        self.items.clear()

        if lens_type == "conv":
            self.items.append(Line(points=[self.center_x, self.center_y - 300, self.center_x, self.center_y + 300], width=5))
            self.items.append(Line(points=[self.center_x - self.arrow_size, self.center_y - 300 + self.arrow_size, self.center_x,
                                  self.center_y - 300, self.center_x + self.arrow_size,
                                  self.center_y - 300 + self.arrow_size], width=5))
            self.items.append(Line(points=[self.center_x - self.arrow_size, self.center_y + 300 - self.arrow_size, self.center_x,
                                  self.center_y + 300, self.center_x + self.arrow_size,
                                  self.center_y + 300 - self.arrow_size], width=5))

        elif lens_type == "div":
            self.items.append(Line(points=[self.center_x, self.center_y - 300, self.center_x, self.center_y + 300], width=5))
            self.items.append(Line(points=[self.center_x - self.arrow_size, self.center_y - 300 - self.arrow_size, self.center_x,
                                  self.center_y - 300, self.center_x + self.arrow_size,
                                  self.center_y - 300 - self.arrow_size], width=5))
            self.items.append(Line(points=[self.center_x - self.arrow_size, self.center_y + 300 + self.arrow_size, self.center_x,
                                  self.center_y + 300, self.center_x + self.arrow_size,
                                  self.center_y + 300 + self.arrow_size], width=5))

    def make_lens(self, lens_type):
        self.lens_type = lens_type
        self.change_lens(lens_type)
        for item in self.items:
            self.canvas.before.add(item)

    def update_focus_distance(self):
        global exists
        if exists:
            self.canvas.before.remove(self.focus_line)
            self.canvas.before.remove(self.focus)
            self.canvas.before.remove(self.focus_line_inversed)
            self.canvas.before.remove(self.focus_inversed)
            self.remove_widget(self.focus_mark)
            self.remove_widget(self.focus_mark_inversed)

        if self.ids.focus_distance.text == "":
            self.focus_distance = 0
        else:
            self.focus_distance = int(self.ids.focus_distance.text)

        if self.focus_distance <= 0:
            popup = Popup(title='Ошибка', content=Label(text='Фокусное расстояние не может быть меньше 0!'), size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()
            exists = False
        else:
            self.focus_distance = int(self.ids.focus_distance.text)
            print(self.focus_distance)
            focus_x = self.center_x + self.focus_distance
            focus_y = self.center_y

            self.focus_line = Line(points=[self.center_x, self.center_y, focus_x, focus_y], width=7)
            self.canvas.before.add(self.focus_line)
            self.focus = Line(points=[focus_x, focus_y - 20, focus_x, focus_y, focus_x, focus_y + 20], width=7)

            self.focus_mark = Label()
            self.focus_mark_inversed = Label()
            self.focus_mark.text = "F"
            self.focus_mark_inversed.text = "F"
            self.focus_mark.pos = [self.pos[0] + self.focus_distance, self.pos[1] - 45]
            self.focus_mark_inversed.pos = [self.pos[0] - self.focus_distance, self.pos[1] - 45]
            self.focus_mark_inversed.font_size = 40
            self.focus_mark_inversed.color = [0, 0, 0, 1]
            self.focus_mark.font_size = 40
            self.focus_mark.color = [0, 0, 0, 1]

            self.canvas.before.add(self.focus)

            focus_x = self.center_x - self.focus_distance

            self.focus_line_inversed = Line(points=[self.center_x, self.center_y, focus_x, focus_y], width=7)
            self.canvas.before.add(self.focus_line_inversed)
            self.focus_inversed = Line(points=[focus_x, focus_y - 20, focus_x, focus_y, focus_x, focus_y + 20], width=7)
            self.canvas.before.add(self.focus_inversed)

            self.add_widget(self.focus_mark)
            self.add_widget(self.focus_mark_inversed)
            exists = True

    def change_rays(self, rays_type):
        self.rays_type = rays_type
        print(self.rays_type, self.lens_type)

        for item in self.items_rays:
            self.canvas.before.remove(item)
        self.items_rays.clear()

        if self.lens_type == "conv":
            if rays_type == "parallel":
                print("parallel")
                self.items_rays.append(
                    Line(points=[self.center_x - 900, self.center_y + 250, self.center_x, self.center_y + 250], width=5))
                self.items_rays.append(
                    Line(points=[self.center_x - 900, self.center_y + 125, self.center_x, self.center_y + 125], width=5))
                self.items_rays.append(
                    Line(points=[self.center_x - 900, self.center_y - 125, self.center_x, self.center_y - 125], width=5))
                self.items_rays.append(
                    Line(points=[self.center_x - 900, self.center_y - 250, self.center_x, self.center_y - 250], width=5))
            else:
                if self.focus_distance == 0:
                    popup = Popup(title='Ошибка', content=Label(text=f'Введите фокусное расстояние!'),
                                  size_hint=(0.3, 0.16))
                    popup.overlay_color = Color(1, 1, 1, 0).rgba
                    popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
                    popup.open()
                else:
                    print("inclined")
                    self.items_rays.append(
                        Line(points=[self.center_x - self.focus_distance, self.center_y, self.center_x, self.center_y + 250], width=5))
                    self.items_rays.append(
                        Line(points=[self.center_x - self.focus_distance, self.center_y, self.center_x, self.center_y + 125], width=5))
                    self.items_rays.append(
                        Line(points=[self.center_x - self.focus_distance, self.center_y, self.center_x, self.center_y - 125], width=5))
                    self.items_rays.append(
                        Line(points=[self.center_x - self.focus_distance, self.center_y, self.center_x, self.center_y - 250], width=5))
        else:
            if rays_type == "parallel":
                self.items_rays.append(
                    Line(points=[self.center_x - 900, self.center_y + 250, self.center_x, self.center_y + 250], width=5))
                self.items_rays.append(
                    Line(points=[self.center_x - 900, self.center_y + 125, self.center_x, self.center_y + 125], width=5))
                self.items_rays.append(
                    Line(points=[self.center_x - 900, self.center_y - 125, self.center_x, self.center_y - 125], width=5))
                self.items_rays.append(
                    Line(points=[self.center_x - 900, self.center_y - 250, self.center_x, self.center_y - 250], width=5))

    def make_rays(self, rays_type):
        self.change_rays(rays_type)
        for item in self.items_rays:
            self.canvas.before.add(item)

    def show_path(self):
        if self.focus_distance == 0:
            popup = Popup(title='Ошибка', content=Label(text=f'Введите фокусное расстояние!'),
                          size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

        for item in self.items_path:
            self.canvas.before.remove(item)
        self.items_path.clear()

        if self.lens_type == "conv":
            if self.rays_type == "parallel":
                self.items_path.append(
                    Line(points=[self.center_x, self.center_y + 250, self.center_x + self.focus_distance, self.center_y], width=5))
                self.items_path.append(
                    Line(points=[self.center_x, self.center_y + 125, self.center_x + self.focus_distance, self.center_y], width=5))
                self.items_path.append(
                    Line(points=[self.center_x, self.center_y - 125, self.center_x + self.focus_distance, self.center_y], width=5))
                self.items_path.append(
                    Line(points=[self.center_x, self.center_y - 250, self.center_x + self.focus_distance, self.center_y], width=5))
            else:
                self.items_path.append(
                    Line(points=[self.center_x, self.center_y + 250, self.center_x + 900, self.center_y + 250], width=5))
                self.items_path.append(
                    Line(points=[self.center_x, self.center_y + 125, self.center_x + 900, self.center_y + 125], width=5))
                self.items_path.append(
                    Line(points=[self.center_x, self.center_y - 125, self.center_x + 900, self.center_y - 125], width=5))
                self.items_path.append(
                    Line(points=[self.center_x, self.center_y - 250, self.center_x + 900, self.center_y - 250], width=5))
        else:
            if self.rays_type == "parallel":
                self.items_path.append(
                    Line(points=[self.center_x - self.focus_distance, self.center_y, self.center_x, self.center_y + 250], width=1))
                self.items_path.append(
                    Line(points=[self.center_x - self.focus_distance, self.center_y, self.center_x, self.center_y + 125], width=1))
                self.items_path.append(
                    Line(points=[self.center_x - self.focus_distance, self.center_y, self.center_x, self.center_y - 125], width=1))
                self.items_path.append(
                    Line(points=[self.center_x - self.focus_distance, self.center_y, self.center_x, self.center_y - 250], width=1))

                self.items_path.append(
                    Line(points=[self.center_x, self.center_y + 250, self.center_x + self.focus_distance, self.center_y + 500], width=5))
                self.items_path.append(
                    Line(points=[self.center_x, self.center_y + 125, self.center_x + self.focus_distance, self.center_y + 250], width=5))
                self.items_path.append(
                    Line(points=[self.center_x, self.center_y - 125, self.center_x + self.focus_distance, self.center_y - 250], width=5))
                self.items_path.append(
                    Line(points=[self.center_x, self.center_y - 250, self.center_x + self.focus_distance, self.center_y - 500], width=5))

        for item in self.items_path:
            self.canvas.before.add(item)

    def go_back(self):
        print("logout")
        app = MDApp.get_running_app()
        app.root.transition.direction = "right"
        app.root.current = "section_selection"

    def open_account(self):
        global previous
        print("account")
        previous = "optics"
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "account_screen"

    def count_optical_power(self):
        optical_power = 1 / self.focus_distance
        popup = Popup(title='Результат', content=Label(text=f'Оптическая сила = {optical_power:.3f}'),
                      size_hint=(0.3, 0.16))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()


class SetScreenElectricity(Screen):
    def go_back(self):
        print("logout")
        app = MDApp.get_running_app()
        app.root.transition.direction = "right"
        app.root.current = "section_selection"

    def open_account(self):
        print("account")
        global previous
        previous = "set_selection_electricity"
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "account_screen"

    def change(self, number):
        app = MDApp.get_running_app()
        global variant
        variant = number
        print()


class SetScreenMechanics(Screen):
    pass


class SetScreenOptics(Screen):
    def go_back(self):
        print("logout")
        app = MDApp.get_running_app()
        app.root.transition.direction = "right"
        app.root.current = "section_selection"

    def open_account(self):
        print("account")
        global previous
        previous = "set_selection_optics"
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "account_screen"

    def change(self, number):
        app = MDApp.get_running_app()
        global variant
        variant = number
        print()


class AccountScreen(Screen):
    def update(self, user):
        self.ids.sigma.text = f"Ваше имя: {user}"

    def go_back(self):
        global previous
        print(previous)
        app = MDApp.get_running_app()
        app.root.current = previous
        app.root.transition.direction = "right"


class PhysicsApp(MDApp):
    def build(self):
        global account
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

        account_screen = AccountScreen(name="account_screen")
        screen_manager.add_widget(account_screen)
        account = account_screen
        return screen_manager


if __name__ == '__main__':
    PhysicsApp().run()
