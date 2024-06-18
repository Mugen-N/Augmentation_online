import cv2
import streamlit as st

import albumentations as A

from control import param2func
from utils import get_images_list, load_image, upload_image


def select_image(path_to_images: str, interface_type: str = "Professional"):
    """Покажите интерфейс, чтобы выбрать изображение и загрузить его
        с аргументами:
        path_to_images (dict): путь к папке с изображениями
        interface_type (dict): режим используемого интерфейса
         Возвращается:
         (статус, изображение)
        статус (int):
        0 - если все в порядке
        1 - если произошла ошибка при загрузке файла изображения
        2 - если пользователь еще не загрузил фотографию
    """
    image_names_list = get_images_list(path_to_images)
    if len(image_names_list) < 1:
        return 1, 0
    else:
        if interface_type == "Professional":
            image_name = st.sidebar.selectbox(
                "Выбор изображения:", image_names_list + ["Загрузить своё изображение"]
            )
        else:
            image_name = st.sidebar.selectbox("Выбор изображения:", image_names_list)

        if image_name != "Загрузить своё изображение":
            try:
                image = load_image(image_name, path_to_images)
                return 0, image
            except cv2.error:
                return 1, 0
        else:
            try:
                image = upload_image()
                return 0, image
            except cv2.error:
                return 1, 0
            except AttributeError:
                return 2, 0


def show_transform_control(transform_params: dict, n_for_hash: int) -> dict:
    param_values = {"p": 1.0} # Создается словарь param_values с ключом "p" и значением по умолчанию 1.0
                              # которое влияет на вероятность применения аугментации к изображению
    if len(transform_params) == 0:
        st.sidebar.text("Трансформация не имеет параметров")
    else:
        for param in transform_params:
            control_function = param2func[param["type"]] # Получаем значение из cловаря на основе типа параметра
            if isinstance(param["param_name"], list): #Проверяем, является ли имя параметра списком
                returned_values = control_function(**param, n_for_hash=n_for_hash)## Вызываем функцию управления с параметрами
                for name, value in zip(param["param_name"], returned_values): # Распаковываем и присваиваем значения param_values
                    param_values[name] = value
            else:
                param_values[param["param_name"]] = control_function(
                    **param, n_for_hash=n_for_hash
                )
    return param_values #возвращает словарь param_values, содержащий все параметры трансформации с их значениями

def get_transormations_params(transform_names: list, augmentations: dict) -> list:
    transforms = []
    for i, transform_name in enumerate(transform_names): #Проходит цикл по индексам и именам трансформаций
        # select the params values
        st.sidebar.subheader("Параметры трансформации:" + transform_name)
        param_values = show_transform_control(augmentations[transform_name], i) #возвращает словарь param_values,
                                                                                #содержащий все параметры трансформации с их значениями
        transforms.append(getattr(A, transform_name)(**param_values))
        #добавляет в список выбранные трансформации с нужными параметрами
        #но уже из библиотеки A
    return transforms


def show_docstring(obj_with_ds):
    st.markdown("* * *")
    st.subheader("Строка документации трансформации " + obj_with_ds.__class__.__name__)
    st.text(obj_with_ds.__doc__)
