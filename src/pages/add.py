import streamlit as st
import pandas as pd
import os

from pages.home import authenticated_menu as menu

from database import (
    get_user_login,
    check_table,
    add_dataset,
)

from utils import (
    create_user_folder,
    image_saver,
    image_formatter,
)

st.set_page_config(page_title="Upload Images to DataFrame", layout="wide")

# Папка для сохранения загруженных изображений
UPLOAD_FOLDER = 'D:\\Upload_dataset'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def main():
    menu()
    st.title('Загрузка изображений и добавление данных в DataFrame')

    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.warning("Пожалуйста, войдите в аккаунт.")
        st.stop()

    if 'user_id' in st.session_state:
        user_id = st.session_state.user_id

    user_login = get_user_login(user_id)
    user_folder = create_user_folder(user_login, UPLOAD_FOLDER)

    # Добавление элемента загрузки нескольких файлов на веб-страницу
    uploaded_files = st.file_uploader("Загрузите изображения", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    data_name = st.text_input("Укажите название для датасета")
    st.text("Укажите параметры к которым будут приведены изображения:")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Высота px")
    with col2:
        st.text_input("Ширина px")

    st.radio(
        "Цветовой формат",
        [":rainbow[RGB]", "Gray"])

    if st.button("Загрузить изображения"):
        if not data_name:
            st.warning("Поле не должно быть пустым!")
            exit()

        new_folder_path = os.path.join(user_folder, data_name)
        new_folder_path = new_folder_path.replace(os.sep, '/')
        check_table()

        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)

        data = image_saver(uploaded_files, new_folder_path)
        add_dataset(data_name, new_folder_path, user_id)
        df = pd.DataFrame(data)
        st.success("Данные успешно добавлены!")
        st.write("Добавленные данные:")
        st.write(df.to_html(escape=False, formatters={"Изображение": image_formatter}), unsafe_allow_html=True)
    else:
        st.error("Нет файлов для загрузки")

if __name__ == "__main__":
    main()
