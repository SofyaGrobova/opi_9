#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sqlite3
import typing as t
from pathlib import Path


def display_products(products: t.List[t.Dict[str, t.Any]]) -> None:

    if products:
        # Заголовок таблицы.
        line = '+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 20,
            '-' * 15
        )
        print(line)
        print(
            '| {:^4} | {:^30} | {:^20} | {:^15} |'.format(
                "№",
                "Наименование товара",
                "Название магазина",
                "Стоимость"
            )
        )
        print(line)
        for idx, product in enumerate(products, 1):
            print(
                '| {:>4} | {:<30} | {:<20} | {:<15} |'.format(
                    idx,
                    product.get('product_name', ''),
                    product.get('product_shop', ''),
                    product.get('product_cost', 0)
                )
            )
            print(line)
    else:
        print("Список пуст")


def create_db(database_path: Path) -> None:
    """
    Создать базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS product_name (
        name_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_title TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_shop TEXT NOT NULL,
        name_id INTEGER NOT NULL,
        product_cost TEXT NOT NULL,
        FOREIGN KEY(name_id) REFERENCES product_name(name_id)
        )
        """
    )
    conn.close()


def add_product(
        database_path: Path,
        product_name: str,
        product_shop: str,
        product_cost: int
) -> None:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT name_id FROM product_name WHERE name_title = ?
        """,
        (product_name,)
    )
    row = cursor.fetchone()
    if row is None:
        cursor.execute(
            """
            INSERT INTO product_name (name_title) VALUES (?)
            """,
            (product_name,)
        )
        name_id = cursor.lastrowid
    else:
        name_id = row[0]
    cursor.execute(
        """
        INSERT INTO products (product_shop, name_id, product_cost)
        VALUES (?, ?, ?)
        """,
        (product_shop, name_id, product_cost)
    )
    conn.commit()
    conn.close()


def select_all(database_path: Path) -> t.List[t.Dict[str, t.Any]]:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT product.product_name, product_shop.name_title, 
        product.product_cost FROM products INNER JOIN product_cost ON 
        product_shop.name_id = products.name_id """
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "product_name": row[0],
            "product_shop": row[1],
            "product_cost": row[2],
        }
        for row in rows
    ]


def select_products(
        database_path: Path, prd_cost: str
) -> t.List[t.Dict[str, t.Any]]:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT products.product_name, product_shop.name_title, 
        products.product_cost
        FROM products
        INNER JOIN product_shop ON product_shop.name_id = products.name_id
        WHERE products.product_cost == ?
        """,
        (prd_cost,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "product_name": row[0],
            "product_shop": row[1],
            "product_cost": row[2],
        }
        for row in rows
    ]


def main(command_line=None):
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.home() / "products.db"),
        help="The database file name"
    )
    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("products")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command")
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new product"
    )
    add.add_argument(
        "-n",
        "--name",
        action="store",
        required=True,
        help="product name"
    )
    add.add_argument(
        "-s",
        "--shop",
        action="store",
        help="product shop"
    )
    add.add_argument(
        "-c",
        "--cost",
        action="store",
        type=str,
        required=True,
        help="product cost"
    )
    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all products"
    )
    select = subparsers.add_parser(
        "select",
        parents=[file_parser],
        help="Select the products"
    )
    select.add_argument(
        "-C",
        "--cost",
        action="store",
        type=str,
        required=True,
        help="The required cost"
    )
    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)
    # Получить путь к файлу базы данных.
    db_path = Path(args.db)
    create_db(db_path)
    if args.command == "add":
        add_product(db_path, args.name, args.shop, args.cost)
    elif args.command == "display":
        display_products(select_all(db_path))
    elif args.command == "select":
        display_products(select_products(db_path, args.type))
        pass


if __name__ == "__main__":
    main()