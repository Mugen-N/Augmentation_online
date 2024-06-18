import os
import io
import streamlit as st
import albumentations as A
from PIL import Image
from pages.home import authenticated_menu as menu

from utils import (
    load_augmentations_config,
    get_arguments,
    get_placeholder_params,
    select_transformations,
)
from visuals import (
    select_image,
    show_docstring,
    get_transormations_params,
)


def main():

    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.warning("Пожалуйста, войдите в аккаунт.")
        st.stop()

    menu()

    # получаем параметры CLI: путь к изображениям и ширину изображения
    path_to_images, width_original = get_arguments()

    if not os.path.isdir(path_to_images):  # если путь существует возвращает TRUE
        st.title("Не существующий путь: " + path_to_images)
    else:
        # # выберите тип интерфейса
        # interface_type = st.sidebar.radio(
        #     "Выберите тип интерфейса", ["Simple", "Professional"]
        # )

        # выбор изображения
        status, image = select_image(path_to_images, "Professional")
        if status == 1:
            st.title("Невозможно загрузить изображение")
        if status == 2:
            st.title("Пожалуйста, загрузите изображение")
        else:
            # возвращает словарь параметров изображения высота ширина и тд
            placeholder_params = get_placeholder_params(image)

            # Возвращает словарь всех json аугментаций
            augmentations = load_augmentations_config(
                placeholder_params, "configs/augmentations.json"
            )

            # получение списка названий преобразований
            transform_names = select_transformations(augmentations, "Professional")

            # получение списка готовых трансформаций из библиотеки A
            transforms = get_transormations_params(transform_names, augmentations)

            try:
                # применение преобразований к изображению
                data = A.ReplayCompose(transforms)(image=image)
                error = 0
            except ValueError:
                error = 1
                st.title(
                    "Произошла ошибка. \
                        Скорее всего, вы ввели неверный набор параметров. \
                        Проверьте преобразования, которые изменяют форму изображения."
                )

            if error == 0:
                augmented_image = data["image"]

                # show the images
                width_transformed = int(
                    width_original / image.shape[1] * augmented_image.shape[1]
                )

                st.image(image, caption="Оригинальное изображение", width=width_original)
                st.image(
                    augmented_image,
                    caption="Аугментированое изображение",
                    width=width_transformed,
                )

                image = Image.fromarray(augmented_image)
                buffer = io.BytesIO()
                image.save(buffer, format="JPEG")
                buffer.seek(0)
                byte_im = buffer.read()

                st.download_button(
                    label="Скачать изображение",
                    data=byte_im,
                    file_name="reasoned.jpeg",
                    mime="image/png"
                )

                # вывод информации о трансформациях
                for transform in transforms:
                    show_docstring(transform)
                    st.code(str(transform))


if __name__ == "__main__":
    main()
