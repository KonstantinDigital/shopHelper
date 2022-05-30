#!/usr/bin/env python3

import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class MainApp(App):
    def __init__(self):
        super().__init__()
        self.conn, self.cur = self.sql_connection()
        self.main_layout = BoxLayout(orientation="vertical")
        self.txt_input = TextInput(multiline=False, readonly=False, halign="right", font_size=30)
        self.txt_input.bind(text=self.on_text)
        self.txt_variants = TextInput(multiline=False, readonly=True, halign="right", font_size=30, disabled=True)
        self.txt_variants.bind(on_touch_up=self.push_txt_variant)

    def build(self):
        self.create_sql_table()
        self.main_layout.add_widget(self.txt_input)
        self.main_layout.add_widget(self.txt_variants)
        return self.main_layout

    def on_text(self, instance, value):
        self.cur.execute("""SELECT product_name FROM products 
                            WHERE product_name != '' AND product_name LIKE '{0}%' LIMIT 1;""".format(value))
        product_variant = self.cur.fetchall()
        self.txt_variants.text = product_variant[0][0] if product_variant else ""

    def push_txt_variant(self, instance, value):
        self.txt_input.text = self.txt_variants.text

    def sql_connection(self):
        try:
            self.conn = sqlite3.connect("shopping_db.db")
            self.cur = self.conn.cursor()
            return self.conn, self.cur
        except Exception as e:
            print(e)

    def create_sql_table(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY, product_name TEXT UNIQUE "
                         "NOT NULL, dept_name TEXT NOT NULL);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS shopping_card(products_id INT UNIQUE NOT NULL);")
        try:
            products_list = [("Гречка", "Крупы"), ("Рис", "Крупы"), ("Манка", "Крупы"), ("Помидоры", "Овощи"),
                             ("Огурцы", "Овощи")]
            add_many_products = "INSERT INTO products(product_name, dept_name) VALUES(?, ?);"
            self.cur.executemany(add_many_products, products_list)
        except sqlite3.IntegrityError as err:
            if str(err).startswith("UNIQUE"):
                print("Данный вид товара уже есть в списке")
            if str(err).startswith("NOT NULL"):
                print("Значение NULL не допускается")
            else:
                print(err)
        self.conn.commit()


def add_product(conn, cur):
    product = input("Добавить товар: ")
    product = "'" + product + "'" if product else "NULL"
    dept = input("Отдел: ")
    dept = "'" + dept + "'" if dept else "NULL"
    try:
        cur.execute("INSERT INTO products(product_name, dept_name) VALUES({0}, {1});".format(product, dept))
        conn.commit()
    except sqlite3.IntegrityError as err:
        if str(err).startswith("UNIQUE"):
            print("Данный вид товара уже есть в списке")
        if str(err).startswith("NOT NULL"):
            print("Значение NULL не допускается")
        else:
            print(err)


if __name__ == "__main__":
    app = MainApp()
    app.run()
