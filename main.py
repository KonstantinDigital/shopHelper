#!/usr/bin/env python3

import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window

EMPTY_PROD = "Введите название продукта"
EMPTY_DEPT = "Введите название отдела"
LABEL_WIDTH = Window.width - 20


class MainApp(App):
    def __init__(self):
        super().__init__()
        self.conn, self.cur = self.sql_connection()
        self.main_layout = BoxLayout(orientation="vertical")
        self.prod_input = TextInput(multiline=False, readonly=False, halign="right", font_size=16, size_hint_y=.05)
        self.prod_input.bind(text=self.on_text, focus=self.on_focus_prod)
        self.txt_variants = TextInput(multiline=False, readonly=True, halign="right", font_size=16, disabled=False,
                                      size_hint_y=.05)
        self.txt_variants.bind(on_double_tap=self.push_txt_variant)
        self.dept_input = TextInput(multiline=False, readonly=False, halign="right", font_size=16, size_hint_y=.05)
        self.dept_input.bind(focus=self.on_focus_dept)
        self.buttons = ["Удалить", "Очистить", "Добавить"]
        self.btn_layout = BoxLayout(size_hint=(1, .1))
        self.scr_prod_list = ScrollView(size_hint=(1, .55))
        self.prod_list_layout = GridLayout(cols=1, size_hint_y=None)
        self.prod_list_layout.bind(minimum_height=self.prod_list_layout.setter('height'))
        self.shop_card = self.create_shop_card()
        self.foot_layout = BoxLayout(size_hint=(1, .1))
        self.num_foot_layout = BoxLayout(orientation="vertical", size_hint=(.25, 1))
        self.num_plus = TextInput(multiline=False, halign="right", font_size=17)
        self.num_minus = TextInput(multiline=False, halign="right", font_size=17)
        self.btn_foot_layout = BoxLayout(orientation="vertical", size_hint=(.1, .98))
        self.btn_plus = Button(text="+", font_size=35, size_hint_y=.51)
        self.btn_minus = Button(text="-", font_size=70, size_hint_y=.49)
        self.summa_input = TextInput(multiline=False, readonly=True, halign="right", font_size=50, size_hint_x=.45)
        self.clr_button = Button(text="Сброс", pos_hint={"center_x": 0.5, "center_y": 0.49},
                                 font_size=15, size_hint_x=.2)

    def build(self):
        self.create_sql_table()
        self.main_layout.add_widget(self.prod_input)
        self.main_layout.add_widget(self.txt_variants)
        self.main_layout.add_widget(self.dept_input)
        for label in self.buttons:
            button = Button(text=label, pos_hint={"center_x": 0.5, "center_y": 0.498}, font_size=20)
            button.bind(on_press=self.on_button_press)
            self.btn_layout.add_widget(button)
        self.main_layout.add_widget(self.btn_layout)
        for purchase in self.shop_card:
            btn_purchase = Button(text=purchase[0], font_size=16, size_hint_y=None, height=30,
                                  text_size=(LABEL_WIDTH, 24), halign="right", valign="top")
            btn_purchase.bind(on_press=self.on_purchase_press)
            self.prod_list_layout.add_widget(btn_purchase)
        self.scr_prod_list.add_widget(self.prod_list_layout)
        self.main_layout.add_widget(self.scr_prod_list)
        self.num_foot_layout.add_widget(self.num_plus)
        self.num_foot_layout.add_widget(self.num_minus)
        self.btn_foot_layout.add_widget(self.btn_plus)
        self.btn_foot_layout.add_widget(self.btn_minus)
        self.foot_layout.add_widget(self.num_foot_layout)
        self.foot_layout.add_widget(self.btn_foot_layout)
        self.foot_layout.add_widget(self.summa_input)
        self.foot_layout.add_widget(self.clr_button)
        self.main_layout.add_widget(self.foot_layout)
        return self.main_layout

    @staticmethod
    def on_focus_prod(instance, value):
        if value:
            if instance.text == EMPTY_PROD:
                instance.text = ""
        else:
            if instance.text == "":
                instance.text = EMPTY_PROD

    @staticmethod
    def on_focus_dept(instance, value):
        if value:
            if instance.text == EMPTY_DEPT:
                instance.text = ""
        else:
            if instance.text == "":
                instance.text = EMPTY_DEPT

    def create_shop_card(self):
        try:
            self.cur.execute("SELECT product_name FROM products JOIN shopping_card "
                             "ON shopping_card.products_id = products.id;")
            shop_card = self.cur.fetchall()
            return shop_card
        except Exception as err:
            print(err)

    def on_button_press(self, instance):
        button_text = instance.text
        if button_text == "Добавить":
            self.add_product()
        elif button_text == "Очистить":
            self.prod_input.text = EMPTY_PROD
            self.dept_input.text = EMPTY_DEPT
        elif button_text == "Удалить":
            self.del_product()

    def on_purchase_press(self, instance):
        purchase = instance.text
        try:
            self.cur.execute("DELETE FROM shopping_card WHERE products_id = "
                             "(SELECT shopping_card.products_id FROM shopping_card "
                             "JOIN products ON shopping_card.products_id = products.id "
                             "WHERE products.product_name = '{0}');".format(purchase))
            self.conn.commit()
            self.prod_list_layout.remove_widget(instance)
        except Exception as err:
            print(err)

    def on_text(self, instance, value):
        if value:
            self.cur.execute("""SELECT product_name, dept_name FROM products 
                                WHERE product_name != '' AND product_name LIKE '{0}%' LIMIT 1;""".format(value))
            product_variant = self.cur.fetchall()
            self.txt_variants.text = product_variant[0][0] if product_variant else ""
            if instance.text == self.txt_variants.text:
                self.dept_input.text = product_variant[0][1] if product_variant else ""
            elif instance.text == EMPTY_PROD:
                self.dept_input.text = EMPTY_DEPT
            else:
                self.dept_input.text = ""

    def push_txt_variant(self, instance):
        if instance.text:
            self.prod_input.text = instance.text

    def sql_connection(self):
        try:
            self.conn = sqlite3.connect("shopping_db.db")
            self.cur = self.conn.cursor()
            return self.conn, self.cur
        except Exception as err:
            print(err)

    def create_sql_table(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY, product_name TEXT UNIQUE "
                         "NOT NULL, dept_name TEXT NOT NULL);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS shopping_card(products_id INT UNIQUE NOT NULL);")
        # try:
        #     products_list = [("Гречка", "Крупы"), ("Рис", "Крупы"), ("Манка", "Крупы"), ("Помидоры", "Овощи"),
        #                      ("Огурцы", "Овощи")]
        #     add_many_products = "INSERT INTO products(product_name, dept_name) VALUES(?, ?);"
        #     self.cur.executemany(add_many_products, products_list)
        # except sqlite3.IntegrityError as err:
        #     if str(err).startswith("UNIQUE"):
        #         print("Данный вид товара уже есть в списке")
        #     if str(err).startswith("NOT NULL"):
        #         print("Значение NULL не допускается")
        #     else:
        #         print(err)
        self.conn.commit()

    def add_product(self):
        product = self.prod_input.text if (self.prod_input.text != EMPTY_PROD) else ""
        product = "'" + product + "'" if product else "NULL"
        dept = self.dept_input.text if (self.dept_input.text != EMPTY_DEPT) else ""
        dept = "'" + dept + "'" if dept else "NULL"
        try:
            self.cur.execute("INSERT INTO products(product_name, dept_name) VALUES({0}, {1});".format(product, dept))
            self.conn.commit()
            self.prod_input.text = EMPTY_PROD
            self.dept_input.text = ""
            self.add_to_prod_list(product)
        except sqlite3.IntegrityError as err:
            if str(err).startswith("UNIQUE"):
                print("Данный товар уже есть в DB")
                self.prod_input.text = EMPTY_PROD
                self.dept_input.text = ""
                self.add_to_prod_list(product)
            elif str(err).startswith("NOT NULL"):
                if self.prod_input.text == "":
                    self.prod_input.text = EMPTY_PROD
                if self.dept_input.text == "":
                    self.dept_input.text = EMPTY_DEPT
                print("Значение NULL не допускается")
            else:
                print(err)

    def add_to_prod_list(self, product):
        try:
            self.cur.execute("""INSERT INTO shopping_card(products_id) 
                             VALUES((SELECT id FROM products WHERE product_name = {0}));""".format(product))
            self.conn.commit()
            btn_purchase = Button(text=product.strip("'"), font_size=16, size_hint_y=None, height=30,
                                  text_size=(LABEL_WIDTH, 24), halign="right", valign="top")
            btn_purchase.bind(on_press=self.on_purchase_press)
            self.prod_list_layout.add_widget(btn_purchase)
        except sqlite3.IntegrityError as err:
            if str(err).startswith("UNIQUE"):
                print("Данный товар уже в списке покупок")
            else:
                print(err)

    def del_product(self):
        product = self.prod_input.text
        dept = self.dept_input.text
        try:
            self.cur.execute("DELETE FROM products WHERE product_name = '{0}' "
                             "AND dept_name = '{1}';".format(product, dept))
            self.conn.commit()
            self.prod_input.text = EMPTY_PROD
            self.dept_input.text = ""
        except Exception as err:
            print(err)


if __name__ == "__main__":
    app = MainApp()
    app.run()
