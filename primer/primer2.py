# !/usr/bin/env python3
# -*- cosing: utf-8 -*-

import sqlite3

con = sqlite3.connect('mydatabase.db')

cursor_obj = con.cursor()