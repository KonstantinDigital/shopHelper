#!/usr/bin/env python3

import sqlite3


def main():
    conn, cur = sql_connection()
    sql_table(conn, cur)
    add_product(conn, cur)


def add_product(conn, cur):
    product = input("Добавить товар: ")
    dept = input("Отдел: ")
    cur.execute("INSERT INTO products(product_name, dept_name) VALUES('{0}', '{1}');".format(product, dept))
    conn.commit()


def sql_connection():
    try:
        conn = sqlite3.connect("shopping_db.db")
        cur = conn.cursor()
        return conn, cur
    except Exception as e:
        print(e)


def sql_table(conn, cur):
    cur.execute("CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY, product_name TEXT "
                "NOT NULL, dept_name TEXT NOT NULL);")
    cur.execute("CREATE TABLE IF NOT EXISTS shopping_card(products_id INT UNIQUE NOT NULL);")
    conn.commit()


if __name__ == "__main__":
    main()
