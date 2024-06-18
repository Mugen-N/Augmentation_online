import streamlit as st
from PIL import Image
import os

from pages.home import authenticated_menu as menu

from database import (
    get_user_login,
)

from utils import (
    create_user_folder,
    create_zip_from_images,
)

st.set_page_config(page_title="Upload Images to DataFrame", layout="wide")


# Папка для сохранения загруженных изображений
UPLOAD_FOLDER = 'D:\\Upload_dataset'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def main():
    menu()
    st.title('Ваши датасеты')

    user_login = get_user_login(st.session_state.user_id)
    user_folder = create_user_folder(user_login, UPLOAD_FOLDER)

    # Получаем список всех элементов в директории
    items = os.listdir(user_folder)
    folders = [item for item in items if os.path.isdir(os.path.join(user_folder, item))]

    st.title('Выберите датасет для просмотра')
    selected_folder = st.selectbox('Папки', folders)

    if selected_folder:
        selected_folder_path = os.path.join(user_folder, selected_folder)
        itemss = os.listdir(selected_folder_path)
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        images = [item for item in itemss if os.path.splitext(item)[1].lower() in image_extensions]

        cols_per_row = 3
        cols = st.columns(cols_per_row)

        for idx, image_name in enumerate(images):
            image_path = os.path.join(selected_folder_path, image_name)
            image = Image.open(image_path)
            col = cols[idx % cols_per_row]
            with col:
                st.image(image, caption=image_name)

        zip_buffer = create_zip_from_images(selected_folder_path, images)
        st.download_button(
            label="Скачать все изображения",
            data=zip_buffer,
            file_name=f"{selected_folder}.zip",
            mime="application/zip"
        )

if __name__ == "__main__":
    main()
