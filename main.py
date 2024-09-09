import math
import pymysql.cursors
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.properties import NumericProperty
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.lang import Builder
from config import host, port, user, passkey, database
from kivy.config import Config
import re


Builder.load_file('registration.kv')
Builder.load_file('login.kv')
Builder.load_file('selection.kv')
Builder.load_file('mechanics_frictionforce_Field.kv')
Builder.load_file('mechanics_fluctuations_Field.kv')
Builder.load_file('mechanics_blocks_Field.kv')
Builder.load_file('mechanics_archimedesforce_Field.kv')
Builder.load_file('mainField.kv')
Builder.load_file('opticsField.kv')
Builder.load_file('set_selection_mechanics.kv')
Builder.load_file('account.kv')
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
graph = []
previous = ""
userr = ""
variant = 0
lenses = None
exists = False
account = None
mechanics_frictionforce_screen = None
mechanics_fluctuations_screen = None
mechanics_blocks_screen = None
mechanics_archimedesforce_screen = None
electricity_screen = None
optics_screen = None
section_selection = None
set_selection_mechanics = None


class RegistrationScreen(Screen):
    def do_registration(self, instance):
        global userr
        in_data_base = False
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        email = self.ids.email_input.text

        # проверка вводимой информации
        if len(username.split()) != 2:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Имя пользователя должно состоять из 2-ух слов: фамилии и имени!',
                          font_size='17sp'), size_hint=(0.4, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()
            return

        if not username.split()[0].isalpha() or not username.split()[1].isalpha():
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Имя пользователя не может включать символы помимо букв!',
                          font_size='17sp'), size_hint=(0.4, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()
            return

        if len(password) < 6:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Пароль должен содержать не менее 6 символов!', font_size='17sp'),
                          size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Неправильный формат адреса электронной почты!', font_size='17sp'),
                          size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()
            return

        # поиск совпадений в базе данных
        with connection.cursor() as cursor:
            check_query = """SELECT * FROM users"""
            cursor.execute(check_query)
            rows = cursor.fetchall()
            for row in rows:
                if username == row['name'] or email == row['email']:
                    in_data_base = True
                    break

       # запись нового пользователя в базу данных
        with connection.cursor() as cursor:
            if not in_data_base:
                insert_query = f"INSERT INTO users (name, password, email) VALUES ('{username}','{password}','{email}')"
                cursor.execute(insert_query)
            else:
                popup = Popup(title='Ошибка', title_size='20sp',
                              content=Label(text='Пользователь уже есть в базе!', font_size='17sp'),
                              size_hint=(0.2, 0.16))
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
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        with (connection.cursor() as cursor):
            check_query = """SELECT * FROM users"""
            cursor.execute(check_query)
            rows = cursor.fetchall()
            for row in rows:
                if username == row['name']:
                    if password == row['password']:
                        found = True
                        userr = username
                        break
        if not found:
            popup = Popup(title='Ошибка', title_size='20sp', content=Label(text='Неправильные данные!',
                          font_size='17sp'), size_hint=(0.2, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()
        else:
            app.root.current = "section_selection"
            app.root.transition.direction = "left"


class ScreenSelection(Screen):
    def go_back(self):
        app = MDApp.get_running_app()
        app.root.transition.direction = "right"
        app.root.current = "login"

    def open_account(self):
        global userr
        global account
        global previous
        previous = "section_selection"
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "account_screen"
        account.update(userr)


pairs = []
pair = []
lines = []
result = []
x, y = None, None
backs = []


class DraggableElement(Image):
    global icons
    global pairs
    global lines
    initial_position = None  # начальная позиция первого элемента
    dragged_elements = []  # cписок для хранения уже перетащенных элементов
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.double_tapped = False
        self.pins = []
        self.pairs = []
        self.size_hint = (None, None)
        self.size = (50, 50)  # размер элемента
        self.dragging = False  # флаг перетаскивания
        self.touch_offset = None  # смещение при перетаскивании
        self.connected = None

    # обработка клика на элемент
    def on_touch_down(self, touch):
        global pair
        global backs
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                self.canvas.add(Color(0, 0, 0, 1))
                backs.append(self)
                pair.append(self)
                self.double_tapped = True
                if len(pair) == 2:
                    pr = [pair[0], pair[1]]
                    if (pr not in pairs) and (pair[0] != pair[1]) and (pr[::-1] not in pairs):
                        pairs.append(pr)
                    pair.clear()

            else:
                self.dragging = True
                if self.double_tapped:
                    self.dragging = False
                self.touch_offset = (self.pos[0] - touch.pos[0], self.pos[1] - touch.pos[1])
                if not self.initial_position:
                    self.initial_position = tuple(self.pos)

    # обработка перемещения
    def on_touch_move(self, touch):
        self.canvas.before.clear()
        cell_size = 50
        self.canvas.before.add(Color(0, 0, 0, 1))
        if self.dragging:
            self.pos = (touch.pos[0] + self.touch_offset[0], touch.pos[1] + self.touch_offset[1])
        for pr in pairs:
            el1 = pr[0]
            el2 = pr[1]
            x1, y1 = el1.pos
            x2, y2 = el2.pos
            y1 += 25
            y2 += 25
            try:
                result.clear()
                for el in el1.pins:
                    if el[1] is el2:
                        result.append(el[0])

                for el in el2.pins:
                    if el[1] is el1:
                        result.append(el[0])
            except:
                print("out of range")

            if el1.source == "images/voltmeter.png":
                el1.pos = [el2.pos[0], el2.pos[1] + cell_size]
                ln1 = Line(points=[x2 + cell_size, y2, x2 + cell_size, y2 + cell_size], width=5)
                ln2 = Line(points=[x2, y2, x2, y2 + cell_size], width=5)
                self.canvas.before.add(Color(0, 0, 0, 1))
                self.canvas.before.add(ln1)
                self.canvas.before.add(ln2)

            elif el2.source == "images/voltmeter.png":
                el2.pos = [el1.pos[0], el1.pos[1] + cell_size]
                ln1 = Line(points=[x1 + cell_size, y1, x1 + cell_size, y1 + cell_size], width=5)
                ln2 = Line(points=[x1, y1, x1, y1 + cell_size], width=5)
                self.canvas.before.add(Color(0, 0, 0, 1))
                self.canvas.before.add(ln1)
                self.canvas.before.add(ln2)
            else:
                try:
                    if result[0] == "left" and result[1] == "left":
                        if x2 > x1:
                            if y1 == y2:
                                ln1 = Line(points=[x1, y1, x1, y2 + cell_size], width=5)
                                ln2 = Line(points=[x1, y2 + cell_size, x2, y2 + cell_size], width=5)
                                ln3 = Line(points=[x2, y2 + cell_size, x2, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                                self.canvas.before.add(ln3)
                            else:
                                ln1 = Line(points=[x1, y1, x1, y2], width=5)
                                ln2 = Line(points=[x1, y2, x2, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                        elif x2 == x1:
                            ln1 = Line(points=[x1, y1, x1, y2], width=5)
                            self.canvas.before.add(Color(0, 0, 0, 1))
                            self.canvas.before.add(ln1)
                        else:
                            if y1 == y2:
                                ln1 = Line(points=[x1, y1, x1, y2 + cell_size], width=5)
                                ln2 = Line(points=[x1, y2 + cell_size, x2, y2 + cell_size], width=5)
                                ln3 = Line(points=[x2, y2 + cell_size, x2, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                                self.canvas.before.add(ln3)
                            else:
                                ln1 = Line(points=[x1, y1, x2, y1], width=5)
                                ln2 = Line(points=[x2, y1, x2, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)

                    elif result[0] == "left" and result[1] == "right":
                        if x2 < x1:
                            ln1 = Line(points=[x1, y1, x2 + cell_size, y1], width=5)
                            ln2 = Line(points=[x2 + cell_size, y1, x2 + cell_size, y2], width=5)
                            self.canvas.before.add(Color(0, 0, 0, 1))
                            self.canvas.before.add(ln1)
                            self.canvas.before.add(ln2)
                        else:
                            if y1 > y2:
                                ln1 = Line(points=[x1, y1, x1, y1 + cell_size], width=5)
                                ln2 = Line(points=[x1, y1 + cell_size, x2 + cell_size, y1 + cell_size], width=5)
                                ln3 = Line(points=[x2 + cell_size, y1 + cell_size, x2 + cell_size, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                                self.canvas.before.add(ln3)
                            else:
                                ln1 = Line(points=[x1, y1, x1, y1 - cell_size], width=5)
                                ln2 = Line(points=[x1, y1 - cell_size, x2 + cell_size, y1 - cell_size], width=5)
                                ln3 = Line(points=[x2 + cell_size, y1 - cell_size, x2 + cell_size, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                                self.canvas.before.add(ln3)

                    elif result[0] == "right" and result[1] == "left":
                        if x2 > x1:
                            ln1 = Line(points=[x1 + cell_size, y1, x2, y1], width=5)
                            ln2 = Line(points=[x2, y1, x2, y2], width=5)
                            self.canvas.before.add(Color(0, 0, 0, 1))
                            self.canvas.before.add(ln1)
                            self.canvas.before.add(ln2)
                        else:
                            if y1 > y2:
                                ln1 = Line(points=[x1 + cell_size, y1, x1 + cell_size, y1 + cell_size], width=5)
                                ln2 = Line(points=[x1 + cell_size, y1 + cell_size, x2, y1 + cell_size], width=5)
                                ln3 = Line(points=[x2, y1 + cell_size, x2, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                                self.canvas.before.add(ln3)
                            else:
                                ln1 = Line(points=[x1 + cell_size, y1, x1 + cell_size, y1 - cell_size], width=5)
                                ln2 = Line(points=[x1 + cell_size, y1 - cell_size, x2, y1 - cell_size], width=5)
                                ln3 = Line(points=[x2, y1 - cell_size, x2, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                                self.canvas.before.add(ln3)

                    elif result[0] == "right" and result[1] == "right":
                        if x2 > x1:
                            if y1 == y2:
                                ln1 = Line(points=[x1 + cell_size, y1, x1 + cell_size, y1 + cell_size], width=5)
                                ln2 = Line(points=[x1 + cell_size, y1 + cell_size, x2 + cell_size, y1 + cell_size],
                                           width=5)
                                ln3 = Line(points=[x2 + cell_size, y1 + cell_size, x2 + cell_size, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                                self.canvas.before.add(ln3)
                            else:
                                ln1 = Line(points=[x1 + cell_size, y1, x2 + cell_size, y1], width=5)
                                ln2 = Line(points=[x2 + cell_size, y1, x2 + cell_size, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                        elif x2 == x1:
                            ln1 = Line(points=[x1 + cell_size, y1, x1 + cell_size, y2], width=5)
                            self.canvas.before.add(Color(0, 0, 0, 1))
                            self.canvas.before.add(ln1)
                        else:
                            if y1 == y2:
                                ln1 = Line(points=[x1 + cell_size, y1, x1 + cell_size, y1 + cell_size], width=5)
                                ln2 = Line(points=[x1 + cell_size, y1 + cell_size, x2 + cell_size, y1 + cell_size],
                                           width=5)
                                ln3 = Line(points=[x2 + cell_size, y1 + cell_size, x2 + cell_size, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                                self.canvas.before.add(ln3)
                            else:
                                ln1 = Line(points=[x1 + cell_size, y1, x1 + cell_size, y2], width=5)
                                ln2 = Line(points=[x1 + cell_size, y2, x2 + cell_size, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                except:
                    print("out of range")

    # обработка отпускания
    def on_touch_up(self, touch):
        global result
        global backs
        global x, y
        cell_size = 50
        self.dragging = False
        if self.collide_point(*touch.pos):
            self.dragged_elements.append(self)
            # округление координат к ближайшим точкам сетки
            if self.pos[0] % cell_size >= cell_size / 2:
                new_x = (int(self.pos[0] / cell_size) + 1) * cell_size
            else:
                new_x = int(self.pos[0] / cell_size) * cell_size
            if self.pos[1] % cell_size >= cell_size / 2:
                new_y = (int(self.pos[1] / cell_size) + 1) * cell_size
            else:
                new_y = int(self.pos[1] / cell_size) * cell_size
            self.pos = (new_x, new_y)  # перемещение элемента в ближайшую точку сетки

        if self.double_tapped:
            if touch.pos[0] < (self.pos[0] + cell_size // 2):
                if "left" not in self.pins:
                    self.pins.append(["left"])
                else:
                    self.pins.append(["right"])
            else:
                if "right" not in self.pins:
                    self.pins.append(["right"])
                else:
                    self.pins.append(["left"])

        self.canvas.before.clear()
        lines.clear()

        count = 0
        for pr in pairs:
            count += 1
            el1 = pr[0]
            el2 = pr[1]
            if self.double_tapped and len(backs) % 2 == 0:
                flag1 = False
                flag2 = False
                for i in range(len(el1.pins)):
                    if len(el1.pins[i]) == 1:
                        x = el1.pins[i]
                        flag1 = True
                        break

                for j in range(len(el2.pins)):
                    if len(el2.pins[j]) == 1:
                        y = el2.pins[j]
                        flag2 = True
                        break

                if flag1 and flag2:
                    x.append(el2)
                    y.append(el1)
            try:
                result.clear()
                for el in el1.pins:
                    if el[1] is el2:
                        result.append(el[0])

                for el in el2.pins:
                    if el[1] is el1:
                        result.append(el[0])
            except:
                print("out of range")

            x1, y1 = el1.pos
            x2, y2 = el2.pos

            if x1 % cell_size >= cell_size / 2:
                new_x1 = (int(x1 / cell_size) + 1) * cell_size
            else:
                new_x1 = int(x1 / cell_size) * cell_size
            if y1 % cell_size >= cell_size / 2:
                new_y1 = (int(y1 / cell_size) + 1) * cell_size
            else:
                new_y1 = int(y1 / cell_size) * cell_size

            x1, y1 = (new_x1, new_y1 + 25)

            if x2 % cell_size >= cell_size / 2:
                new_x2 = (int(x2 / cell_size) + 1) * cell_size
            else:
                new_x2 = int(x2 / cell_size) * cell_size
            if y2 % cell_size >= cell_size / 2:
                new_y2 = (int(y2 / cell_size) + 1) * cell_size
            else:
                new_y2 = int(y2 / cell_size) * cell_size

            x2, y2 = (new_x2, new_y2 + 25)

            if el1.source == "images/voltmeter.png":
                el1.pos = [el2.pos[0], el2.pos[1] + cell_size]
                ln1 = Line(points=[x2 + cell_size, y2, x2 + cell_size, y2 + cell_size], width=5)
                ln2 = Line(points=[x2, y2, x2, y2 + cell_size], width=5)
                self.canvas.before.add(Color(0, 0, 0, 1))
                self.canvas.before.add(ln1)
                self.canvas.before.add(ln2)

            elif el2.source == "images/voltmeter.png":
                el2.pos = [el1.pos[0], el1.pos[1] + cell_size]
                ln1 = Line(points=[x1 + cell_size, y1, x1 + cell_size, y1 + cell_size], width=5)
                ln2 = Line(points=[x1, y1, x1, y1 + cell_size], width=5)
                self.canvas.before.add(Color(0, 0, 0, 1))
                self.canvas.before.add(ln1)
                self.canvas.before.add(ln2)

            else:
                try:
                    if result[0] == "left" and result[1] == "left":
                        if x2 > x1:
                            if y1 == y2:
                                ln1 = Line(points=[x1, y1, x1, y2 + cell_size], width=5)
                                ln2 = Line(points=[x1, y2 + cell_size, x2, y2 + cell_size], width=5)
                                ln3 = Line(points=[x2, y2 + cell_size, x2, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                                self.canvas.before.add(ln3)
                            else:
                                ln1 = Line(points=[x1, y1, x1, y2], width=5)
                                ln2 = Line(points=[x1, y2, x2, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)

                        elif x2 == x1:
                            ln1 = Line(points=[x1, y1, x1, y2], width=5)
                            self.canvas.before.add(Color(0, 0, 0, 1))
                            self.canvas.before.add(ln1)

                        else:
                            if y1 == y2:
                                ln1 = Line(points=[x1, y1, x1, y2 + cell_size], width=5)
                                ln2 = Line(points=[x1, y2 + cell_size, x2, y2 + cell_size], width=5)
                                ln3 = Line(points=[x2, y2 + cell_size, x2, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                                self.canvas.before.add(ln3)
                            else:
                                ln1 = Line(points=[x1, y1, x2, y1], width=5)
                                ln2 = Line(points=[x2, y1, x2, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)

                    elif result[0] == "left" and result[1] == "right":
                        if x2 < x1:
                            ln1 = Line(points=[x1, y1, x2 + cell_size, y1], width=5)
                            ln2 = Line(points=[x2 + cell_size, y1, x2 + cell_size, y2], width=5)
                            self.canvas.before.add(Color(0, 0, 0, 1))
                            self.canvas.before.add(ln1)
                            self.canvas.before.add(ln2)
                        else:
                            if y1 > y2:
                                ln1 = Line(points=[x1, y1, x1, y1 + cell_size], width=5)
                                ln2 = Line(points=[x1, y1 + cell_size, x2 + cell_size, y1 + cell_size], width=5)
                                ln3 = Line(points=[x2 + cell_size, y1 + cell_size, x2 + cell_size, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                                self.canvas.before.add(ln3)
                            else:
                                ln1 = Line(points=[x1, y1, x1, y1 - cell_size], width=5)
                                ln2 = Line(points=[x1, y1 - cell_size, x2 + cell_size, y1 - cell_size], width=5)
                                ln3 = Line(points=[x2 + cell_size, y1 - cell_size, x2 + cell_size, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                                self.canvas.before.add(ln3)

                    elif result[0] == "right" and result[1] == "left":
                        if x2 > x1:
                            ln1 = Line(points=[x1 + cell_size, y1, x2, y1], width=5)
                            ln2 = Line(points=[x2, y1, x2, y2], width=5)
                            self.canvas.before.add(Color(0, 0, 0, 1))
                            self.canvas.before.add(ln1)
                            self.canvas.before.add(ln2)
                        else:
                            if y1 > y2:
                                ln1 = Line(points=[x1 + cell_size, y1, x1 + cell_size, y1 + cell_size], width=5)
                                ln2 = Line(points=[x1 + cell_size, y1 + cell_size, x2, y1 + cell_size], width=5)
                                ln3 = Line(points=[x2, y1 + cell_size, x2, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                                self.canvas.before.add(ln3)
                            else:
                                ln1 = Line(points=[x1 + cell_size, y1, x1 + cell_size, y1 - cell_size], width=5)
                                ln2 = Line(points=[x1 + cell_size, y1 - cell_size, x2, y1 - cell_size], width=5)
                                ln3 = Line(points=[x2, y1 - cell_size, x2, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                                self.canvas.before.add(ln3)

                    elif result[0] == "right" and result[1] == "right":
                        if x2 > x1:
                            if y1 == y2:
                                ln1 = Line(points=[x1 + cell_size, y1, x1 + cell_size, y1 + cell_size], width=5)
                                ln2 = Line(points=[x1 + cell_size, y1 + cell_size, x2 + cell_size, y1 + cell_size],
                                           width=5)
                                ln3 = Line(points=[x2 + cell_size, y1 + cell_size, x2 + cell_size, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                                self.canvas.before.add(ln3)
                            else:
                                ln1 = Line(points=[x1 + cell_size, y1, x2 + cell_size, y1], width=5)
                                ln2 = Line(points=[x2 + cell_size, y1, x2 + cell_size, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                        elif x2 == x1:
                            ln1 = Line(points=[x1 + cell_size, y1, x1 + cell_size, y2], width=5)
                            self.canvas.before.add(Color(0, 0, 0, 1))
                            self.canvas.before.add(ln1)
                        else:
                            if y1 == y2:
                                ln1 = Line(points=[x1 + cell_size, y1, x1 + cell_size, y1 + cell_size], width=5)
                                ln2 = Line(points=[x1 + cell_size, y1 + cell_size, x2 + cell_size, y1 + cell_size],
                                           width=5)
                                ln3 = Line(points=[x2 + cell_size, y1 + cell_size, x2 + cell_size, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                                self.canvas.before.add(ln3)
                            else:
                                ln1 = Line(points=[x1 + cell_size, y1, x1 + cell_size, y2], width=5)
                                ln2 = Line(points=[x1 + cell_size, y2, x2 + cell_size, y2], width=5)
                                self.canvas.before.add(Color(0, 0, 0, 1))
                                self.canvas.before.add(ln1)
                                self.canvas.before.add(ln2)
                except:
                    print("out of range")

        self.double_tapped = False


class MechanicsFrictionForceScreen(Screen):
    def __init__(self, **kwargs):
        global variant
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.ids.top_bar.title = "Механика, комплект " + str(variant)
        self.center_x = Window.size[0] / 2
        self.center_y = Window.size[1] / 2
        self.object_placed = False
        self.forces_shown = False
        self.dynamometer_placed = False
        self.ground_reaction_mark = None
        self.gravity_mark = None
        self.friction_mark = None
        self.traction_mark = None
        self.friction_force = 0
        self.distance = 0
        self.traction_force = 0
        self.weight = 0
        self.canvas.before.add(Color(0, 0, 0, 1))
        self.canvas.before.add(Line(points=[self.center_x - 900, self.center_y - 300, self.center_x + 900,
                                            self.center_y - 300], width=5))

    def draw_object(self):
        self.object_placed = True
        self.canvas.before.add(Color(0.65, 0.89, 0.62, 1))
        self.canvas.before.add(Rectangle(pos=(self.center_x - 550, self.center_y - 295), size=(300, 200)))

    def show_forces(self):
        if self.object_placed:
            self.forces_shown = True
            self.canvas.before.add(Color(0, 0, 0, 1))

            self.canvas.before.add(Line(points=[self.center_x - 800, self.center_y - 195, self.center_x,
                                                self.center_y - 195], width=5))
            self.canvas.before.add(Line(points=[self.center_x - 800, self.center_y - 195, self.center_x - 790,
                                                self.center_y - 185], width=5))
            self.canvas.before.add(Line(points=[self.center_x - 800, self.center_y - 195, self.center_x - 790,
                                                self.center_y - 205], width=5))
            self.canvas.before.add(Line(points=[self.center_x, self.center_y - 195, self.center_x - 10,
                                                self.center_y - 185], width=5))
            self.canvas.before.add(Line(points=[self.center_x, self.center_y - 195, self.center_x - 10,
                                                self.center_y - 205], width=5))

            self.canvas.before.add(Line(points=[self.center_x - 400, self.center_y - 395, self.center_x - 400,
                                                self.center_y + 5], width=5))
            self.canvas.before.add(Line(points=[self.center_x - 400, self.center_y - 395, self.center_x - 410,
                                                self.center_y - 385], width=5))
            self.canvas.before.add(Line(points=[self.center_x - 400, self.center_y - 395, self.center_x - 390,
                                                self.center_y - 385], width=5))
            self.canvas.before.add(Line(points=[self.center_x - 400, self.center_y + 5, self.center_x - 410,
                                                self.center_y - 5], width=5))
            self.canvas.before.add(Line(points=[self.center_x - 400, self.center_y + 5, self.center_x - 390,
                                                self.center_y - 5], width=5))

            self.ground_reaction_mark = Label()
            self.gravity_mark = Label()
            self.friction_mark = Label()
            self.traction_mark = Label()

            self.ground_reaction_mark.text = "N"
            self.ground_reaction_mark.font_size = 40
            self.ground_reaction_mark.color = [0, 0, 0, 1]
            self.ground_reaction_mark.pos = [self.pos[0] - 400, self.pos[1] + 50]
            self.add_widget(self.ground_reaction_mark)

            self.gravity_mark.text = "mg"
            self.gravity_mark.font_size = 40
            self.gravity_mark.color = [0, 0, 0, 1]
            self.gravity_mark.pos = [self.pos[0] - 400, self.pos[1] - 420]
            self.add_widget(self.gravity_mark)

            self.friction_mark.text = "Fтр"
            self.friction_mark.font_size = 40
            self.friction_mark.color = [0, 0, 0, 1]
            self.friction_mark.pos = [self.pos[0] - 850, self.pos[1] - 190]
            self.add_widget(self.friction_mark)

            self.traction_mark.text = "Fтяги"
            self.traction_mark.font_size = 40
            self.traction_mark.color = [0, 0, 0, 1]
            self.traction_mark.pos = [self.pos[0] + 40, self.pos[1] - 160]
            self.add_widget(self.traction_mark)
        else:
            popup = Popup(title='Ошибка', title_size='20sp', content=Label(text='Сначала установите тело',
                          font_size='17sp'), size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def update(self):
        global variant
        self.ids.top_bar.title = "Механика, комплект " + str(variant)

    def draw_dynamometer(self):
        if self.object_placed and self.forces_shown:
            self.dynamometer_placed = True
            self.canvas.before.add(Line(points=[self.center_x - 400, self.center_y - 195, self.center_x + 170,
                                                self.center_y - 195], width=5))
            with self.canvas:
                Rectangle(source="mechanics_images/dynamometer.png", pos=(self.center_x + 170, self.center_y - 300),
                          size=(200, 200))
        else:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Сначала установите тело и отобразите силы', font_size='17sp'),
                          size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()
    def get_friction_force(self):
        if self.object_placed and self.forces_shown and self.dynamometer_placed:
            if self.ids.friction_force.text == "":
                self.friction_force = 1
            else:
                try:
                    self.friction_force = float(self.ids.friction_force.text)
                except:
                    self.friction_force = -10

            if self.friction_force <= 0:
                popup = Popup(title='Ошибка', title_size='20sp',
                              content=Label(text='Сила трения не может быть меньше 0!', font_size='17sp'),
                              size_hint=(0.3, 0.16))
                popup.overlay_color = Color(1, 1, 1, 0).rgba
                popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
                popup.open()
        else:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Сначала установите тело, динамометр и отобразите силы', font_size='17sp'),
                          size_hint=(0.35, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def get_distance(self):
        if self.object_placed and self.forces_shown:
            if self.ids.distance.text == "":
                self.distance = 1
            else:
                try:
                    self.distance = float(self.ids.distance.text)
                except:
                    self.distance = -10

            if self.distance <= 0:
                popup = Popup(title='Ошибка', title_size='20sp',
                              content=Label(text='Расстояние не может быть меньше 0!', font_size='17sp'),
                              size_hint=(0.3, 0.16))
                popup.overlay_color = Color(1, 1, 1, 0).rgba
                popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
                popup.open()
        else:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Сначала установите тело и отобразите силы', font_size='17sp'),
                          size_hint=(0.35, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def get_traction_force(self):
        if self.object_placed and self.forces_shown:
            if self.ids.traction_force.text == "":
                self.traction_force = 1
            else:
                try:
                    self.traction_force = float(self.ids.traction_force.text)
                except:
                    self.traction_force = -10

            if self.traction_force <= 0:
                popup = Popup(title='Ошибка', title_size='20sp',
                              content=Label(text='Сила тяги не может быть меньше 0!', font_size='17sp'),
                              size_hint=(0.3, 0.16))
                popup.overlay_color = Color(1, 1, 1, 0).rgba
                popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
                popup.open()
        else:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Сначала установите тело и отобразите силы', font_size='17sp'),
                          size_hint=(0.35, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def get_weight(self):
        if self.object_placed and self.forces_shown:
            if self.ids.weight.text == "":
                self.weight = 1
            else:
                try:
                    self.weight = float(self.ids.weight.text)
                except:
                    self.weight = -10

            if self.weight <= 0:
                popup = Popup(title='Ошибка', title_size='20sp',
                              content=Label(text='Масса не может быть меньше 0!', font_size='17sp'),
                              size_hint=(0.3, 0.16))
                popup.overlay_color = Color(1, 1, 1, 0).rgba
                popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
                popup.open()
        else:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Сначала установите тело и отобразите силы', font_size='17sp'),
                          size_hint=(0.35, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def count_friction_force_work(self):
        friction_force_work = self.friction_force * (self.distance / 100)
        popup = Popup(title='Результат', title_size='20sp',
                      content=Label(text=f'Работа силы трения = {friction_force_work} [Дж]', font_size='17sp'),
                      size_hint=(0.3, 0.16))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def count_friction_coefficient(self):
        try:
            friction_coefficient = self.traction_force / (self.weight / 100)
        except:
            friction_coefficient = 0
        popup = Popup(title='Результат', title_size='20sp',
                      content=Label(text=f'Коэффициент трения = {friction_coefficient:.3f}', font_size='17sp'),
                      size_hint=(0.3, 0.16))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def friction_force_explanation(self):
        popup = Popup(title='Пояснение', title_size='20sp',
                      content=Label(text=f'Задача 1:\nA = Fтрения * S [Дж]\nFтрения = Fтяги\nFтяги = m * g\nA - работа силы трения[Дж]\nS - пройденное расстояние[м]\nm - масса тела с грузиками[кг]\ng - ускорение свободного падения = 10[Н/кг]\n----------------------\nЗадача 2:\nFтрения = M*m*g*cosα[Н], cosα = 1\nFтрения = Fтяги\nM = Fтяги/mg (коэффициент силы трения)', font_size='17sp'), size_hint=(0.3, 0.45))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def friction_force_task1(self):
        popup = Popup(title='Задача 1', title_size='20sp',
                      content=Label(text='Используя каретку (брусок) с крючком, динамометр, два груза, направляющую рейку, соберите экспериментальную установку для измерения работы силы трения скольжения\nпри движении каретки с грузами по поверхности рейки на расстояние в 40 см. Абсолютную погрешность измерения силы с помощью динамометра принять равной ± 0,1Н.', font_size='17sp'), size_hint=(0.95, 0.16))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def friction_force_task2(self):
        popup = Popup(title='Задача 2', title_size='20sp',
                      content=Label(text='Используя брусок с крючком, динамометр, груз, направляющую рейку, соберите экспериментальную установку для измерения коэффициента трения\nскольжения между бруском с грузом и поверхностью рейки. Используйте поверхность рейки. Абсолютная погрешность измерения силы при помощи динамометра\nравна ± 0,02 Н, а при помощи динамометра равна ± 0,1 Н.', font_size='17sp'), size_hint=(0.9, 0.2))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def go_back(self):
        app = MDApp.get_running_app()
        app.root.transition.direction = "right"
        app.root.current = "set_selection_mechanics"

    def open_account(self):
        global previous
        previous = "mechanics_frictionforce"
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "account_screen"


class MechanicsFluctuationsScreen(Screen):
    def __init__(self, **kwargs):
        global variant
        super().__init__(**kwargs)
        self.items = []
        self.orientation = "vertical"
        self.ids.top_bar.title = "Механика, комплект " + str(variant)
        self.center_x = Window.size[0] / 2
        self.center_y = Window.size[1] / 2
        self.fluctuations_time = 1
        self.fluctuations_number = 1
        self.oscillation_period = 0
        self.rope_length = 200
        self.rope_angle = 0
        self.rope_speed = 5
        self.canvas.before.add(Color(0, 0, 0, 1))
        self.canvas.before.add(Line(points=[self.center_x - 400, self.center_y + 300, self.center_x + 400,
                                            self.center_y + 300], width=5))
        self.rope = Line(points=[self.center_x, self.center_y + 300, self.center_x, self.center_y - 100], width=5)
        self.ball = Ellipse(pos=(self.center_x - 50, self.center_y - 150), size=(100, 100))
        self.canvas.before.add(self.ball)
        self.canvas.before.add(self.rope)
        self.start_oscillation()

    def update(self):
        global variant
        self.ids.top_bar.title = "Механика, комплект " + str(variant)

    def start_oscillation(self):
        self.oscillation_time = 0
        self.oscillation_period = self.fluctuations_time / self.fluctuations_number
        Clock.schedule_interval(self.update_oscillation, 1.0 / 60.0)

    def update_oscillation(self, dt):
        self.oscillation_time += dt
        try:
            self.oscillation_period = self.fluctuations_time / self.fluctuations_number
            self.oscillation_time %= self.oscillation_period
        except:
            self.oscillation_period = 1
        half_period = self.oscillation_period / 2
        if self.oscillation_time <= half_period:
            angle = self.oscillation_time / half_period * math.pi
            x = self.center_x - 300 * math.cos(angle)
        else:
            angle = (self.oscillation_time - half_period) / half_period * math.pi
            x = self.center_x + 300 * math.cos(angle)
        y = self.center_y + 50 - 150 * math.sin(angle)
        self.ball.pos = (x - 50, y - 50)
        self.rope.points = [self.center_x, self.center_y + 300, x, y]

    def get_fluctuations_number(self):
        if self.ids.fluctuations_number.text == "":
            self.fluctuations_number = 1
        else:
            try:
                self.fluctuations_number = int(self.ids.fluctuations_number.text)
            except:
                self.fluctuations_number = -10

        if self.fluctuations_number <= 0:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Количество колебаний не может быть меньше 0!', font_size='17sp'),
                          size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def get_fluctuations_time(self):
        if self.ids.fluctuations_time.text == "":
            self.fluctuations_time = 1
        else:
            try:
                self.fluctuations_time = int(self.ids.fluctuations_time.text)
            except:
                self.fluctuations_time = -10

        if self.fluctuations_time <= 0:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Время колебаний не может быть меньше 0!', font_size='17sp'),
                          size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def count_frequency(self):
        try:
            frequency = self.fluctuations_number / self.fluctuations_time
        except:
            frequency = 0
        popup = Popup(title='Результат', title_size='20sp',
                      content=Label(text=f'Частота колебания = {frequency:.3f} [Гц]', font_size='17sp'),
                      size_hint=(0.3, 0.16))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def count_period(self):
        try:
            period = self.fluctuations_time / self.fluctuations_number
        except:
            period = 0
        popup = Popup(title='Результат', title_size='20sp',
                      content=Label(text=f'Период колебания = {period:.3f} [с]', font_size='17sp'),
                      size_hint=(0.3, 0.16))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()
        return period

    def fluctuations_explanation(self):
        popup = Popup(title='Пояснение', title_size='20sp',
                      content=Label(text=f'Задача 1:\nv = n/t [Гц]\nv - частота колебаний[Гц]\nn - количество колебаний за время t\nt - время колебаний[с]\n----------------------\nЗадача 2:\nT = t/n [с]\nT - период колебаний[с]', font_size='17sp'), size_hint=(0.22, 0.34))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def fluctuations_task1(self):
        popup = Popup(title='Задача 1', title_size='20sp',
                      content=Label(text='Используя штатив с муфтой и лапкой, груз с прикреплённой к нему нитью, метровую линейку и секундомер,\nсоберите экспериментальную установку для исследования свободных колебаний нитяного маятника. Определите время для 30 полных колебаний и посчитайте частоту\nколебаний для случая когда длина нити равна 50 см. Абсолютную погрешность измерения времени принять равной ± 5с.', font_size='17sp'), size_hint=(0.92, 0.16))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def fluctuations_task2(self):
        popup = Popup(title='Задача 2', title_size='20sp',
                      content=Label(text='Используя штатив с муфтой и лапкой, груз с прикреплённой к нему нитью, метровую линейку и секундомер,\nсоберите экспериментальную установку для исследования свободных колебаний нитяного маятника. Определите время 30 полных колебаний и вычислите период колебаний\nдля случая, когда длина маятника равна 1 м. Абсолютную погрешность измерения интервала времени принять равной ± 5с.', font_size='17sp'), size_hint=(0.92, 0.16))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def go_back(self):
        app = MDApp.get_running_app()
        app.root.transition.direction = "right"
        app.root.current = "set_selection_mechanics"

    def open_account(self):
        global previous
        previous = "mechanics_fluctuations"
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "account_screen"


class MechanicsBlocksScreen(Screen):
    def __init__(self, **kwargs):
        global variant
        super().__init__(**kwargs)
        self.items = []
        self.orientation = "vertical"
        self.ids.top_bar.title = "Механика, комплект " + str(variant)
        self.center_x = Window.size[0] / 2
        self.center_y = Window.size[1] / 2
        self.reach_height = 0
        self.cargo_number = 0
        self.cargo_weight = 0
        self.elastic_force = 0
        self.elastic_force_mark = None
        self.force_shown = False
        self.dynamometer_placed = False
        self.blocks_placed = False
        self.canvas.before.add(Color(0, 0, 0, 1))
        self.canvas.before.add(Line(points=[self.center_x - 400, self.center_y + 300, self.center_x + 400,
                                            self.center_y + 300], width=5))
        self.canvas.before.add(Line(points=[self.center_x, self.center_y + 300, self.center_x, self.center_y + 50],
                                    width=5))
        self.canvas.before.add(Ellipse(pos=(self.center_x - 75, self.center_y), size=(150, 150)))
        self.canvas.before.add(Line(points=[self.center_x - 70, self.center_y + 75, self.center_x - 70,
                                            self.center_y - 100], width=5))
        self.canvas.before.add(Line(points=[self.center_x + 70, self.center_y + 75, self.center_x + 70,
                                            self.center_y - 100], width=5))

    def update(self):
        global variant
        self.ids.top_bar.title = "Механика, комплект " + str(variant)

    def show_force(self):
        self.force_shown = True
        self.canvas.before.add(Color(0, 0, 0, 1))
        self.canvas.before.add(Line(points=[self.center_x - 70, self.center_y - 100, self.center_x - 80,
                                            self.center_y - 90], width=5))
        self.canvas.before.add(Line(points=[self.center_x - 70, self.center_y - 100, self.center_x - 60,
                                            self.center_y - 90], width=5))
        self.elastic_force_mark = Label()
        self.elastic_force_mark.text = "Fупр"
        self.elastic_force_mark.font_size = 40
        self.elastic_force_mark.color = [0, 0, 0, 1]
        self.elastic_force_mark.pos = [self.pos[0] - 130, self.pos[1] - 110]
        self.add_widget(self.elastic_force_mark)

    def draw_dynamometer(self):
        if self.force_shown:
            self.dynamometer_placed = True
            self.canvas.before.add(Line(points=[self.center_x - 70, self.center_y - 100, self.center_x - 70,
                                                self.center_y - 140], width=5))
            with self.canvas:
                Rectangle(source="mechanics_images/dynamometer2.png", pos=(self.center_x - 136, self.center_y - 280),
                          size=(135, 135))
        else:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Сначала отобразите силы', font_size='17sp'), size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def draw_cargo(self):
        if self.force_shown and self.dynamometer_placed:
            self.blocks_placed = True

            for item in self.items:
                self.canvas.before.remove(item)
            self.items.clear()

            self.canvas.before.add(Color(0, 0, 0, 1))
            if self.cargo_number == 1:
                rec1 = Rectangle(pos=(self.center_x + 45, self.center_y - 150), size=(50, 50))
                self.items.append(rec1)
                self.canvas.before.add(rec1)

            if self.cargo_number == 2:
                rec1 = Rectangle(pos=(self.center_x + 45, self.center_y - 150), size=(50, 50))
                self.items.append(rec1)
                self.canvas.before.add(rec1)

                ln1 = Line(points=[self.center_x + 70, self.center_y + 45, self.center_x + 70, self.center_y - 180],
                           width=5)
                self.items.append(ln1)
                self.canvas.before.add(ln1)

                rec2 = Rectangle(pos=(self.center_x + 45, self.center_y - 230), size=(50, 50))
                self.items.append(rec2)
                self.canvas.before.add(rec2)

            if self.cargo_number == 3:
                rec1 = Rectangle(pos=(self.center_x + 45, self.center_y - 150), size=(50, 50))
                self.items.append(rec1)
                self.canvas.before.add(rec1)

                ln1 = Line(points=[self.center_x + 70, self.center_y + 45, self.center_x + 70, self.center_y - 180],
                           width=5)
                self.items.append(ln1)
                self.canvas.before.add(ln1)

                rec2 = Rectangle(pos=(self.center_x + 45, self.center_y - 230), size=(50, 50))
                self.items.append(rec2)
                self.canvas.before.add(rec2)

                ln2 = Line(points=[self.center_x + 70, self.center_y + 45, self.center_x + 70, self.center_y - 260],
                           width=5)
                self.items.append(ln2)
                self.canvas.before.add(ln2)

                rec3 = Rectangle(pos=(self.center_x + 45, self.center_y - 310), size=(50, 50))
                self.items.append(rec3)
                self.canvas.before.add(rec3)
        else:
            popup = Popup(title='Ошибка', title_size='20sp', content=Label(text='Сначала отобразите силы и динамометр',
                          font_size='17sp'), size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def get_cargo_number(self):
        if self.ids.cargo_number.text == "":
            self.cargo_number = 1
        else:
            try:
                self.cargo_number = int(self.ids.cargo_number.text)
            except:
                self.cargo_number = 0

        if self.cargo_number <= 0:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Количество грузов не может быть меньше 0!', font_size='17sp'),
                          size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()
        elif self.cargo_number > 3:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Количество грузов не может быть больше 3!', font_size='17sp'),
                          size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def get_cargo_weight(self):
        if self.force_shown and self.dynamometer_placed and self.blocks_placed:
            if self.ids.cargo_weight.text == "":
                self.cargo_weight = 1
            else:
                try:
                    self.cargo_weight = float(self.ids.cargo_weight.text)
                except:
                    self.cargo_weight = 0

            if self.cargo_weight <= 0:
                popup = Popup(title='Ошибка', title_size='20sp',
                              content=Label(text='Масса груза не может быть меньше 0!', font_size='17sp'),
                              size_hint=(0.3, 0.16))
                popup.overlay_color = Color(1, 1, 1, 0).rgba
                popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
                popup.open()
        else:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Сначала отобразите силы, динамометр и грузы', font_size='17sp'),
                          size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def get_reach_height(self):
        if self.force_shown and self.dynamometer_placed and self.blocks_placed:
            if self.ids.reach_height.text == "":
                self.reach_height = 1
            else:
                try:
                    self.reach_height = float(self.ids.reach_height.text)
                except:
                    self.reach_height = 0

            if self.reach_height <= 0:
                popup = Popup(title='Ошибка', title_size='20sp', content=Label(text='Высота не может быть меньше 0!',
                              font_size='17sp'), size_hint=(0.3, 0.16))
                popup.overlay_color = Color(1, 1, 1, 0).rgba
                popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
                popup.open()
        else:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Сначала отобразите силы, динамометр и грузы', font_size='17sp'),
                          size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def count_elastic_force_work(self):
        elastic_force_work = self.cargo_number * (self.cargo_weight / 1000) * (self.reach_height / 100)
        popup = Popup(title='Результат', title_size='20sp',
                      content=Label(text=f'Работа силы упругости = {elastic_force_work:.3f} [Дж]', font_size='17sp'),
                      size_hint=(0.3, 0.16))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def blocks_explanation(self):
        popup = Popup(title='Пояснение', title_size='20sp',
                      content=Label(text=f'A = Fупр * S [Дж]\nA - работа силы трения[Дж]\nFупр - сила упругости[Н]\nS - высота подъема[м]\ng = 10[Н/кг]', font_size='17sp'), size_hint=(0.2, 0.29))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def blocks_task(self):
        popup = Popup(title='Задача', title_size='20sp',
                      content=Label(text='Используя штатив с муфтой, неподвижный блок, нить, два груза и динамометр, соберите экспериментальную установку для измерения работы силы упругости\nпри равномерном подъёме грузов с использованием неподвижного блока. Определите работу, совершаемую силой упругости при подъёме\nдвух соединённых вместе грузов на высоту 10 см. Абсолютную погрешность измерения силы с помощью динамометра принять равной ± 0,1 H', font_size='17sp'), size_hint=(0.86, 0.21))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def go_back(self):
        app = MDApp.get_running_app()
        app.root.transition.direction = "right"
        app.root.current = "set_selection_mechanics"

    def open_account(self):
        global previous
        previous = "mechanics_blocks"
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "account_screen"


class MechanicsArchimedesForceScreen(Screen):
    def __init__(self, **kwargs):
        global variant
        super().__init__(**kwargs)
        self.items1 = []
        self.items2 = []
        self.orientation = "vertical"
        self.ids.top_bar.title = "Механика, комплект " + str(variant)
        self.center_x = Window.size[0] / 2
        self.center_y = Window.size[1] / 2
        self.volume_before = 0
        self.volume_after = 0
        self.weight = 0
        self.before = Label()
        self.after = Label()
        self.before.text = "БЫЛО"
        self.after.text = "СТАЛО"
        self.before.pos = [self.pos[0] - 1.33 * self.center_x, self.pos[1] - 1.6 * self.center_y]
        self.after.pos = [self.pos[0] - 0.57 * self.center_x, self.pos[1] - 1.6 * self.center_y]
        self.before.font_size = 40
        self.before.color = [0, 0, 0, 1]
        self.after.font_size = 40
        self.after.color = [0, 0, 0, 1]
        self.canvas.before.add(Color(0, 0, 0, 1))
        self.canvas.before.add(Line(points=[self.center_x - self.center_x / 1.5, self.center_y - 300,
                                            self.center_x - 100, self.center_y - 300], width=5))
        self.canvas.before.add(Line(points=[self.center_x - self.center_x / 1.5, self.center_y + 300,
                                            self.center_x - self.center_x / 1.5, self.center_y - 300], width=5))
        self.canvas.before.add(Line(points=[self.center_x - 100, self.center_y + 300, self.center_x - 100,
                                            self.center_y - 300], width=5))
        self.add_widget(self.before)
        self.canvas.before.add(Line(points=[self.center_x + self.center_x / 1.5, self.center_y - 300,
                                            self.center_x + 100, self.center_y - 300], width=5))
        self.canvas.before.add(Line(points=[self.center_x + self.center_x / 1.5, self.center_y + 300,
                                            self.center_x + self.center_x / 1.5, self.center_y - 300], width=5))
        self.canvas.before.add(Line(points=[self.center_x + 100, self.center_y + 300, self.center_x + 100,
                                            self.center_y - 300], width=5))
        self.add_widget(self.after)
        self.canvas.before.add(Line(points=[self.center_x - 50, self.center_y - 60, self.center_x + 50,
                                            self.center_y - 60], width = 5))
        self.canvas.before.add(Line(points=[self.center_x + 35, self.center_y - 40, self.center_x + 50,
                                            self.center_y - 60], width=5))
        self.canvas.before.add(Line(points=[self.center_x + 35, self.center_y - 80, self.center_x + 50,
                                            self.center_y - 60], width=5))

    def show_water_level_before(self):
        for item in self.items1:
            try:
                self.canvas.before.remove(item)
            except:
                self.remove_widget(item)
        self.items1.clear()

        self.canvas.before.add(Color(0, 0, 0, 1))
        self.volume_before_mark = Label()
        self.volume_before_mark.text = "V1"
        self.volume_before_mark.font_size = 40
        self.volume_before_mark.color = [0, 0, 0, 1]
        self.volume_before_mark.pos = [self.pos[0] - 150, -280 + self.volume_before * 10]
        self.add_widget(self.volume_before_mark)
        self.items1.append(self.volume_before_mark)

        self.canvas.before.add(Color(0, 0, 0, 1))
        level1 = Line(points=[self.center_x - 120, self.center_y - 300 + self.volume_before * 10,
                              self.center_x - 80, self.center_y - 300 + self.volume_before * 10], width=5)
        self.canvas.before.add(level1)
        self.items1.append(level1)

        self.canvas.before.add(Color(0, 1, 1, 1))
        rec1 = Rectangle(pos=(self.center_x - 635, self.center_y - 295), size=(530, self.volume_before * 10 - 10))
        self.canvas.before.add(rec1)
        self.items1.append(rec1)

    def show_water_level_after(self):
        for item in self.items2:
            try:
                self.canvas.before.remove(item)
            except:
                self.remove_widget(item)
        self.items2.clear()

        self.canvas.before.add(Color(0, 0, 0, 1))
        self.volume_after_mark = Label()
        self.volume_after_mark.text = "V2"
        self.volume_after_mark.font_size = 40
        self.volume_after_mark.color = [0, 0, 0, 1]
        self.volume_after_mark.pos = [self.pos[0] + 150, -280 + self.volume_after * 10]
        self.add_widget(self.volume_after_mark)
        self.items2.append(self.volume_after_mark)

        self.canvas.before.add(Color(0, 0, 0, 1))
        level2 = Line(points=[self.center_x + 120, self.center_y - 300 + self.volume_after * 10, self.center_x + 80,
                              self.center_y - 300 + self.volume_after * 10], width=5)  # +665, +615
        self.canvas.before.add(level2)
        self.items2.append(level2)

        self.canvas.before.add(Color(0, 1, 1, 1))
        rec2 = Rectangle(pos=(self.center_x + 105, self.center_y - 295), size=(530, self.volume_after * 10 - 10))
        self.canvas.before.add(rec2)
        self.items2.append(rec2)

    def update(self):
        global variant
        self.ids.top_bar.title = "Механика, комплект " + str(variant)

    def get_volume_before(self):
        if self.ids.volume_before.text == "":
            self.volume_before = 1
        else:
            try:
                self.volume_before = float(self.ids.volume_before.text)
            except:
                self.volume_before = -10

        if self.volume_before <= 0 or self.volume_before > 60:
            self.volume_before = 60
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Объем не может быть меньше 0 или больше 60 мл!', font_size='17sp'),
                          size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def get_volume_after(self):
        if self.ids.volume_after.text == "":
            self.volume_after = 1
        else:
            try:
                self.volume_after = float(self.ids.volume_after.text)
            except:
                self.volume_after = -10

        if self.volume_after <= 0 or self.volume_after > 60:
            self.volume_after = 60
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Объем не может быть меньше 0 или больше 60 мл!', font_size='17sp'),
                          size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()
        elif self.volume_after <= self.volume_before:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Объем после погружения не может быть меньше/равен объему до погружения!', font_size='17sp'),
                          size_hint=(0.45, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def get_weight(self):
        if self.ids.weight.text == "":
            self.weight = 0
        else:
            try:
                self.weight = float(self.ids.weight.text)
            except:
                self.weight = -10

        if self.weight <= 0:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Масса не может быть меньше 0!', font_size='17sp'), size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def count_density(self):
        try:
            density = (self.weight / (self.volume_after - self.volume_before)) * 1000
        except:
            density = 0
        popup = Popup(title='Результат', title_size='20sp',
                      content=Label(text=f'Плотность тела = {density:.3f} [кг/м^3]', font_size='17sp'), size_hint=(0.3, 0.16))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def archimedes_force_explanation(self):
        popup = Popup(title='Пояснение', title_size='20sp',
                      content=Label(text=f'ρ = m / V [кг/м^3]\nV = Vпосле - Vдо\nm - масса тела[кг]\nV - объем тела[м^3]', font_size='17sp'), size_hint=(0.16, 0.23))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def archimedes_force_task(self):
        popup = Popup(title='Задача', title_size='20sp',
                      content=Label(text='Используя рычажные весы, мензурку, стакан с водой, цилиндр, соберите экспериментальную установку для измерения плотности материала,\nиз которого изготовлен цилиндр, опускаемый в воду. Абсолютную погрешность измерения массы принять равной ± 1г,\nабсолютную погрешность измерения объёма ± 2мл.', font_size='17sp'), size_hint=(0.8, 0.18))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def go_back(self):
        app = MDApp.get_running_app()
        app.root.transition.direction = "right"
        app.root.current = "set_selection_mechanics"

    def open_account(self):
        global previous
        previous = "mechanics_archimedesforce"
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "account_screen"


lines = []
pairs = []


class ElectricityScreen(Screen):
    global icons
    global graph
    global lines
    global pairs

    def __init__(self, **kwargs):
        global variant
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.ids.top_bar.title = "Электричество"
        self.canvas.before.add(Color(0.9, 0.9, 0.9, 1))
        self.canvas.before.add(Line(width=1.5))
        self.checked = False
        self.voltage = 0
        self.amperage_force = 0
        self.time = 0

        cell_size = 50  # размер ячейки сетки
        win_width, win_height = Window.size

        for i in range(int(win_width / cell_size) + 1):  # вертикальные линии
            x = i * cell_size
            self.canvas.before.add(Line(points=[x, 0, x, win_height], width=1))
        for i in range(int(win_height / cell_size) + 1):  # горизонтальные линии
            y = i * cell_size
            self.canvas.before.add(Line(points=[0, y, win_width, y], width=1))

    def go_back(self):
        app = MDApp.get_running_app()
        app.root.transition.direction = "right"
        app.root.current = "section_selection"

    def open_account(self):
        global previous
        previous = "electricity"
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "account_screen"

    def check_scheme(self):
        first = 1
        last = 0
        source_in = False
        resistor_in = False
        try:
            first = pairs[0][0]
            last = pairs[0][1]
            for i in range(1, len(pairs)):
                if pairs[i][0].source == "images/source.png" or pairs[i][1].source == "images/source.png":
                    source_in = True

                if pairs[i][0].source == "images/resistor.png" or pairs[i][1].source == "images/resistor.png":
                    resistor_in = True

                if last == pairs[i][0]:
                    last = pairs[i][1]
                elif last == pairs[i][1]:
                    last = pairs[i][0]
        except:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Неправильная схема!', font_size='17sp'), size_hint=(0.16, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

        if first == last and source_in and resistor_in:
            popup = Popup(title='Молодец!', title_size='20sp',
                          content=Label(text='Правильная схема!', font_size='17sp'), size_hint=(0.16, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()
            self.checked = True
        else:
            popup = Popup(title='Ошибка', content=Label(text='Неправильная схема!'), size_hint=(0.16, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def clear_scheme(self):
        for icon in icons:
            self.remove_widget(icon)
        icons.clear()
        pairs.clear()

    def make_element(self, element_path):
        element = DraggableElement(source=element_path)
        width = 1920
        height = 1080
        element.pos = [width / 2, height / 2]
        self.add_widget(element)
        for icon in icons:
            if element.pos == icon.pos:
                element.pos = [icon.pos[0], icon.pos[1] + 50]
        icons.append(element)

    def electricity_task1(self):
        popup = Popup(title='Задача 1', title_size='20sp',
                      content=Label(text='Используя источник тока, вольтметр, амперметр, соединительные провода, резистор, обозначенный R1,\nсоберите экспериментальную установку для определения мощности, выделяемой на резисторе.\nУстановите в цепи силу тока 0,3 А. Абсолютная погрешность измерения силы тока с помощью амперметра равна ± 0,1 А;\nабсолютная погрешность измерения напряжения с помощью вольтметра равна ±0,2 В.', font_size='17sp'), size_hint=(0.66, 0.2))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def electricity_task2(self):
        popup = Popup(title='Задача 2', title_size='20sp',
                      content=Label(text='Соберите экспериментальную установку для определения работы электрического тока, совершаемой в резисторе,\nиспользуя источник тока, вольтметр, амперметр, соединительные провода и резистор, обозначенный R2.\nУстановите в цепи силу тока 0,5 А. Определите работу электрического тока в резисторе в течение 5 мин.\nАбсолютная погрешность измерения силы тока с помощью амперметра равна ± 0,1 А;\nабсолютная погрешность измерения напряжения с помощью вольтметра равна ±0,2 В.', font_size='17sp'), size_hint=(0.65, 0.25))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def electricity_explanation(self):
        popup = Popup(title='Пояснение', title_size='20sp',
                      content=Label(text='Задача 1:\nP = U * I [Вт]\nP - мощность[Вт]\nU - напряжение[В]\nI - сила тока[А]\n----------------------\nЗадача 2:\nA = P * t [Дж]\nA - работа[Дж]\nt - время[с]', font_size='17sp'), size_hint=(0.12, 0.35))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def get_voltage(self):
        if self.ids.voltage.text == "":
            self.voltage = 1
        else:
            try:
                self.voltage = int(self.ids.voltage.text)
            except:
                self.voltage = -10

        if self.voltage <= 0:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Напряжение не может быть меньше 0!', font_size='17sp'),
                          size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def get_amperage_force(self):
        if self.ids.amperage_force.text == "":
            self.amperage_force = 1
        else:
            try:
                self.amperage_force = int(self.ids.amperage_force.text)
            except:
                self.amperage_force = -10

        if self.amperage_force <= 0:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Сила тока не может быть меньше 0!', font_size='17sp'),
                          size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def get_time(self):
        if self.ids.time.text == "":
            self.time = 1
        else:
            try:
                self.time = int(self.ids.time.text)
            except:
                self.time = -10

        if self.time <= 0:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Время не может быть меньше 0!', font_size='17sp'),
                          size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def count_power(self):
        if self.checked:
            answer = self.voltage * self.amperage_force
            popup = Popup(title='Ответ', title_size='20sp',
                          content=Label(text=f'Ответ - {answer} [Вт]', font_size='17sp'), size_hint=(0.16, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()
        else:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Проверьте схему!', font_size='17sp'), size_hint=(0.16, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168/255, 228/255, 160/255, 1).rgba
            popup.open()

    def count_amperage_force_work(self):
        if self.checked:
            try:
                self.voltage = float(self.ids.voltage.text)
            except:
                popup = Popup(title='Ошибка', title_size='20sp',
                              content=Label(text='Введите напряжение!', font_size='17sp'), size_hint=(0.16, 0.16))
                popup.overlay_color = Color(1, 1, 1, 0).rgba
                popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
                popup.open()

            try:
                self.amperage_force = float(self.ids.amperage_force.text)
            except:
                popup = Popup(title='Ошибка', title_size='20sp',
                              content=Label(text='Введите силу тока!', font_size='17sp'), size_hint=(0.16, 0.16))
                popup.overlay_color = Color(1, 1, 1, 0).rgba
                popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
                popup.open()

            try:
                self.time = float(self.ids.time.text)
            except:
                popup = Popup(title='Ошибка', title_size='20sp',
                              content=Label(text='Введите время!', font_size='17sp'), size_hint=(0.16, 0.16))
                popup.overlay_color = Color(1, 1, 1, 0).rgba
                popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
                popup.open()

            try:
                answer = self.voltage * self.amperage_force * self.time * 60
                popup = Popup(title='Ответ', title_size='20sp',
                              content=Label(text=f'Ответ - {answer} [Дж]', font_size='17sp'), size_hint=(0.16, 0.16))
                popup.overlay_color = Color(1, 1, 1, 0).rgba
                popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
                popup.open()
            except:
                print("checked")
        else:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Проверьте схему!', font_size='17sp'), size_hint=(0.16, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168/255, 228/255, 160/255, 1).rgba
            popup.open()


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
        self.ids.top_bar.title = "Оптика"
        self.focus_distance = 0
        self.focus_line_inversed = None
        self.focus_inversed = None
        self.focus_mark = None
        self.focus_mark_inversed = None
        self.focus_line = Line()
        self.lens_placed = False
        self.rays_shown = False
        self.center_x = Window.size[0] / 2
        self.center_y = Window.size[1] / 2
        self.arrow_size = 20
        self.canvas.before.add(Color(0, 0, 0, 1))
        self.canvas.before.add(Line(points=[self.center_x - 900, self.center_y, self.center_x + 900,
                                            self.center_y], width=5))

    def change_lens(self, lens_type):
        for item in self.items:
            self.canvas.before.remove(item)
        self.items.clear()

        if lens_type == "conv":
            self.items.append(Line(points=[self.center_x, self.center_y - 300, self.center_x, self.center_y + 300], width=5))
            self.items.append(Line(points=[self.center_x - self.arrow_size, self.center_y - 300 + self.arrow_size,
                                           self.center_x, self.center_y - 300, self.center_x + self.arrow_size,
                                           self.center_y - 300 + self.arrow_size], width=5))
            self.items.append(Line(points=[self.center_x - self.arrow_size, self.center_y + 300 - self.arrow_size,
                                           self.center_x, self.center_y + 300, self.center_x + self.arrow_size,
                                           self.center_y + 300 - self.arrow_size], width=5))

        elif lens_type == "div":
            self.items.append(Line(points=[self.center_x, self.center_y - 300, self.center_x, self.center_y + 300], width=5))
            self.items.append(Line(points=[self.center_x - self.arrow_size, self.center_y - 300 - self.arrow_size,
                                           self.center_x, self.center_y - 300, self.center_x + self.arrow_size,
                                           self.center_y - 300 - self.arrow_size], width=5))
            self.items.append(Line(points=[self.center_x - self.arrow_size, self.center_y + 300 + self.arrow_size,
                                           self.center_x, self.center_y + 300, self.center_x + self.arrow_size,
                                           self.center_y + 300 + self.arrow_size], width=5))
        self.lens_placed = True

    def make_lens(self, lens_type):
        self.lens_type = lens_type
        self.change_lens(lens_type)
        for item in self.items:
            self.canvas.before.add(item)

    def update_focus_distance(self):
        global exists

        if self.lens_placed and self.rays_shown:
            if exists:
                self.canvas.before.remove(self.focus_line)
                self.canvas.before.remove(self.focus)
                self.canvas.before.remove(self.focus_line_inversed)
                self.canvas.before.remove(self.focus_inversed)
                self.remove_widget(self.focus_mark)
                self.remove_widget(self.focus_mark_inversed)

            if self.ids.focus_distance.text == "":
                self.focus_distance = 1
            else:
                try:
                    self.focus_distance = float(self.ids.focus_distance.text) * 1000
                except:
                    self.focus_distance = -10

            if self.focus_distance == 0:
                exists = False
            elif self.focus_distance < 0:
                popup = Popup(title='Ошибка', title_size='20sp',
                              content=Label(text='Фокусное расстояние не может быть меньше 0!', font_size='17sp'),
                              size_hint=(0.3, 0.16))
                popup.overlay_color = Color(1, 1, 1, 0).rgba
                popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
                popup.open()
                exists = False
            else:
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
                self.focus_inversed = Line(points=[focus_x, focus_y - 20, focus_x, focus_y, focus_x, focus_y + 20],
                                           width=7)
                self.canvas.before.add(self.focus_inversed)

                self.add_widget(self.focus_mark)
                self.add_widget(self.focus_mark_inversed)
                exists = True
        else:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Сначала установите линзу и отобразите лучи', font_size='17sp'),
                          size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def change_rays(self, rays_type):
        if self.lens_placed:
            self.rays_shown = True

            self.rays_type = rays_type

            for item in self.items_rays:
                self.canvas.before.remove(item)
            self.items_rays.clear()

            if self.lens_type == "conv":
                if rays_type == "parallel":
                    self.items_rays.append(
                        Line(points=[self.center_x - 900, self.center_y + 250, self.center_x, self.center_y + 250],
                             width=5))
                    self.items_rays.append(
                        Line(points=[self.center_x - 900, self.center_y + 125, self.center_x, self.center_y + 125],
                             width=5))
                    self.items_rays.append(
                        Line(points=[self.center_x - 900, self.center_y - 125, self.center_x, self.center_y - 125],
                             width=5))
                    self.items_rays.append(
                        Line(points=[self.center_x - 900, self.center_y - 250, self.center_x, self.center_y - 250],
                             width=5))
                else:
                    if self.focus_distance == 0:
                        popup = Popup(title='Ошибка', title_size='20sp',
                                      content=Label(text=f'Введите фокусное расстояние!', font_size='17sp'),
                                      size_hint=(0.3, 0.16))
                        popup.overlay_color = Color(1, 1, 1, 0).rgba
                        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
                        popup.open()
                    else:
                        self.items_rays.append(
                            Line(points=[self.center_x - self.focus_distance, self.center_y, self.center_x,
                                         self.center_y + 250], width=5))
                        self.items_rays.append(
                            Line(points=[self.center_x - self.focus_distance, self.center_y, self.center_x,
                                         self.center_y + 125], width=5))
                        self.items_rays.append(
                            Line(points=[self.center_x - self.focus_distance, self.center_y, self.center_x,
                                         self.center_y - 125], width=5))
                        self.items_rays.append(
                            Line(points=[self.center_x - self.focus_distance, self.center_y, self.center_x,
                                         self.center_y - 250], width=5))
            else:
                if rays_type == "parallel":
                    self.items_rays.append(
                        Line(points=[self.center_x - 900, self.center_y + 250, self.center_x, self.center_y + 250],
                             width=5))
                    self.items_rays.append(
                        Line(points=[self.center_x - 900, self.center_y + 125, self.center_x, self.center_y + 125],
                             width=5))
                    self.items_rays.append(
                        Line(points=[self.center_x - 900, self.center_y - 125, self.center_x, self.center_y - 125],
                             width=5))
                    self.items_rays.append(
                        Line(points=[self.center_x - 900, self.center_y - 250, self.center_x, self.center_y - 250],
                             width=5))
                else:
                    if self.focus_distance == 0:
                        popup = Popup(title='Ошибка', title_size='20sp',
                                      content=Label(text=f'Введите фокусное расстояние!', font_size='17sp'),
                                      size_hint=(0.3, 0.16))
                        popup.overlay_color = Color(1, 1, 1, 0).rgba
                        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
                        popup.open()
                    else:
                        self.items_rays.append(
                            Line(points=[self.center_x - self.focus_distance, self.center_y, self.center_x,
                                         self.center_y + 250], width=5))
                        self.items_rays.append(
                            Line(points=[self.center_x - self.focus_distance, self.center_y, self.center_x,
                                         self.center_y + 125], width=5))
                        self.items_rays.append(
                            Line(points=[self.center_x - self.focus_distance, self.center_y, self.center_x,
                                         self.center_y - 125], width=5))
                        self.items_rays.append(
                            Line(points=[self.center_x - self.focus_distance, self.center_y, self.center_x,
                                         self.center_y - 250], width=5))
        else:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text='Сначала установите линзу', font_size='17sp'), size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

    def make_rays(self, rays_type):
        self.change_rays(rays_type)
        for item in self.items_rays:
            self.canvas.before.add(item)

    def show_path(self):
        if self.focus_distance == 0:
            popup = Popup(title='Ошибка', title_size='20sp',
                          content=Label(text=f'Введите фокусное расстояние!', font_size='17sp'), size_hint=(0.3, 0.16))
            popup.overlay_color = Color(1, 1, 1, 0).rgba
            popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
            popup.open()

        for item in self.items_path:
            self.canvas.before.remove(item)
        self.items_path.clear()

        if self.focus_distance != 0:
            if self.lens_type == "conv":
                if self.rays_type == "parallel":
                    self.items_path.append(
                        Line(
                            points=[self.center_x, self.center_y + 250, self.center_x + self.focus_distance,
                                    self.center_y], width=5))
                    self.items_path.append(
                        Line(
                            points=[self.center_x, self.center_y + 125, self.center_x + self.focus_distance,
                                    self.center_y], width=5))
                    self.items_path.append(
                        Line(
                            points=[self.center_x, self.center_y - 125, self.center_x + self.focus_distance,
                                    self.center_y], width=5))
                    self.items_path.append(
                        Line(
                            points=[self.center_x, self.center_y - 250, self.center_x + self.focus_distance,
                                    self.center_y], width=5))
                else:
                    self.items_path.append(
                        Line(points=[self.center_x, self.center_y + 250, self.center_x + 900, self.center_y + 250],
                             width=5))
                    self.items_path.append(
                        Line(points=[self.center_x, self.center_y + 125, self.center_x + 900, self.center_y + 125],
                             width=5))
                    self.items_path.append(
                        Line(points=[self.center_x, self.center_y - 125, self.center_x + 900, self.center_y - 125],
                             width=5))
                    self.items_path.append(
                        Line(points=[self.center_x, self.center_y - 250, self.center_x + 900, self.center_y - 250],
                             width=5))
            else:
                if self.rays_type == "parallel":
                    self.items_path.append(
                        Line(
                            points=[self.center_x - self.focus_distance, self.center_y, self.center_x,
                                    self.center_y + 250], width=1))
                    self.items_path.append(
                        Line(
                            points=[self.center_x - self.focus_distance, self.center_y, self.center_x,
                                    self.center_y + 125], width=1))
                    self.items_path.append(
                        Line(
                            points=[self.center_x - self.focus_distance, self.center_y, self.center_x,
                                    self.center_y - 125], width=1))
                    self.items_path.append(
                        Line(
                            points=[self.center_x - self.focus_distance, self.center_y, self.center_x,
                                    self.center_y - 250], width=1))

                    self.items_path.append(
                        Line(points=[self.center_x, self.center_y + 250, self.center_x + self.focus_distance,
                                     self.center_y + 500], width=5))
                    self.items_path.append(
                        Line(points=[self.center_x, self.center_y + 125, self.center_x + self.focus_distance,
                                     self.center_y + 250], width=5))
                    self.items_path.append(
                        Line(points=[self.center_x, self.center_y - 125, self.center_x + self.focus_distance,
                                     self.center_y - 250], width=5))
                    self.items_path.append(
                        Line(points=[self.center_x, self.center_y - 250, self.center_x + self.focus_distance,
                                     self.center_y - 500], width=5))
                else:
                    self.items_path.append(
                        Line(points=[self.center_x - self.focus_distance, self.center_y - 250, self.center_x,
                                     self.center_y], width=1))
                    self.items_path.append(
                        Line(points=[self.center_x - self.focus_distance, self.center_y - 125, self.center_x,
                                     self.center_y], width=1))
                    self.items_path.append(
                        Line(points=[self.center_x - self.focus_distance, self.center_y + 125, self.center_x,
                                     self.center_y], width=1))
                    self.items_path.append(
                        Line(points=[self.center_x - self.focus_distance, self.center_y + 250, self.center_x,
                                     self.center_y], width=1))
                    self.items_path.append(
                        Line(points=[self.center_x - self.focus_distance, self.center_y - 250, self.center_x,
                                     self.center_y + 250], width=1))
                    self.items_path.append(
                        Line(points=[self.center_x - self.focus_distance, self.center_y - 125, self.center_x,
                                     self.center_y + 125], width=1))
                    self.items_path.append(
                        Line(points=[self.center_x - self.focus_distance, self.center_y + 125, self.center_x,
                                     self.center_y - 125], width=1))
                    self.items_path.append(
                        Line(points=[self.center_x - self.focus_distance, self.center_y + 250, self.center_x,
                                     self.center_y - 250], width=1))

                    self.items_path.append(
                        Line(points=[self.center_x, self.center_y + 250, self.center_x + self.focus_distance,
                                     self.center_y + 750], width=5))
                    self.items_path.append(
                        Line(points=[self.center_x, self.center_y + 125, self.center_x + self.focus_distance,
                                     self.center_y + 375], width=5))
                    self.items_path.append(
                        Line(points=[self.center_x, self.center_y - 125, self.center_x + self.focus_distance,
                                     self.center_y - 375], width=5))
                    self.items_path.append(
                        Line(points=[self.center_x, self.center_y - 250, self.center_x + self.focus_distance,
                                     self.center_y - 750], width=5))

        for item in self.items_path:
            self.canvas.before.add(item)

    def optics_explanation(self):
        popup = Popup(title='Пояснение',
                      title_size='20sp', content=Label(text='D = 1 / F [дптр]\nD - оптическая сила линзы[дптр]\nF - длинна фокусного расстояния[м]', font_size='17sp'), size_hint=(0.23, 0.18))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def optics_task(self):
        popup = Popup(title='Задача', title_size='20sp',
                      content=Label(text='Используя собирающую линзу 1, экран и линейку, соберите экспериментальную установку для определения оптической силы линзы.\nВ качестве источника света используйте солнечный свет от удалённого окна.', font_size='17sp'), size_hint=(0.73, 0.16))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()

    def go_back(self):
        app = MDApp.get_running_app()
        app.root.transition.direction = "right"
        app.root.current = "section_selection"

    def open_account(self):
        global previous
        previous = "optics"
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "account_screen"

    def count_optical_power(self):
        try:
            optical_power = 1 / self.focus_distance
        except:
            optical_power = 0
        popup = Popup(title='Результат', title_size='20sp',
                      content=Label(text=f'Оптическая сила = {optical_power:.3f}', font_size='17sp'),
                      size_hint=(0.3, 0.16))
        popup.overlay_color = Color(1, 1, 1, 0).rgba
        popup.separator_color = Color(168 / 255, 228 / 255, 160 / 255, 1).rgba
        popup.open()


class SetScreenElectricity(Screen):
    def go_back(self):
        app = MDApp.get_running_app()
        app.root.transition.direction = "right"
        app.root.current = "section_selection"

    def open_account(self):
        global previous
        previous = "section_selection"
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "account_screen"

    def change(self, number):
        global variant
        variant = number


class SetScreenMechanics(Screen):
    def go_back(self):
        app = MDApp.get_running_app()
        app.root.transition.direction = "right"
        app.root.current = "section_selection"

    def open_account(self):
        global previous
        previous = "set_selection_mechanics"
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "account_screen"

    def change(self, number, where):
        app = MDApp.get_running_app()
        app.root.current = where
        app.root.transition.direction = "left"
        global variant
        variant = number
        mechanics_frictionforce_screen.update()
        mechanics_fluctuations_screen.update()
        mechanics_blocks_screen.update()
        mechanics_archimedesforce_screen.update()


class SetScreenOptics(Screen):
    def go_back(self):
        app = MDApp.get_running_app()
        app.root.transition.direction = "right"
        app.root.current = "section_selection"

    def open_account(self):
        global previous
        previous = "optics"
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "account_screen"

    def change(self, number):
        app = MDApp.get_running_app()
        global variant
        variant = number


class AccountScreen(Screen):
    def update(self, user):
        self.ids.sigma.text = f"Ваше имя: {user}"

    def go_back(self):
        global previous
        app = MDApp.get_running_app()
        app.root.current = previous
        app.root.transition.direction = "right"


class Online_LabApp(MDApp):
    def build(self):
        global account
        global mechanics_archimedesforce_screen
        global mechanics_fluctuations_screen
        global mechanics_blocks_screen
        global mechanics_frictionforce_screen
        global electricity_screen
        global optics_screen
        global section_selection
        global set_selection_mechanics

        screen_manager = ScreenManager()

        login_screen = LoginScreen(name="login")
        screen_manager.add_widget(login_screen)

        registration_screen = RegistrationScreen(name="registration")
        screen_manager.add_widget(registration_screen)

        mechanics_frictionforce_screen = MechanicsFrictionForceScreen(name="mechanics_frictionforce")
        screen_manager.add_widget(mechanics_frictionforce_screen)

        mechanics_fluctuations_screen = MechanicsFluctuationsScreen(name="mechanics_fluctuations")
        screen_manager.add_widget(mechanics_fluctuations_screen)

        mechanics_blocks_screen = MechanicsBlocksScreen(name="mechanics_blocks")
        screen_manager.add_widget(mechanics_blocks_screen)

        mechanics_archimedesforce_screen = MechanicsArchimedesForceScreen(name="mechanics_archimedesforce")
        screen_manager.add_widget(mechanics_archimedesforce_screen)

        electricity_screen = ElectricityScreen(name="electricity")
        screen_manager.add_widget(electricity_screen)

        optics_screen = OpticsScreen(name="optics")
        screen_manager.add_widget(optics_screen)

        section_selection = ScreenSelection(name="section_selection")
        screen_manager.add_widget(section_selection)

        set_selection_mechanics = SetScreenMechanics(name="set_selection_mechanics")
        screen_manager.add_widget(set_selection_mechanics)

        account_screen = AccountScreen(name="account_screen")
        screen_manager.add_widget(account_screen)
        account = account_screen

        return screen_manager


if __name__ == '__main__':
    Online_LabApp().run()