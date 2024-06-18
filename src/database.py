import hashlib
import sqlite3
import streamlit as st

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Функция для получения логина пользователя из базы данных
def get_user_login(user_id):
    # Подключение к базе данных
    conn = sqlite3.connect('Augment.db')
    cursor = conn.cursor()

    # Запрос к базе данных для получения логина пользователя
    cursor.execute("SELECT username FROM Users WHERE userID=?", (user_id,))
    user_login = cursor.fetchone()[0]

    # Закрытие соединения с базой данных
    conn.close()

    return user_login

def check_user_table():
    conn = sqlite3.connect('Augment.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        userID INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    )
    ''')
    conn.commit()
    conn.close()

# Функция для проверки пользователя в базе данных
def check_user(login, password):
    conn = sqlite3.connect('Augment.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT userID FROM Users WHERE username=? AND password=?
    ''', (login, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    if user:
        return user[0]  # Вернуть userID
    else:
        return None  # Пользователь не найден

# Функция для добавления пользователя в базу данных
def add_user(login, password, email):
    conn = sqlite3.connect('Augment.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO Users (username, password, email)
    VALUES (?, ?, ?)
    ''', (login, hash_password(password), email))
    conn.commit()
    conn.close()

# Функция для получения логина пользователя из базы данных
def get_user_login(user_id):
    # Подключение к базе данных
    conn = sqlite3.connect('Augment.db')
    cursor = conn.cursor()

    # Запрос к базе данных для получения логина пользователя
    cursor.execute("SELECT username FROM Users WHERE userID=?", (user_id,))
    user_login = cursor.fetchone()[0]

    # Закрытие соединения с базой данных
    conn.close()

    return user_login

def check_table():
    conn = sqlite3.connect('Augment.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Datasets (
        DataID INTEGER PRIMARY KEY AUTOINCREMENT,
        dataname TEXT NOT NULL,
        datapath TEXT NOT NULL,
        userID INTEGER NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def add_dataset(dataname, datapath, userID):
    conn = sqlite3.connect('Augment.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO Datasets (dataname, datapath, userID)
    VALUES (?, ?, ?)
    ''', (dataname, datapath, userID))
    conn.commit()
    conn.close()