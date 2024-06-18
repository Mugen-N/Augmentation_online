import streamlit as st
import sqlite3

from database import (
    check_user_table,
    add_user,
    check_user,
)


@st.experimental_dialog("Регистрация пользователя")
def registration_form():
    st.header("Форма регистрации")

    username = st.text_input("Имя пользователя")
    email = st.text_input("Email")
    password = st.text_input("Пароль", type="password")
    confirm_password = st.text_input("Подтвердите пароль", type="password")

    if st.button("Зарегистрироваться"):
        if username and password and email and confirm_password:
            try:
                if password != confirm_password:
                    st.warning("Пароли не совпадают!")
                else:
                    check_user_table()
                    add_user(username, password, email)
                    st.success(f"Регистрация успешна! Добро пожаловать, {username}!")
                    user = check_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user
                        st.switch_page("pages/home.py")
            except sqlite3.IntegrityError:
                st.error("Логин или Email уже заняты")
        else:
            st.error("Пожалуйста, заполните все поля")


@st.experimental_dialog("Авторизация пользователя")
def login_form():
    st.header("Форма авторизации")

    username = st.text_input("Имя пользователя")
    password = st.text_input("Пароль", type="password")

    if st.button("Войти", key="vhod"):
        if username and password:
            user = check_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user
                st.success(f"С возвращением, {username}!")
                st.switch_page("pages/home.py")
            else:
                st.error("Неверный логин или пароль")
        else:
            st.error("Пожалуйста, заполните все поля")

def main():
    st.title("Добро пожаловать в Аугментацию онлайн")
    st.text("Данное приложение создано для быстрого и комфортного аугментирования наборов данных")

    st.html("""
                  <style>
                    [alt=Logo] {
                      height: 5rem;
                    }
                  </style>
                        """)
    st.logo("logo.png")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Регистрация"):
            registration_form()
    with col2:
        if st.button("Войти"):
            login_form()


if __name__ == "__main__":
    main()
