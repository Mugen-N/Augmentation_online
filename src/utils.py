import cv2
import os
import numpy as np
import json
import argparse
from io import BytesIO
import base64
import zipfile
import streamlit as st
from PIL import Image


@st.cache_data
def get_arguments():
    """Возвращает значения параметров CLI"""
    parser = argparse.ArgumentParser() #создает новый объект класса парсер
    parser.add_argument("--image_folder", default="images") #указываем какие аргументы ожидать
    parser.add_argument("--image_width", default=400, type=int)
    """На вход ожидаются 2 аргумента путь к папке с изображением и размер изображения"""
    args = parser.parse_args() #вызов парсера для получения переданных значений
    return getattr(args, "image_folder"), getattr(args, "image_width")#получение значения атрибутов


@st.cache_data
def get_images_list(path_to_folder: str) -> list: #получает строку возвращает список
    """Возвращает список изображений из папки
        Аргументы:
         path_to_folder (str): абсолютный или относительный путь к папке с изображениями
    """
    image_names_list = [
        x for x in os.listdir(path_to_folder) if x[-3:] in ["jpg", "peg", "png"]
    ]
    """os.listdir возвращает список файлов и каталогов в папке path_to_folder,
        последние 3 символа которых перечислены"""
    return image_names_list


@st.cache_data
def load_image(image_name: str, path_to_folder: str, bgr2rgb: bool = True):
    """Load the image
    Args:
        image_name (str): name of the image
        path_to_folder (str): path to the folder with image
        bgr2rgb (bool): converts BGR image to RGB if True
    """
    path_to_image = os.path.join(path_to_folder, image_name) #создание полного пути к файлу с изображением
    path_to_image = path_to_image.replace("\\", "/")
    image = cv2.imread(path_to_image) #возвращает массив NumPy, представляющий изображение
    if image is None:
        raise FileNotFoundError(f"Image not found: {path_to_image}") #убрать
    if bgr2rgb:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def upload_image(bgr2rgb: bool = True):
    """Uoload the image
    Args:
        bgr2rgb (bool): converts BGR image to RGB if True
    """
    file = st.sidebar.file_uploader(
        "Загрузите своё изображение (jpg, jpeg, png)", ["jpg", "jpeg", "png"]
    )
    image = cv2.imdecode(np.fromstring(file.read(), np.uint8), 1)
    if bgr2rgb:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

@st.cache_data
def load_augmentations_config(
    placeholder_params: dict, path_to_config: str = "configs/augmentations.json"
) -> dict:
    """Загрузка конфигурации json с параметрами всех преобразований
    Args:
        placeholder_params (dict): словарь со значениями параметров изображения
        path_to_config (str): путь к json файлу
    """
    with open(path_to_config, "r") as config_file: #открытие файла на чтение
        augmentations = json.load(config_file) #создаёт словарь augmentation на основе открытого js файла
    for name, params in augmentations.items(): #цикл по всем элементы словаря augmentation по именам и преобразованиям
        params = [fill_placeholders(param, placeholder_params) for param in params] #заменяет параметры на параметры изображения
    return augmentations


def fill_placeholders(params: dict, placeholder_params: dict) -> dict:
    """Fill the placeholder values in the config file
    Args:
        params (dict): original params dict with placeholders
        placeholder_params (dict): dict with values of placeholders
    """
    # TODO: refactor
    if "placeholder" in params:
        placeholder_dict = params["placeholder"] #проверяет наличие ключа "placeholder" в словаре params
        for k, v in placeholder_dict.items(): #Цикл по элементам словаря placeholder_dict где k - ключ, а v - значение
            if isinstance(v, list): #Проверяет, является ли значение v списком
                params[k] = [] #создается пустой список в словаре params для данного ключа k
                for element in v:
                    if element in placeholder_params:
                        params[k].append(placeholder_params[element])
                    else:
                        params[k].append(element)
            else:
                if v in placeholder_params:
                    params[k] = placeholder_params[v]
                else:
                    params[k] = v
        params.pop("placeholder")
    return params


def get_params_string(param_values: dict) -> str:
    """Generate the string from the dict with parameters
    Args:
        param_values (dict): dict of "param_name" -> "param_value"
    """
    params_string = ", ".join(
        [k + "=" + str(param_values[k]) for k in param_values.keys()]
    )
    return params_string


def get_placeholder_params(image):
    return {
        "image_width": image.shape[1],
        "image_height": image.shape[0],
        "image_half_width": int(image.shape[1] / 2),
        "image_half_height": int(image.shape[0] / 2),
    }


def select_transformations(augmentations: dict, interface_type: str) -> list:
    # в простом моде только 1 трансформация
    if interface_type == "Simple":
        transform_names = [
            st.sidebar.selectbox(
                "Выбор трансформации:", sorted(list(augmentations.keys()))
            )
        ]
    # в проффесианальном можно выбрать несколько
    elif interface_type == "Professional":
        transform_names = [
            st.sidebar.selectbox(
                "Выбор трансформации №1:", sorted(list(augmentations.keys()))
            )
        ]
        while transform_names[-1] != "None": # пока последний эл списка не NONE
            transform_names.append(
                st.sidebar.selectbox(
                    f"Выбор трансформации №{len(transform_names) + 1}:",
                    ["None"] + sorted(list(augmentations.keys())),
                )
            )
        transform_names = transform_names[:-1]# удаляет последний эл списка
    return transform_names


def create_zip_from_images(directory, images):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zipf:
        for image_name in images:
            image_path = os.path.join(directory, image_name)
            zipf.write(image_path, arcname=image_name)
    buffer.seek(0)
    return buffer

# Функция для создания папки пользователя
def create_user_folder(user_login, base_path):
    user_folder_path = os.path.join(base_path, user_login)

    if not os.path.exists(user_folder_path):
        os.makedirs(user_folder_path)

    return user_folder_path

# Функция для конвертации изображений в base64
def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode() # Кодируем данные изображения в base64 и декодируем результат в строку
    return img_str

# Функция для отображения изображений в DataFrame
def image_formatter(img_path):
    return f'<img src="data:image/png;base64,{img_path}" width="50" height="50">'

def image_saver(uploaded_files, new_folder_path):
    if uploaded_files is not None:
        data = {"Название": [], "Изображение": []}

        for uploaded_file in uploaded_files:
            # Сохранение загруженного изображения
            img = Image.open(uploaded_file)
            img_base64 = image_to_base64(img)
            img_path = os.path.join(new_folder_path, uploaded_file.name)
            img.save(img_path)

            # Добавление данных в словарь
            data["Название"].append(uploaded_file.name)
            data["Изображение"].append(img_base64)
    return data
