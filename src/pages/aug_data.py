import os
import cv2
import streamlit as st
import albumentations as A

from utils import (
    load_augmentations_config,
    get_placeholder_params,
    select_transformations,
    load_image, create_user_folder,
)

from database import get_user_login

from visuals import get_transormations_params

from pages.home import authenticated_menu as menu


# Папка для сохранения загруженных изображений
UPLOAD_FOLDER = 'D:\\Upload_dataset'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def get_image_paths(folder_path):
    image_paths = []
    for root, dirs, files in os.walk(folder_path): # подумать поменять потом
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                image_paths.append({'path': root, 'name': file})
    return image_paths


def main():
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.warning("Пожалуйста, войдите в аккаунт.")
        st.stop()

    menu()

    user_login = get_user_login(st.session_state.user_id)
    user_folder = create_user_folder(user_login, UPLOAD_FOLDER)

    # Получаем список всех элементов в директории
    items = os.listdir(user_folder)
    folders = [item for item in items if os.path.isdir(os.path.join(user_folder, item))]

    st.title('Выберите датасет для аугментации')
    selected_folder = st.selectbox('Папки', folders)
    if selected_folder:
        selected_folder_path = os.path.join(user_folder, selected_folder)
        output_folder = os.path.join(user_folder, selected_folder + "_augmented")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

    image_names_list = get_image_paths(selected_folder_path)


    if not os.path.isdir(output_folder): # если путь существует возвращает TRUE
        st.title("Не существующий путь: " + output_folder)
    else:
        # выберите тип интерфейса
        interface_type = st.sidebar.radio(
            "Выберите тип интерфейса", ["Simple", "Professional"]
        )

    for name in image_names_list:
        image = load_image(name['name'], name['path'])
        resized_img = cv2.resize(image, (256, 256))
        resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
        output_path = os.path.join(output_folder, name['name'])
        cv2.imwrite(output_path, resized_img)
        print(f"Изображение сохранено в: {output_path}")

    placeholder_params = get_placeholder_params(resized_img)

    # Возвращает словарь всех json аугментаций
    augmentations = load_augmentations_config(
        placeholder_params, "configs/augmentations.json"
    )

    # получение списка названий преобразований
    transform_names = select_transformations(augmentations, interface_type)

    # получение списка готовых трансформаций из библиотеки A
    transforms = get_transormations_params(transform_names, augmentations)

    st.text(transforms)

    if st.button('Применить трансформации к датасету'):
        transform = A.ReplayCompose(transforms)
        for filename in os.listdir(output_folder):
            image_path = os.path.join(output_folder, filename)
            image = cv2.imread(image_path)
            if image is None:
                continue
            try:
                # применение преобразований к изображению
                transformed = transform(image=image)
                transformed_image = transformed['image']
                cv2.imwrite(image_path, transformed_image)
                error = 0
            except ValueError:
                error = 1
                st.title(
                    "Произошла ошибка. \
                        Скорее всего, вы ввели неверный набор параметров. \
                        Проверьте преобразования, которые изменяют форму изображения."
                )
        st.success("Датасет успешно аугментирован")
if __name__ == "__main__":
    main()
