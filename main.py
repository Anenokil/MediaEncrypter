import sys
import os
from shutil import copyfile, rmtree
from time import perf_counter
from threading import Thread
from numpy import dstack, uint8, arange
from math import gcd  # НОД
from transliterate import translit  # Транслитерация
from skimage.io import imread, imsave
from PIL import Image  # Разбиение gif-изображений на кадры
import imageio.v2 as io  # Составление gif-изображений из кадров
from moviepy.editor import VideoFileClip  # Разбиение видео на кадры
import cv2  # Составление видео из кадров
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory
from colorama import Fore, Style  # Цвета в консоли
if sys.platform == 'win32':  # Для цветного текста в консоли Windows
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
import re  # Несколько разделителей в split
import urllib.request as urllib2  # Для проверки наличия обновлений
import wget  # Для загрузки обновления
import zipfile  # Для распаковки обновления

""" Информация о программе """

PROGRAM_NAME = 'Media encrypter'
PROGRAM_VERSION = 'v7.0.0_PRE-45'
PROGRAM_DATE = '3.2.2023 22:06 (UTC+3)'

""" Темы """

REQUIRED_THEME_VERSION = 1
THEMES = ['light', 'dark']  # Названия тем

# Все: bg
# Все, кроме frame: fg
# Все, кроме текста: border
# Frame: relief
# Кнопки: activebackground
# Entry: selectbackground, highlightcolor

ST_BG           = {THEMES[0]: '#EEEEEE', THEMES[1]: '#222222'}  # bg или background
ST_BG_RGB       = {THEMES[0]: '#EEEEEE', THEMES[1]: '#222222'}  # bg
ST_BG_FIELDS    = {THEMES[0]: '#FFFFFF', THEMES[1]: '#171717'}  # bg
ST_BG_ERR       = {THEMES[0]: '#EE6666', THEMES[1]: '#773333'}  # bg

ST_BORDER       = {THEMES[0]: '#222222', THEMES[1]: '#111111'}  # highlightbackground
ST_RELIEF       = {THEMES[0]: 'groove',  THEMES[1]: 'solid'  }  # relief

ST_SELECT       = {THEMES[0]: '#BBBBBB', THEMES[1]: '#444444'}  # selectbackground
ST_HIGHLIGHT    = {THEMES[0]: '#00DD00', THEMES[1]: '#007700'}  # highlightcolor

ST_BTN          = {THEMES[0]: '#D0D0D0', THEMES[1]: '#202020'}  # bg
ST_BTN_SELECT   = {THEMES[0]: '#BABABA', THEMES[1]: '#272727'}  # activebackground
ST_MCM          = {THEMES[0]: '#B0B0B0', THEMES[1]: '#0E0E0E'}  # bg
ST_MCM_SELECT   = {THEMES[0]: '#9A9A9A', THEMES[1]: '#151515'}  # activebackground
ST_BTN_Y        = {THEMES[0]: '#88DD88', THEMES[1]: '#446F44'}  # bg
ST_BTN_Y_SELECT = {THEMES[0]: '#77CC77', THEMES[1]: '#558055'}  # activebackground
ST_BTN_N        = {THEMES[0]: '#FF6666', THEMES[1]: '#803333'}  # bg
ST_BTN_N_SELECT = {THEMES[0]: '#EE5555', THEMES[1]: '#904444'}  # activebackground

ST_FG           = {THEMES[0]: '#222222', THEMES[1]: '#979797'}  # fg или foreground
ST_FG_LOGO      = {THEMES[0]: '#FF7200', THEMES[1]: '#803600'}  # fg
ST_FG_FOOTER    = {THEMES[0]: '#666666', THEMES[1]: '#666666'}  # fg
ST_FG_EXAMPLE   = {THEMES[0]: '#448899', THEMES[1]: '#448899'}  # fg
ST_FG_KEY       = {THEMES[0]: '#EE0000', THEMES[1]: '#BC4040'}  # fg

ST_PROG         = {THEMES[0]: '#06B025', THEMES[1]: '#06B025'}  # bg
ST_PROG_ABORT   = {THEMES[0]: '#FFB050', THEMES[1]: '#FFB040'}  # bg
ST_PROG_DONE    = {THEMES[0]: '#0077FF', THEMES[1]: '#1133DD'}  # bg

# Названия стилизуемых элементов
STYLE_ELEMENTS = ['BG', 'BG_RGB', 'BG_FIELDS', 'BG_ERR', 'BORDER', 'RELIEF', 'SELECT', 'HIGHLIGHT',
                  'BTN', 'BTN_SELECT', 'MCM', 'MCM_SELECT', 'BTNY', 'BTNY_SELECT', 'BTNN', 'BTNN_SELECT',
                  'FG_TEXT', 'FG_LOGO', 'FG_FOOTER', 'FG_EXAMPLE', 'FG_KEY', 'ST_PROG', 'ST_PROG_ABORT', 'ST_PROG_DONE']

# Стили для каждого элемента
STYLES = {STYLE_ELEMENTS[0]:  ST_BG,
          STYLE_ELEMENTS[1]:  ST_BG_RGB,
          STYLE_ELEMENTS[2]:  ST_BG_FIELDS,
          STYLE_ELEMENTS[3]:  ST_BG_ERR,
          STYLE_ELEMENTS[4]:  ST_BORDER,
          STYLE_ELEMENTS[5]:  ST_RELIEF,
          STYLE_ELEMENTS[6]:  ST_SELECT,
          STYLE_ELEMENTS[7]:  ST_HIGHLIGHT,
          STYLE_ELEMENTS[8]:  ST_BTN,
          STYLE_ELEMENTS[9]:  ST_BTN_SELECT,
          STYLE_ELEMENTS[10]: ST_MCM,
          STYLE_ELEMENTS[11]: ST_MCM_SELECT,
          STYLE_ELEMENTS[12]: ST_BTN_Y,
          STYLE_ELEMENTS[13]: ST_BTN_Y_SELECT,
          STYLE_ELEMENTS[14]: ST_BTN_N,
          STYLE_ELEMENTS[15]: ST_BTN_N_SELECT,
          STYLE_ELEMENTS[16]: ST_FG,
          STYLE_ELEMENTS[17]: ST_FG_LOGO,
          STYLE_ELEMENTS[18]: ST_FG_FOOTER,
          STYLE_ELEMENTS[19]: ST_FG_EXAMPLE,
          STYLE_ELEMENTS[20]: ST_FG_KEY,
          STYLE_ELEMENTS[21]: ST_PROG,
          STYLE_ELEMENTS[22]: ST_PROG_ABORT,
          STYLE_ELEMENTS[23]: ST_PROG_DONE}

""" Пути, файлы, ссылки """

MAIN_PATH = os.path.dirname(__file__)  # Папка с программой
RESOURCES_DIR = 'resources'  # Главная папка с ресурсами
CUSTOM_SETTINGS_DIR = 'custom_settings'  # Папка с сохранёнными пользовательскими настройками
CUSTOM_SETTINGS_PATH = os.path.join(RESOURCES_DIR, CUSTOM_SETTINGS_DIR)
SETTINGS_FILENAME = 'settings.txt'  # Файл с настройками
SETTINGS_PATH = os.path.join(RESOURCES_DIR, SETTINGS_FILENAME)
TMP_FILENAME = 'tmp.png'  # Временный файл для обработки gif-изображений и видео
TMP_PATH = os.path.join(RESOURCES_DIR, TMP_FILENAME)
IMAGES_DIR = 'img'  # Папка с изображениями
IMAGES_PATH = os.path.join(RESOURCES_DIR, IMAGES_DIR)
CUSTOM_THEMES_DIR = 'themes'  # Папка с пользовательскими темами
CUSTOM_THEMES_PATH = os.path.join(RESOURCES_DIR, CUSTOM_THEMES_DIR)

# Если нет папки с ресурсами
if RESOURCES_DIR not in os.listdir(os.curdir):
    os.mkdir(RESOURCES_DIR)
if CUSTOM_SETTINGS_DIR not in os.listdir(RESOURCES_DIR):
    os.mkdir(CUSTOM_SETTINGS_PATH)
if CUSTOM_THEMES_DIR not in os.listdir(RESOURCES_DIR):
    os.mkdir(CUSTOM_THEMES_PATH)

# Затирание временного файла при запуске программы, если он остался с прошлого сеанса
if TMP_FILENAME in os.listdir(RESOURCES_DIR):
    open(TMP_PATH, 'w')
    os.remove(TMP_PATH)

# Название репозитория на GitHub
REPOSITORY_NAME = 'MediaEncrypter'

# Ссылка на репозиторий программы на GitHub
URL_GITHUB = f'https://github.com/Anenokil/{REPOSITORY_NAME}'
# Ссылка на файл с названием последней версии
URL_LAST_VERSION = f'https://raw.githubusercontent.com/Anenokil/{REPOSITORY_NAME}/master/ver'
# Ссылка для установки последней версии
URL_DOWNLOAD_ZIP = f'https://github.com/Anenokil/{REPOSITORY_NAME}/archive/refs/heads/master.zip'

NEW_VERSION_DIR = f'{REPOSITORY_NAME}-master'  # Временная папка с обновлением
NEW_VERSION_ZIP = f'{NEW_VERSION_DIR}.zip'  # Архив с обновлением

# Допустимые в названии файлов символы (Windows)
FN_SYMBOLS_WITHOUT_RU = '#\' 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@$%^&()[]{}-=_+`~;,.'
FN_SYMBOLS_WITH_RU = FN_SYMBOLS_WITHOUT_RU + 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
FN_SYMBOLS_WITHOUT_RU_NUM = len(FN_SYMBOLS_WITHOUT_RU)
FN_SYMBOLS_WITH_RU_NUM = len(FN_SYMBOLS_WITH_RU)

""" Настройки """

settings = {}
INT_SETTINGS_NUM = 2  # Количество числовых настроек
SETTINGS_NUM = 15  # Количество всех настроек

# Названия настроек
SETTINGS_NAMES = ['count_from', 'format', 'show_updates', 'support_ru', 'processing_ru',
                  'naming_mode', 'print_info', 'theme',
                  'marker_enc', 'marker_dec', 'src_dir_enc', 'dst_dir_enc',
                  'src_dir_dec', 'dst_dir_dec', 'example_key']

# Варианты значений настроек с перечислимым типом
SHOW_UPDATES_MODES = ['yes', 'no']  # Варианты поддержки кириллических букв
SUPPORT_RU_MODES = ['yes', 'no']  # Варианты поддержки кириллических букв
PROCESSING_RU_MODES = ['don`t change', 'transliterate to latin']  # Варианты обработки кириллических букв
NAMING_MODES = ['don`t change', 'encryption', 'numbering', 'add prefix', 'add postfix']  # Варианты именования выходных файлов
PRINT_INFO_MODES = ['don`t print', 'print']  # Варианты печати информации
THEME_MODES = THEMES  # Варианты тем

# Значения настроек по умолчанию
DEFAULT_SETTINGS = {'count_from': 1,
                    'format': 1,
                    'show_updates': 'yes',
                    'support_ru': 'no',
                    'processing_ru': 'transliterate to latin',
                    'naming_mode': 'encryption',
                    'print_info': 'don`t print',
                    'theme': 'light',
                    'marker_enc': '_ENC_',
                    'marker_dec': '_DEC_',
                    'src_dir_enc': 'f_src',
                    'dst_dir_enc': 'f_enc',
                    'src_dir_dec': 'f_enc',
                    'dst_dir_dec': 'f_dec',
                    'example_key': '_123456789_123456789_123456789_123456789'}

""" Ключ """

KEY_SYMBOLS = '0123456789-abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ'  # Допустимые в ключе символы
KEY_LEN = 40  # Длина ключа

""" Общие функции """


# Перевод 'yes'/'no' в bool
def str_to_bool(line: str):
    return line == 'yes'


# Перевод bool в 'yes'/'no'
def bool_to_str(boolean: bool):
    if boolean:
        return 'yes'
    else:
        return 'no'


# Печать с отступом
def print_tab(msg='', tab=0, end='\n'):
    print('~ ' * tab + str(msg), end=end)


# Добавить запись в журнал обработки
def add_log(msg='', tab=0, end='\n'):
    try:
        gui.logger.add_log(msg, tab, end)
    except:
        global process_status
        process_status = 'error'


# Обновить прогресс обработки (файлы и папки)
def set_progress_f_d(num: int, den: int):
    try:
        gui.logger.set_progress_f_d(num, den)
    except:
        global process_status
        process_status = 'error'


# Обновить прогресс обработки (кадры)
def set_progress_fr(num: int, den: int):
    try:
        gui.logger.set_progress_fr(num, den)
    except:
        global process_status
        process_status = 'error'


# Вывод предупреждения в консоль и в журнал
def print_warn(msg: str):
    print(f'{Fore.RED}[!!!] {msg} [!!!]{Style.RESET_ALL}')
    add_log(f'[!!!] {msg} [!!!]')


# Является ли строка целым числом
def is_num(line: str):
    return line.isnumeric() or (len(line) > 1 and line[0] == '-' and line[1:].isnumeric())


# Проверка ключа на корректность
def check_key(key: str):
    length = len(key)
    if length != KEY_LEN:  # Если ключ имеет неверную длину
        return 'L', length
    for i in range(length):
        pos = KEY_SYMBOLS.find(key[i])
        if pos == -1:  # Если ключ содержит недопустимые символы
            return 'S', key[i]
    return '+', None


# Установка значений по умолчанию для всех настроек
def set_default_settings():
    for name in SETTINGS_NAMES:
        settings[name] = DEFAULT_SETTINGS[name]


# Проверка и исправление настроек
def correct_settings():
    if not is_num(settings['count_from']):
        settings['count_from'] = DEFAULT_SETTINGS['count_from']
    if not settings['format'].isnumeric():
        settings['format'] = DEFAULT_SETTINGS['format']
    if settings['show_updates'] not in SHOW_UPDATES_MODES:
        settings['show_updates'] = DEFAULT_SETTINGS['show_updates']
    if settings['support_ru'] not in SUPPORT_RU_MODES:
        settings['support_ru'] = DEFAULT_SETTINGS['support_ru']
    if settings['processing_ru'] not in PROCESSING_RU_MODES:
        settings['processing_ru'] = DEFAULT_SETTINGS['processing_ru']
    if settings['print_info'] not in PRINT_INFO_MODES:
        settings['print_info'] = DEFAULT_SETTINGS['print_info']
    if settings['naming_mode'] not in NAMING_MODES:
        settings['naming_mode'] = DEFAULT_SETTINGS['naming_mode']
    if settings['theme'] not in THEME_MODES:
        settings['theme'] = DEFAULT_SETTINGS['theme']
    if check_key(settings['example_key'])[0] != '+':
        settings['example_key'] = DEFAULT_SETTINGS['example_key']

    if settings['support_ru'] == DEFAULT_SETTINGS['support_ru']:
        settings['processing_ru'] = DEFAULT_SETTINGS['processing_ru']


# Загрузка настроек из файла
def load_settings(filename: str):
    with open(filename, 'r') as file:
        for i in range(SETTINGS_NUM):
            settings[SETTINGS_NAMES[i]] = file.readline().strip()
        correct_settings()
        for i in range(INT_SETTINGS_NUM):
            settings[SETTINGS_NAMES[i]] = int(settings[SETTINGS_NAMES[i]])


# Сохранить настройки в файл
def save_settings_to_file(filename=SETTINGS_PATH):
    with open(filename, 'w') as file:
        for name in SETTINGS_NAMES:
            file.write(f'{settings[name]}\n')


# Преобразование ключа в массив битов (каждый символ - в 6 битов)
def key_to_bites(key: str):
    bits = [[0] * KEY_LEN for _ in range(6)]
    for i in range(KEY_LEN):
        symbol = KEY_SYMBOLS.find(key[i])
        for j in range(6):
            bits[j][i] = symbol // (2 ** j) % 2
    return bits


# Нахождение числа по его битам
def bites_sum(*bites: int | list[int]):
    res = 0
    for i in bites:
        if type(i) == list:
            for j in i:
                res = 2 * res + j
        else:
            res = 2 * res + i
    return res


# Извлечение ключевых значений
def extract_key_values(b: list[list[int]]):
    global mult_blocks_h_r, mult_blocks_h_g, mult_blocks_h_b, mult_blocks_w_r, mult_blocks_w_g, mult_blocks_w_b,\
        shift_h_r, shift_h_g, shift_h_b, shift_w_r, shift_w_g, shift_w_b, shift_r, shift_g, shift_b, mult_r,\
        mult_g, mult_b, shift2_r, shift2_g, shift2_b, order, mult_name

    mult_blocks_h_r = bites_sum(b[0][16:20], b[1][20:24], b[2][12:16]) + 47  # Множитель блоков по горизонтали для красного канала
    mult_blocks_h_g = bites_sum(b[0][4:8],   b[1][8:12],  b[2][0:4])   + 47  # Множитель блоков по горизонтали для зелёного канала
    mult_blocks_h_b = bites_sum(b[0][28:32], b[1][32:36], b[2][24:28]) + 47  # Множитель блоков по горизонтали для синего канала
    mult_blocks_w_r = bites_sum(b[3][34:38], b[4][2:4],   b[4][38:40], b[5][30:34]) + 47  # Множитель блоков по вертикали для красного канала
    mult_blocks_w_g = bites_sum(b[3][22:26], b[4][26:30], b[5][18:22]) + 47  # Множитель блоков по вертикали для зелёного канала
    mult_blocks_w_b = bites_sum(b[3][10:14], b[4][14:18], b[5][6:10])  + 47  # Множитель блоков по вертикали для синего канала
    shift_h_r = bites_sum(b[0][0:4], b[1][4:8], b[2][8:12]) + 228  # Сдвиг блоков по вертикали для красного канала
    shift_h_g = bites_sum(b[0][12:16], b[1][16:20], b[2][20:24]) + 228  # Сдвиг блоков по вертикали для зелёного канала
    shift_h_b = bites_sum(b[0][24:28], b[1][28:32], b[2][32:36]) + 228  # Сдвиг блоков по вертикали для синего канала
    shift_w_r = bites_sum(b[3][18:22], b[4][22:26], b[5][26:30]) + 228  # Сдвиг блоков по горизонтали для красного канала
    shift_w_g = bites_sum(b[3][30:34], b[4][34:38], b[5][0:2], b[5][38:40]) + 228  # Сдвиг блоков по горизонтали для зелёного канала
    shift_w_b = bites_sum(b[3][6:10],  b[4][10:14], b[5][14:18]) + 228  # Сдвиг блоков по горизонтали для синего канала
    shift_r = bites_sum(b[2][16:20], b[2][28:32])  # Первичное смещение цвета для красного канала
    shift_g = bites_sum(b[0][32:36], b[1][14:16], b[2][6:8])  # Первичное смещение цвета для зелёного канала
    shift_b = bites_sum(b[0][20:22], b[1][0:4],   b[2][4:6])  # Первичное смещение цвета для синего канала
    mult_r = bites_sum(b[0][22:24], b[0][36:38], b[1][12:14], b[3][14:16], b[3][28:30], b[4][0], 0)  + 21  # Цветовой множитель для красного канала
    mult_g = bites_sum(b[0][8:10],  b[1][24:26], b[2][38:40], b[3][2:4],   b[3][16:18], b[4][30], 0) + 21  # Цветовой множитель для зелёного канала
    mult_b = bites_sum(b[0][10:12], b[1][26:28], b[1][36:38], b[4][18:20], b[4][32:34], b[5][4], 0)  + 21  # Цветовой множитель для синего канала
    shift2_r = bites_sum(b[4][6:10],  b[4][20:22], b[5][34:36])  # Вторичное смещение цвета для красного канала
    shift2_g = bites_sum(b[3][26:28], b[5][10:14], b[5][24:25])  # Вторичное смещение цвета для зелёного канала
    shift2_b = bites_sum(b[3][4:6],   b[3][38:40], b[5][22:24], b[5][36:38])  # Вторичное смещение цвета для синего канала
    order = bites_sum(b[0][38], b[2][37], b[5][2]) % 6  # Порядок следования каналов после перемешивания
    mult_name = bites_sum(b[0][39], b[1][38:40], b[2][36], b[3][0:2], b[4][4:6], b[5][3]) % (fn_symbols_num - 1) + 1  # Сдвиг букв в имени файла

    if settings['print_info'] == 'print':  # Вывод ключевых значений
        print('                                    KEY  CONSTANTS')
        print(f'  ML BH: {mult_blocks_h_r}, {mult_blocks_h_g}, {mult_blocks_h_b}')
        print(f'  ML BW: {mult_blocks_w_r}, {mult_blocks_w_g}, {mult_blocks_w_b}')
        print(f'  SH  H: {shift_h_r}, {shift_h_g}, {shift_h_b}')
        print(f'  SH  W: {shift_w_r}, {shift_w_g}, {shift_w_b}')
        print(f'  SH1 C: {shift_r}, {shift_g}, {shift_b}')
        print(f'  ML  C: {mult_r}, {mult_g}, {mult_b}')
        print(f'  SH2 C: {shift2_r}, {shift2_g}, {shift2_b}')
        print(f'  ML  N: {mult_name}')
        print(f'  ORDER: {order}')
        print('======================================================================================')


# Проверка наличия обновлений программы
def check_updates(window_parent, show_updates: bool):
    print('\nПроверка наличия обновлений...')
    window_last_version = None
    try:
        data = urllib2.urlopen(URL_LAST_VERSION)
        last_version = str(data.read().decode('utf-8')).strip()
        if PROGRAM_VERSION == last_version:
            print('Установлена последняя доступная версия')
        else:
            print(f'Доступна новая версия: {last_version}')
            if show_updates:
                window_last_version = LastVersionW(window_parent, last_version)
    except:
        print('Ошибка, возможно отсутствует соединение')
    return window_last_version


# Загрузка пользовательских тем
def upload_themes(themes: list[str]):
    if os.listdir(CUSTOM_THEMES_PATH):
        print('\nЗагрузка тем...')
    for file_name in os.listdir(CUSTOM_THEMES_PATH):
        base_name, ext = os.path.splitext(file_name)
        theme = base_name
        file_path = os.path.join(CUSTOM_THEMES_PATH, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as theme_file:
                line = theme_file.readline().strip()
                theme_version = int(re.split(' |//', line)[0])  # После // идут комментарии
                if theme_version != REQUIRED_THEME_VERSION:  # Проверка версии темы
                    print(f'Не удалось загрузить тему "{theme}", т. к. она устарела!')
                    continue
                themes += [theme]  # Добавляем название новой темы
                for style_elem in STYLE_ELEMENTS:  # Проходимся по стилизуемым элементам
                    line = theme_file.readline().strip()
                    style = re.split(' |//', line)[0]  # После // идут комментарии
                    element = STYLES[style_elem]
                    element[theme] = style  # Добавляем новый стиль для элемента, соответствующий теме theme
        except:
            print(f'Не удалось загрузить тему "{theme}" из-за ошибки!')
        else:
            print(f'Тема "{theme}" успешно загружена')


""" Алгоритм шифровки/дешифровки """


# Разделение полотна на блоки и их перемешивание
def mix_blocks(img, mult_h: int, mult_w: int, shift_h: int, shift_w: int, depth: int):
    h = img.shape[0]  # Высота изображения
    w = img.shape[1]  # Ширина изображения

    # Нахождение наименьшего числа, взаимно-простого с h, большего чем mult_h, дающего при делении на h в остатке 1
    while gcd(mult_h, h) != 1 or mult_h % h == 1:
        mult_h += 1
    # Нахождение наименьшего числа, взаимно-простого с w, большего чем mult_w, дающего при делении на w в остатке 1
    while gcd(mult_w, w) != 1 or mult_w % w == 1:
        mult_w += 1

    if settings['print_info'] == 'print':
        print_tab(f'{h}x{w}: {mult_h} {mult_w}', depth)
        add_log(f'{h}x{w}: {mult_h} {mult_w}', depth)

    img_tmp = img.copy()
    for i in range(h):
        for j in range(w):
            jj = (j + shift_w * i) % w
            ii = (i + shift_h * jj) % h
            iii = (ii * mult_h) % h
            jjj = (jj * mult_w) % w
            img[iii][jjj] = img_tmp[i][j]


# Шифровка файла
def encode_file(img, depth: int):
    # Разделение изображения на RGB-каналы
    if len(img.shape) < 3:  # Если в изображении меньше трёх каналов
        red, green, blue = img.copy(), img.copy(), img.copy()
    else:
        red, green, blue = [img[:, :, i].copy() for i in range(3)]

    # Перемешивание блоков для каждого канала
    mix_blocks(red,   mult_blocks_h_r, mult_blocks_w_r, shift_h_r, shift_w_r, depth)
    mix_blocks(green, mult_blocks_h_g, mult_blocks_w_g, shift_h_g, shift_w_g, depth)
    mix_blocks(blue,  mult_blocks_h_b, mult_blocks_w_b, shift_h_b, shift_w_b, depth)

    # Начальное смещение цвета для каждого канала
    red = (red + shift_r) % 256
    green = (green + shift_g) % 256
    blue = (blue + shift_b) % 256

    # Мультипликативное смещение цвета для каждого канала
    red = (red * mult_r) % 256
    green = (green * mult_g) % 256
    blue = (blue * mult_b) % 256

    # Конечное смещение цвета для каждого канала
    red = (red + shift2_r) % 256
    green = (green + shift2_g) % 256
    blue = (blue + shift2_b) % 256

    # Перемешивание и объединение каналов
    if len(img.shape) < 3:  # Если в изображении меньше трёх каналов
        img = red
    else:
        if order == 0:
            img = dstack((red, green, blue))
        elif order == 1:
            img = dstack((red, blue, green))
        elif order == 2:
            img = dstack((green, red, blue))
        elif order == 3:
            img = dstack((green, blue, red))
        elif order == 4:
            img = dstack((blue, red, green))
        else:
            img = dstack((blue, green, red))

    return img


# Вычисление параметров для recover_blocks
def recover_blocks_calc(h: int, w: int, mult_h: int, mult_w: int, depth: int):
    # Нахождение наименьшего числа, взаимно-простого с h, большего чем mult_h, дающего при делении на h в остатке 1
    while gcd(mult_h, h) != 1 or mult_h % h == 1:
        mult_h += 1
    # Нахождение наименьшего числа, взаимно-простого с w, большего чем mult_w, дающего при делении на w в остатке 1
    while gcd(mult_w, w) != 1 or mult_w % w == 1:
        mult_w += 1

    if settings['print_info'] == 'print':
        print_tab(f'{h}x{w}: {mult_h} {mult_w}', depth)
        add_log(f'{h}x{w}: {mult_h} {mult_w}', depth)

    dec_h = [0] * h  # Составление массива обратных сдвигов по вертикали
    for i in range(h):
        dec_h[(i * mult_h) % h] = i
    dec_w = [0] * w  # Составление массива обратных сдвигов по горизонтали
    for i in range(w):
        dec_w[(i * mult_w) % w] = i

    return dec_h, dec_w


# Разделение полотна на блоки и восстановление из них исходного изображения
def recover_blocks(img, h: int, w: int, shift_h: int, shift_w: int, dec_h: list[int], dec_w: list[int]):
    img_tmp = img.copy()
    for i in range(h):
        for j in range(w):
            ii = dec_h[i]
            jj = dec_w[j]
            iii = (ii + (h - shift_h) * jj) % h
            jjj = (jj + (w - shift_w) * iii) % w
            img[iii][jjj] = img_tmp[i][j]


# Вычисление параметров для decode_file
def decode_file_calc(img, depth: int):
    h = img.shape[0]  # Высота изображения
    w = img.shape[1]  # Ширина изображения

    dec_h_r, dec_w_r = recover_blocks_calc(h, w, mult_blocks_h_r, mult_blocks_w_r, depth)  # Массивы обратных сдвигов для красного канала
    dec_h_g, dec_w_g = recover_blocks_calc(h, w, mult_blocks_h_g, mult_blocks_w_g, depth)  # Массивы обратных сдвигов для зелёного канала
    dec_h_b, dec_w_b = recover_blocks_calc(h, w, mult_blocks_h_b, mult_blocks_w_b, depth)  # Массивы обратных сдвигов для синего канала

    return h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b


# Дешифровка файла
def decode_file(img, h: int, w: int, dec_h_r: list[int], dec_w_r: list[int], dec_h_g: list[int], dec_w_g: list[int],
                dec_h_b: list[int], dec_w_b: list[int]):
    # Разделение изображения на RGB-каналы и отмена их перемешивания
    if len(img.shape) < 3:  # Если в изображении меньше трёх каналов
        red, green, blue = img.copy(), img.copy(), img.copy()
    else:
        if order == 0:
            red, green, blue = [img[:, :, i].copy() for i in range(3)]
        elif order == 1:
            red, blue, green = [img[:, :, i].copy() for i in range(3)]
        elif order == 2:
            green, red, blue = [img[:, :, i].copy() for i in range(3)]
        elif order == 3:
            green, blue, red = [img[:, :, i].copy() for i in range(3)]
        elif order == 4:
            blue, red, green = [img[:, :, i].copy() for i in range(3)]
        else:
            blue, green, red = [img[:, :, i].copy() for i in range(3)]

    # Отмена конечного смещения цвета для каждого канала
    red = (red - shift2_r) % 256
    green = (green - shift2_g) % 256
    blue = (blue - shift2_b) % 256

    # Отмена мультипликативного смещения цвета для каждого канала
    for i in range(h):
        for j in range(w):
            red[i][j] = DEC_R[red[i][j]]
            green[i][j] = DEC_G[green[i][j]]
            blue[i][j] = DEC_B[blue[i][j]]

    # Отмена начального смещения цвета для каждого канала
    red = (red - shift_r) % 256
    green = (green - shift_g) % 256
    blue = (blue - shift_b) % 256

    # Отмена перемешивания блоков для каждого канала
    recover_blocks(red,   h, w, shift_h_r, shift_w_r, dec_h_r, dec_w_r)
    recover_blocks(green, h, w, shift_h_g, shift_w_g, dec_h_g, dec_w_g)
    recover_blocks(blue,  h, w, shift_h_b, shift_w_b, dec_h_b, dec_w_b)

    # Объединение каналов
    if len(img.shape) < 3:  # Если в изображении меньше трёх каналов
        img = red
    else:
        img = dstack((red, green, blue))

    return img


# Шифровка имени файла
def encode_filename(name: str):
    if settings['processing_ru'] == 'transliterate to latin':  # Транслитерация кириллицы
        name = translit(name, language_code='ru', reversed=True)

    # Нахождение наименьшего числа, взаимно-простого с fn_symbols_num, большего чем mult_name + len(name)
    mn = mult_name + len(name)
    while gcd(mn, fn_symbols_num) != 1:
        mn += 1

    new_name = ''
    for letter in name:  # Шифровка
        letter = fn_symbols[(fn_symbols.find(letter) + 3) * mn % fn_symbols_num]
        new_name = letter + new_name
    new_name = f'_{new_name}_'  # Защита от потери крайних пробелов
    return new_name


# Дешифровка имени файла
def decode_filename(name: str):
    name = name[1:-1]  # Защита от потери крайних пробелов

    # Нахождение наименьшего числа, взаимно-простого с fn_symbols_num, большего чем mult_name + len(name)
    mn = mult_name + len(name)
    while gcd(mn, fn_symbols_num) != 1:
        mn += 1

    arr = [0] * fn_symbols_num  # Дешифровочный массив
    for i in range(fn_symbols_num):
        arr[(i + 3) * mn % fn_symbols_num] = i

    new_name = ''
    for letter in name:  # Дешифровка
        letter = fn_symbols[arr[fn_symbols.find(letter)]]
        new_name = letter + new_name

    if settings['processing_ru'] == 'transliterate to latin':  # Транслитерация кириллицы
        new_name = translit(new_name, language_code='ru', reversed=True)

    return new_name


# Преобразование имени файла
def filename_processing(op_mode: str, naming_mode: str, base_name: str, ext: str, output_dir: str, marker: str,
                        count_correct: int):
    if op_mode == 'E':  # При шифровке
        count_same = 1  # Счётчик файлов с таким же именем
        counter = ''
        while True:
            if naming_mode == 'encryption':
                new_name = encode_filename(base_name + counter)
            elif naming_mode == 'numbering':
                new_name = ('{:0' + str(settings['format']) + '}').format(count_correct) + counter
            elif naming_mode == 'add prefix':
                new_name = marker + base_name + counter
            elif naming_mode == 'add postfix':
                new_name = base_name + marker + counter
            else:
                new_name = base_name + counter
            new_name += ext

            if new_name not in os.listdir(output_dir):  # Если нет файлов с таким же именем, то завершаем цикл
                break
            count_same += 1
            counter = f' [{count_same}]'  # Если уже есть файл с таким именем, то добавляется индекс
    else:  # При дешифровке
        if naming_mode == 'encryption':
            new_name = decode_filename(base_name)
        elif naming_mode == 'numbering':
            new_name = ('{:0' + str(settings['format']) + '}').format(count_correct)
        elif naming_mode == 'add prefix':
            new_name = marker + base_name
        elif naming_mode == 'add postfix':
            new_name = base_name + marker
        else:
            new_name = base_name

        count_same = 1  # Счётчик файлов с таким же именем
        temp_name = new_name + ext
        while temp_name in os.listdir(output_dir):  # Если уже есть файл с таким именем, то добавляется индекс
            count_same += 1
            temp_name = f'{new_name} [{count_same}]{ext}'
        new_name = temp_name
    return new_name


# Подсчёт всех файлов и папок, всех кадров
def count_all(op_mode: str, var_dir: str, count_f_d: int, count_fr: int):
    for filename in os.listdir(var_dir):  # Проход по файлам
        _, ext = os.path.splitext(filename)
        pth = os.path.join(var_dir, filename)
        isdir = os.path.isdir(pth)

        try:
            count_f_d += 1
            if ext == '.gif':
                im = Image.open(pth)
                count_fr += im.n_frames
            elif isdir and '_gif' in os.listdir(pth) and op_mode == 'D':
                count_fr += len([name for name in os.listdir(pth) if name.endswith('.png')])
            elif ext in ['.avi', '.mp4', '.webm', '.mov']:
                vid = VideoFileClip(pth)
                fps = min(vid.fps, 24)
                step = 1 / fps
                count_fr += int(vid.duration // step + 1)
            elif isdir and '_vid' in os.listdir(pth) and op_mode == 'D':
                count_fr += len([name for name in os.listdir(pth) if name.endswith('.png')])
            elif isdir:
                count_fr += 1
                count_f_d, count_fr = count_all(op_mode, pth, count_f_d, count_fr)
            else:
                count_fr += 1
        except Exception as err:
            print_warn('Couldn`t process the file')
            print(f'{Fore.YELLOW}{err}{Style.RESET_ALL}\n')
            add_log(f'{err}\n')

        if process_status != 'work':
            break
    if process_status == 'abort':
        print(' >> Aborted <<\n')
        add_log(' >> Aborted <<\n')
    elif process_status == 'error':
        print(' >> Emergency stop <<\n')
        add_log(' >> Emergency stop <<\n')
    return count_f_d, count_fr


# Обработка папки с файлами
def converse_dir(op_mode: str, marker: str, formats: list[str], var_dir: str, output_dir: str, count_all_files: int,
                 count_all_frames: int, depth: int):
    count_correct = settings['count_from'] - 1  # Счётчик количества обработанных файлов
    for filename in os.listdir(var_dir):  # Проход по файлам
        base_name, ext = os.path.splitext(filename)
        count_all_files += 1

        pth = os.path.join(var_dir, filename)
        isdir = os.path.isdir(pth)
        if ext.lower() not in formats and not isdir:  # Проверка формата
            print_tab(f'({count_all_files}) <{filename}>', depth)
            add_log(f'({count_all_files}) <{filename}>', depth)
            print_warn('Unsupported file extension')
            print()
            add_log()
            count_all_frames += 1
            set_progress_fr(count_all_frames, count_all_fr)
            set_progress_f_d(count_all_files, count_all_f_d)
            continue
        count_correct += 1

        start = perf_counter()
        try:
            if ext in ['.png', '.jpg', '.jpeg', '.jfif', '.bmp']:
                res_name = filename_processing(op_mode, settings['naming_mode'], base_name, '.png', output_dir, marker, count_correct)  # Преобразование имени файла

                print_tab(f'({count_all_files}) <{filename}>  ->  <{res_name}>', depth)  # Вывод информации
                add_log(f'({count_all_files}) <{filename}>  ->  <{res_name}>', depth)

                img = imread(pth)  # Считывание изображения
                if settings['print_info'] == 'print':
                    print_tab(img.shape, depth)
                    add_log(img.shape, depth)

                outp_path = os.path.join(output_dir, res_name)
                if op_mode == 'E':  # Запись результата
                    imsave(outp_path, encode_file(img, depth).astype(uint8))
                else:
                    h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b = decode_file_calc(img, depth)
                    img = decode_file(img, h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b)
                    imsave(outp_path, img.astype(uint8))
                print()
                add_log()

                count_all_frames += 1
                set_progress_fr(count_all_frames, count_all_fr)
            elif ext == '.gif':
                res_name = filename_processing(op_mode, settings['naming_mode'], base_name, '', output_dir, marker, count_correct)  # Преобразование имени файла

                print_tab(f'({count_all_files}) <{filename}>  ->  <{res_name}>', depth)  # Вывод информации
                add_log(f'({count_all_files}) <{filename}>  ->  <{res_name}>', depth)

                res = os.path.join(output_dir, res_name)
                if res_name not in os.listdir(output_dir):
                    os.mkdir(res)
                open(os.path.join(res, '_gif'), 'w')

                with Image.open(pth) as im:
                    for i in range(im.n_frames):
                        print_tab(f'frame {i + 1}/{im.n_frames}', depth)
                        add_log(f'frame {i + 1}/{im.n_frames}', depth)

                        im.seek(i)
                        im.save(TMP_PATH)
                        fr = imread(TMP_PATH)
                        if settings['print_info'] == 'print':  # Вывод информации о считывании
                            print_tab(fr.shape, depth)
                            add_log(fr.shape, depth)
                        outp_path = os.path.join(res, '{:05}.png'.format(i))
                        imsave(outp_path, encode_file(fr, depth).astype(uint8))
                        print()
                        add_log()

                        count_all_frames += 1
                        set_progress_fr(count_all_frames, count_all_fr)

                        if process_status != 'work':
                            break
                    imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
                    os.remove(TMP_PATH)
            elif isdir and '_gif' in os.listdir(pth) and op_mode == 'D':
                res_name = filename_processing(op_mode, settings['naming_mode'], filename, '.gif', output_dir, marker, count_correct)  # Преобразование имени файла

                print_tab(f'({count_all_files}) <{filename}>  ->  <{res_name}>', depth)  # Вывод информации
                add_log(f'({count_all_files}) <{filename}>  ->  <{res_name}>', depth)

                var_dir_tmp = pth
                frames = sorted([name for name in os.listdir(var_dir_tmp) if name.endswith('.png')])
                res = os.path.join(output_dir, res_name)

                img = imread(os.path.join(var_dir_tmp, frames[0]))
                h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b = decode_file_calc(img, depth)

                count_frames = len(frames)
                with io.get_writer(res, mode='I', duration=1/24) as writer:
                    for i in range(count_frames):
                        print_tab(f'frame {i + 1}/{count_frames}', depth)
                        add_log(f'frame {i + 1}/{count_frames}', depth)

                        fr = imread(os.path.join(var_dir_tmp, frames[i]))
                        if settings['print_info'] == 'print':  # Вывод информации о считывании
                            print_tab(fr.shape, depth)
                            add_log(fr.shape, depth)
                        img = decode_file(fr, h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b)
                        imsave(TMP_PATH, img.astype(uint8))
                        writer.append_data(io.imread(TMP_PATH))
                        print()
                        add_log()

                        count_all_frames += 1
                        set_progress_fr(count_all_frames, count_all_fr)

                        if process_status != 'work':
                            break
                    imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
                    os.remove(TMP_PATH)
            elif ext in ['.avi', '.mp4', '.webm', '.mov']:
                tmp_name = filename_processing(op_mode, 'numbering', base_name, '', output_dir, marker, count_correct)  # Преобразование имени файла (cv2 не воспринимает русские буквы, поэтому приходится использовать временное имя)
                res_name = filename_processing(op_mode, settings['naming_mode'], base_name, '', output_dir, marker, count_correct)

                print_tab(f'({count_all_files}) <{filename}>  ->  <{res_name}>', depth)  # Вывод информации
                add_log(f'({count_all_files}) <{filename}>  ->  <{res_name}>', depth)

                res = os.path.join(output_dir, tmp_name)
                if tmp_name not in os.listdir(output_dir):
                    os.mkdir(res)
                open(os.path.join(res, '_vid'), 'w')

                vid = VideoFileClip(pth)
                fps = min(vid.fps, 24)
                step = 1 / fps
                count_frames = int(vid.duration // step + 1)
                count = 0
                for current_duration in arange(0, vid.duration, step):
                    print_tab(f'frame {count + 1}/{count_frames}', depth)
                    add_log(f'frame {count + 1}/{count_frames}', depth)

                    frame_filename = os.path.join(res, '{:06}.png'.format(count))
                    vid.save_frame(TMP_PATH, current_duration)
                    fr = imread(TMP_PATH)
                    if settings['print_info'] == 'print':  # Вывод информации о считывании
                        print_tab(fr.shape, depth)
                        add_log(fr.shape, depth)
                    imsave(frame_filename, encode_file(fr, depth).astype(uint8))
                    count += 1
                    print()
                    add_log()

                    count_all_frames += 1
                    set_progress_fr(count_all_frames, count_all_fr)

                    if process_status != 'work':
                        break
                imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
                os.remove(TMP_PATH)

                os.rename(res, os.path.join(output_dir, res_name))
            elif isdir and '_vid' in os.listdir(pth) and op_mode == 'D':
                tmp_name = filename_processing(op_mode, 'numbering', filename, '.mp4', output_dir, marker, count_correct)  # Преобразование имени файла (cv2 не воспринимает русские буквы, поэтому приходится использовать временное имя)
                res_name = filename_processing(op_mode, settings['naming_mode'], filename, '.mp4', output_dir, marker, count_correct)

                print_tab(f'({count_all_files}) <{filename}>  ->  <{res_name}>', depth)  # Вывод информации
                add_log(f'({count_all_files}) <{filename}>  ->  <{res_name}>', depth)

                var_dir_tmp = pth
                res = os.path.join(output_dir, tmp_name)

                img = imread(os.path.join(var_dir_tmp, '000000.png'))
                height = img.shape[0]
                width = img.shape[1]
                fps = 24
                video = cv2.VideoWriter(res, 0, fps, (width, height))

                h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b = decode_file_calc(img, depth)

                frames = sorted([name for name in os.listdir(var_dir_tmp) if name.endswith('.png')])
                count_frames = len(frames)
                count = 0
                for f in frames:
                    print_tab(f'frame {count + 1}/{count_frames}', depth)
                    add_log(f'frame {count + 1}/{count_frames}', depth)

                    img = imread(os.path.join(var_dir_tmp, f))
                    if settings['print_info'] == 'print':  # Вывод информации о считывании
                        print_tab(img.shape, depth)
                        add_log(img.shape, depth)
                    fr = decode_file(img, h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b)
                    imsave(TMP_PATH, fr.astype(uint8))
                    video.write(cv2.imread(TMP_PATH))
                    count += 1
                    print()
                    add_log()

                    count_all_frames += 1
                    set_progress_fr(count_all_frames, count_all_fr)

                    if process_status != 'work':
                        break
                imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
                os.remove(TMP_PATH)
                video.release()

                os.rename(res, os.path.join(output_dir, res_name))
            elif isdir:
                res_name = filename_processing(op_mode, settings['naming_mode'], base_name, '', output_dir, marker, count_correct)  # Преобразование имени файла

                print_tab(f'({count_all_files}) <{filename}>  ->  <{res_name}>', depth)  # Вывод информации
                add_log(f'({count_all_files}) <{filename}>  ->  <{res_name}>', depth)

                new_var_dir = pth
                new_outp_dir = os.path.join(output_dir, res_name)

                if res_name not in os.listdir(output_dir):
                    os.mkdir(new_outp_dir)

                print()
                add_log()

                count_all_frames += 1
                set_progress_fr(count_all_frames, count_all_fr)
                set_progress_f_d(count_all_files, count_all_f_d)

                count_all_files, count_all_frames = converse_dir(op_mode, marker, formats, new_var_dir, new_outp_dir, count_all_files, count_all_frames, depth + 1)
                print_tab(f'{Fore.GREEN}*[DIR] ', depth, end='')
                add_log('*[DIR] ', depth, end='')
            else:
                count_all_frames += 1
                set_progress_fr(count_all_frames, count_all_fr)
        except Exception as err:  # count
            print_warn('Couldn`t process the file')
            print(f'{Fore.YELLOW}{err}{Style.RESET_ALL}\n')
            add_log(f'{err}\n')
        print_tab(f'{Fore.GREEN}Time: {perf_counter() - start}{Style.RESET_ALL}\n', depth)
        add_log(f'Time: {perf_counter() - start}\n', depth)

        set_progress_f_d(count_all_files, count_all_f_d)

        if process_status != 'work':
            break
    if process_status == 'abort':
        print(' >> Aborted <<\n')
        add_log(' >> Aborted <<\n')
    elif process_status == 'error':
        print(' >> Emergency stop <<\n')
        add_log(' >> Emergency stop <<\n')
    elif depth == 0:
        print(' >> Done <<\n')
        add_log(' >> Done <<\n')
        gui.logger.done()
    return count_all_files, count_all_frames


# Диагностика папки с файлами
def diagnostic_dir(op_mode: str, marker: str, formats: list[str], var_dir: str, output_dir: str, count_all_files: int,
                   count_all_frames: int, depth: int):
    count_correct = settings['count_from'] - 1  # Счётчик количества обработанных файлов
    for filename in os.listdir(var_dir):  # Проход по файлам
        base_name, ext = os.path.splitext(filename)
        count_all_files += 1

        print_tab(f'({count_all_files}) <{filename}>', depth)  # Вывод информации
        add_log(f'({count_all_files}) <{filename}>', depth)

        pth = os.path.join(var_dir, filename)
        isdir = os.path.isdir(pth)
        if ext.lower() not in formats and not isdir:  # Проверка формата
            print_warn('Unsupported file extension')
            print()
            add_log()
            count_all_frames += 1
            set_progress_fr(count_all_frames, count_all_fr)
            set_progress_f_d(count_all_files, count_all_f_d)
            continue
        count_correct += 1

        start = perf_counter()
        try:
            if ext in ['.png', '.jpg', '.jpeg', '.jfif', '.bmp']:
                img = imread(pth)  # Считывание изображения
                if settings['print_info'] == 'print':
                    print_tab(img.shape, depth)
                    add_log(img.shape, depth)
                print()
                add_log()

                imsave(TMP_PATH, img.astype(uint8)[0:1, 0:1] * 0)
                os.remove(TMP_PATH)

                count_all_frames += 1
                set_progress_fr(count_all_frames, count_all_fr)
            elif ext == '.gif':
                with Image.open(pth) as im:
                    for i in range(im.n_frames):
                        print_tab(f'frame {i + 1}/{im.n_frames}', depth)
                        add_log(f'frame {i + 1}/{im.n_frames}', depth)

                        im.seek(i)
                        im.save(TMP_PATH)
                        fr = imread(TMP_PATH)
                        if settings['print_info'] == 'print':  # Вывод информации о считывании
                            print_tab(fr.shape, depth)
                            add_log(fr.shape, depth)
                        imsave(TMP_PATH, fr.astype(uint8)[0:1, 0:1] * 0)

                        print()
                        add_log()

                        count_all_frames += 1
                        set_progress_fr(count_all_frames, count_all_fr)

                        if process_status != 'work':
                            break
                    imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
                    os.remove(TMP_PATH)
            elif isdir and '_gif' in os.listdir(pth) and op_mode == 'D':
                var_dir_tmp = pth
                frames = sorted([name for name in os.listdir(var_dir_tmp) if name.endswith('.png')])
                length = len(frames)
                with io.get_writer(TMP_PATH, mode='I', duration=1/24) as writer:
                    for i in range(length):
                        print_tab(f'frame {i + 1}/{length}', depth)
                        add_log(f'frame {i + 1}/{length}', depth)

                        fr = imread(os.path.join(var_dir_tmp, frames[i]))
                        if settings['print_info'] == 'print':  # Вывод информации о считывании
                            print_tab(fr.shape, depth)
                            add_log(fr.shape, depth)
                        imsave(TMP_PATH, fr.astype(uint8)[0:1, 0:1] * 0)
                        writer.append_data(io.imread(TMP_PATH))
                        print()
                        add_log()

                        count_all_frames += 1
                        set_progress_fr(count_all_frames, count_all_fr)

                        if process_status != 'work':
                            break
                    imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
                    os.remove(TMP_PATH)
            elif ext in ['.avi', '.mp4', '.webm', '.mov']:
                vid = VideoFileClip(pth)
                fps = min(vid.fps, 24)
                step = 1 / fps
                count_frames = int(vid.duration // step + 1)
                count = 0
                for current_duration in arange(0, vid.duration, step):
                    print_tab(f'frame {count + 1}/{count_frames}', depth)
                    add_log(f'frame {count + 1}/{count_frames}', depth)

                    vid.save_frame(TMP_PATH, current_duration)
                    fr = imread(TMP_PATH)
                    if settings['print_info'] == 'print':  # Вывод информации о считывании
                        print_tab(fr.shape, depth)
                        add_log(fr.shape, depth)
                    imsave(TMP_PATH, fr.astype(uint8)[0:1, 0:1] * 0)
                    count += 1
                    print()
                    add_log()

                    count_all_frames += 1
                    set_progress_fr(count_all_frames, count_all_fr)

                    if process_status != 'work':
                        break
                imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
                os.remove(TMP_PATH)
            elif isdir and '_vid' in os.listdir(pth) and op_mode == 'D':
                var_dir_tmp = pth

                img = imread(os.path.join(var_dir_tmp, '000000.png'))
                height = img.shape[0]
                width = img.shape[1]
                fps = 24
                video = cv2.VideoWriter(TMP_PATH, 0, fps, (width, height))

                frames = sorted([name for name in os.listdir(var_dir_tmp) if name.endswith('.png')])
                count_frames = len(frames)
                count = 0
                for f in frames:
                    print_tab(f'frame {count + 1}/{count_frames}', depth)
                    add_log(f'frame {count + 1}/{count_frames}', depth)

                    img = imread(os.path.join(var_dir_tmp, f))
                    if settings['print_info'] == 'print':  # Вывод информации о считывании
                        print_tab(img.shape, depth)
                        add_log(img.shape, depth)
                    imsave(TMP_PATH, img.astype(uint8)[0:1, 0:1] * 0)
                    count += 1
                    print()
                    add_log()

                    count_all_frames += 1
                    set_progress_fr(count_all_frames, count_all_fr)

                    if process_status != 'work':
                        break
                imsave(TMP_PATH, img[0:1, 0:1] * 0)  # Затирание временного файла
                os.remove(TMP_PATH)
            elif isdir:
                new_var_dir = pth

                print()
                add_log()

                count_all_frames += 1
                set_progress_fr(count_all_frames, count_all_fr)
                set_progress_f_d(count_all_files, count_all_f_d)

                count_all_files, count_all_frames = diagnostic_dir(op_mode, marker, formats, new_var_dir, output_dir, count_all_files, count_all_frames, depth + 1)
                print_tab(f'{Fore.GREEN}*[DIR] ', depth, end='')
                add_log('*[DIR] ', depth, end='')
            else:
                count_all_frames += 1
                set_progress_fr(count_all_frames, count_all_fr)
        except Exception as err:  # count
            print_warn('Couldn`t process the file')
            print(f'{Fore.YELLOW}{err}{Style.RESET_ALL}\n')
            add_log(f'{err}\n')
        print_tab(f'{Fore.GREEN}Time: {perf_counter() - start}{Style.RESET_ALL}\n', depth)
        add_log(f'Time: {perf_counter() - start}\n', depth)

        set_progress_f_d(count_all_files, count_all_f_d)

        if process_status != 'work':
            break
    if process_status == 'abort':
        print(' >> Aborted <<\n')
        add_log(' >> Aborted <<\n')
    elif process_status == 'error':
        print(' >> Emergency stop <<\n')
        add_log(' >> Emergency stop <<\n')
    elif depth == 0:
        print(' >> Done <<\n')
        add_log(' >> Done <<\n')
        gui.logger.done()
    return count_all_files, count_all_frames


# Шифровка
def encode(cmd: int):
    op_mode = 'E'
    input_dir = settings['src_dir_enc']
    output_dir = settings['dst_dir_enc']
    if not os.path.exists(input_dir):
        PopupMsgW(gui, f'Исходная папка "{input_dir}" не найдена!', title='Warning').open()
        gui.logger.destroy()
        return
    if not os.path.exists(output_dir):
        PopupMsgW(gui, f'Папка назначения "{output_dir}" не найдена!', title='Warning').open()
        gui.logger.destroy()
        return
    marker = settings['marker_enc']
    formats = ['.png', '.jpg', '.jpeg', '.jfif', '.bmp', '.gif', '.avi', '.mp4', '.webm', '.mov']
    count_start = 0
    depth = 0

    print('                                   START ENCRYPTING\n')
    global count_all_f_d, count_all_fr
    count_all_f_d, count_all_fr = count_all(op_mode, input_dir, count_start, count_start)
    if cmd == 1:
        diagnostic_dir(op_mode, marker, formats, input_dir, output_dir, count_start, count_start, depth)
    elif cmd == 2:
        converse_dir(op_mode, marker, formats, input_dir, output_dir, count_start, count_start, depth)
    print('=============================== PROCESSING IS FINISHED ===============================')


# Дешифровка
def decode(cmd: int):
    global DEC_R, DEC_G, DEC_B
    DEC_R = [0] * 256  # Массив для отмены цветового множителя для красного канала
    DEC_G = [0] * 256  # Массив для отмены цветового множителя для зелёного канала
    DEC_B = [0] * 256  # Массив для отмены цветового множителя для синего канала
    for i in range(256):
        DEC_R[i * mult_r % 256] = i
        DEC_G[i * mult_g % 256] = i
        DEC_B[i * mult_b % 256] = i

    op_mode = 'D'
    input_dir = settings['src_dir_dec']
    output_dir = settings['dst_dir_dec']
    if not os.path.exists(input_dir):
        PopupMsgW(gui, f'Исходная папка "{input_dir}" не найдена!', title='Warning').open()
        gui.logger.destroy()
        return
    if not os.path.exists(output_dir):
        PopupMsgW(gui, f'Папка назначения "{output_dir}" не найдена!', title='Warning').open()
        gui.logger.destroy()
        return
    marker = settings['marker_dec']
    formats = ['.png']
    count_start = 0
    depth = 0

    print('                                   START DECRYPTING\n')
    global count_all_f_d, count_all_fr
    count_all_f_d, count_all_fr = count_all(op_mode, input_dir, count_start, count_start)
    if cmd == 1:
        diagnostic_dir(op_mode, marker, formats, input_dir, output_dir, count_start, count_start, depth)
    elif cmd == 2:
        converse_dir(op_mode, marker, formats, input_dir, output_dir, count_start, count_start, depth)
    print('=============================== PROCESSING IS FINISHED ===============================')


""" Графический интерфейс - функции валидации """


# Ввод только заданных символов
def validate_symbols(value: str, allowed_symbols: str):
    for c in value:
        if c not in allowed_symbols:
            return False
    return True


# Ввод только натуральных чисел
def validate_natural(value: str):
    return value == '' or value.isnumeric()


# Ввод только целых чисел
def validate_num(value: str):
    return value in ['', '-'] or value.isnumeric() or (value[0] == '-' and value[1:].isnumeric())


# Ввод только до заданной длины
def validate_len(value: str, max_len: int):
    return len(value) <= max_len


# Ввод только натуральных чисел до заданной длины
def validate_natural_and_len(value: str, max_len: int):
    return validate_natural(value) and validate_len(value, max_len)


# Ввод только целых чисел до заданной длины
def validate_num_and_len(value: str, max_len: int):
    return validate_num(value) and validate_len(value, max_len)


# Ввод только символов подходящих для ключа и до длины ключа
def validate_key(value: str):
    return validate_symbols(value, KEY_SYMBOLS) and validate_len(value, KEY_LEN)


# Расширение поля ввода для длинных строк
def validate_expand(value: str, entry: tk.Entry | ttk.Entry, min_len: int, max_len: int):
    len_value = len(value)
    if len_value <= min_len:
        entry['width'] = min_len
    elif len_value >= max_len:
        entry['width'] = max_len
    else:
        entry['width'] = len_value
    return True


""" Графический интерфейс - вспомогательные функции """


# Выключить кнопку (т. к. в ttk нельзя убрать уродливую тень текста на выключенных кнопках, пришлось делать по-своему)
def btn_disable(btn: ttk.Button):
    btn.configure(command='', style='Disabled.TButton')


""" Графический интерфейс - всплывающие окна """


# Всплывающее окно с сообщением
class PopupMsgW(tk.Toplevel):
    def __init__(self, parent, msg: str, btn_text='OK', title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=ST_BG[th])

        ttk.Label(self, text=msg, justify='center', style='Default.TLabel').grid(row=0, column=0, padx=6, pady=4)
        ttk.Button(self, text=btn_text, command=self.destroy, takefocus=False, style='Default.TButton').grid(row=1, column=0, padx=6, pady=4)

    def open(self):
        self.grab_set()
        self.wait_window()


# Всплывающее окно с сообщением и двумя кнопками
class PopupDialogueW(tk.Toplevel):
    def __init__(self, parent, msg='Are you sure?', btn_yes='Yes', btn_no='Cancel', title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=ST_BG[th])

        self.answer = False

        ttk.Label(self, text=msg, justify='center', style='Default.TLabel').grid(row=0, columnspan=2, padx=6, pady=4)
        ttk.Button(self, text=btn_yes, command=self.yes, takefocus=False, style='Yes.TButton').grid(row=1, column=0, padx=(6, 10), pady=4, sticky='E')
        ttk.Button(self, text=btn_no, command=self.no, takefocus=False, style='No.TButton').grid(row=1, column=1, padx=(10, 6), pady=4, sticky='W')

    def yes(self):
        self.answer = True
        self.destroy()

    def no(self):
        self.answer = False
        self.destroy()

    def open(self):
        return self.answer


# Всплывающее окно с полем Combobox
class PopupChooseW(tk.Toplevel):
    def __init__(self, parent, values: list | tuple, msg='Choose the one of these', btn_text='Confirm',
                 default_value=None, title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=ST_BG[th])

        self.answer = tk.StringVar(value=default_value)

        ttk.Label(self, text=msg, justify='center', style='Default.TLabel').grid(row=0, padx=6, pady=(4, 1))
        ttk.Combobox(self, textvariable=self.answer, values=values, state='readonly', style='Default.TCombobox').grid(row=1, padx=6, pady=1)
        ttk.Button(self, text=btn_text, command=self.destroy, takefocus=False, style='Default.TButton').grid(row=2, padx=6, pady=4)

    def open(self):
        self.grab_set()
        self.wait_window()
        return self.answer.get()


""" Графический интерфейс - вспомогательные окна """


# Всплывающее окно для ввода названия сохранения
class EnterSaveNameW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[th])

        self.name_is_correct = False

        self.name = tk.StringVar()

        self.vcmd = (self.register(lambda value: validate_symbols(value, FN_SYMBOLS_WITH_RU)), '%P')

        ttk.Label(self, text='Enter a name for save your custom settings', justify='center', style='Default.TLabel').grid(row=0, padx=6, pady=(4, 1))
        ttk.Entry(self, textvariable=self.name, validate='key', validatecommand=self.vcmd, style='Default.TEntry').grid(row=1, padx=6, pady=1)
        ttk.Button(self, text='Confirm', command=self.check_and_return, takefocus=False, style='Default.TButton').grid(row=2, padx=6, pady=4)

    def check_and_return(self):
        filename = self.name.get()
        if filename == '':
            PopupMsgW(self, 'Incorrect name for save', title='Warning').open()
            return
        self.name_is_correct = True
        if f'{filename}.txt' in os.listdir(CUSTOM_SETTINGS_PATH):  # Если уже есть сохранение с таким названием
            window = PopupDialogueW(self, 'A save with that name already exists!\nDo you want to overwrite it?')
            self.wait_window(window)
            answer = window.open()
            if not answer:
                self.name_is_correct = False
                return
        self.destroy()

    def open(self):
        self.grab_set()
        self.wait_window()
        return self.name_is_correct, self.name.get()


# Всплывающее окно для ввода пароля
class EnterKeyW(tk.Toplevel):
    def __init__(self, parent, action: str):
        super().__init__(parent)
        self.title('Media encrypter - Key')
        self.configure(bg=ST_BG[th])

        self.has_key = False
        self.cmd = 0

        self.key = tk.StringVar()

        self.vcmd = (self.register(validate_key), '%P')

        self.frame_main = ttk.Frame(self, style='Default.TFrame')
        self.frame_main.grid(row=0, columnspan=2, padx=6, pady=4)

        ttk.Label(self.frame_main, text=f'Enter a key ({KEY_LEN} symbols; only latin letters, digits, - and _)', justify='center', style='Default.TLabel').grid(row=0, columnspan=3, padx=6, pady=4)
        ttk.Label(self.frame_main, text='An example of a key:', style='Default.TLabel').grid(row=1, column=0, padx=(6, 1), pady=1, sticky='E')
        ttk.Label(self.frame_main, text='Enter a key:', style='Default.TLabel').grid(row=2, column=0, padx=(6, 1), pady=(1, 4), sticky='E')

        # Функция нужна, чтобы можно было скопировать ключ-пример, но нельзя было его изменить
        def focus_text(event):
            self.txt_example_key.config(state='normal')
            self.txt_example_key.focus()
            self.txt_example_key.config(state='disabled')

        self.txt_example_key = tk.Text(self.frame_main, height=1, width=KEY_LEN, borderwidth=1, font='TkFixedFont', bg=ST_BG_FIELDS[th], fg=ST_FG_EXAMPLE[th], highlightbackground=ST_BORDER[th], selectbackground=ST_SELECT[th], highlightcolor=ST_HIGHLIGHT[th])
        self.txt_example_key.insert(1.0, settings['example_key'])
        self.txt_example_key.grid(row=1, column=1, padx=(0, 4), pady=1)
        self.txt_example_key.configure(state='disabled')
        self.txt_example_key.bind('<Button-1>', focus_text)

        self.entry_key = ttk.Entry(self.frame_main, textvariable=self.key, width=KEY_LEN, validate='key', validatecommand=self.vcmd, show='*', font='TkFixedFont', style='Key.TEntry')
        self.btn_copy_example  = ttk.Button(self.frame_main, text='Copy', command=self.copy_example_key, takefocus=False, style='Default.TButton')
        self.btn_show_hide_key = ttk.Button(self.frame_main, text='Show', command=self.show_hide_key, takefocus=False,    style='Default.TButton')

        self.btn_copy_example.grid( row=1, column=2, padx=(0, 6), pady=1)
        self.entry_key.grid(        row=2, column=1, padx=(0, 4), pady=(1, 4))
        self.btn_show_hide_key.grid(row=2, column=2, padx=(0, 6), pady=(1, 4))

        self.btn_diagnostic = ttk.Button(self, text='Scan files', command=self.to_diagnostic, takefocus=False, style='Default.TButton')
        self.btn_submit     = ttk.Button(self, text=action,       command=self.to_process, takefocus=False,    style='Default.TButton')
        self.btn_diagnostic.grid(row=1, column=0, padx=6, pady=(0, 4))
        self.btn_submit.grid(    row=1, column=1, padx=6, pady=(0, 4))

    # Подставить ключ-пример
    def copy_example_key(self):
        self.key.set(settings['example_key'])

    # Показать/скрыть ключ
    def show_hide_key(self):
        if self.entry_key['show'] == '*':
            self.entry_key['show'] = ''
            self.btn_show_hide_key['text'] = 'Hide'
        else:
            self.entry_key['show'] = '*'
            self.btn_show_hide_key['text'] = 'Show'

    # Проверить корректность ключа и, если корректен, сохранить
    def check_key_and_return(self):
        key = self.key.get()
        code, cause = check_key(key)
        if code == 'L':  # Если неверная длина ключа
            PopupMsgW(self, f'Invalid key length: {cause}!\nMust be {KEY_LEN}', title='Warning').open()
            return
        self.has_key = True
        self.destroy()

    # Начать диагностику
    def to_diagnostic(self):
        self.cmd = 1
        self.check_key_and_return()

    # Начать обработку
    def to_process(self):
        self.cmd = 2
        self.check_key_and_return()

    def open(self):
        self.grab_set()
        self.wait_window()
        return self.has_key, self.key.get(), self.cmd


# Окно журнала
class LoggerW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Media encrypter - Progress')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.str_progress_f_d = tk.StringVar(value='Calculation...')
        self.str_progress_fr = tk.StringVar(value='Calculation...')

        self.frame_progress = ttk.Frame(self, style='Default.TFrame')
        self.frame_progress.grid(row=0, columnspan=2, padx=6, pady=(6, 4))

        ttk.Label(self.frame_progress, text='Progress (files and dirs):', style='Default.TLabel').grid(row=0, column=0, padx=(6, 0), pady=4, sticky='E')
        ttk.Label(self.frame_progress, text='Progress (with frames):', style='Default.TLabel').grid(row=1, column=0, padx=(6, 0), pady=4, sticky='E')
        self.progressbar_f_d = ttk.Progressbar(self.frame_progress, value=0, length=450, style='Default.Horizontal.TProgressbar', orient='horizontal')
        self.progressbar_fr  = ttk.Progressbar(self.frame_progress, value=0, length=450, style='Default.Horizontal.TProgressbar', orient='horizontal')
        self.lbl_progress_f_d = ttk.Label(self.frame_progress, textvariable=self.str_progress_f_d, justify='center', style='Default.TLabel')
        self.lbl_progress_fr  = ttk.Label(self.frame_progress, textvariable=self.str_progress_fr, justify='center', style='Default.TLabel')

        self.progressbar_f_d.grid( row=0, column=1, padx=4,      pady=4)
        self.progressbar_fr.grid(  row=1, column=1, padx=4,      pady=4)
        self.lbl_progress_f_d.grid(row=0, column=2, padx=(0, 6), pady=4)
        self.lbl_progress_fr.grid( row=1, column=2, padx=(0, 6), pady=4)

        self.scrollbar = ttk.Scrollbar(self, style='Vertical.TScrollbar')
        self.log = tk.Text(self, width=70, height=30, state='disabled', yscrollcommand=self.scrollbar.set, bg=ST_BG_FIELDS[th], fg=ST_FG[th], highlightbackground=ST_BORDER[th], selectbackground=ST_SELECT[th], relief=ST_RELIEF[th])
        self.btn_abort = ttk.Button(self, text='Abort', command=self.abort_process, takefocus=False, style='No.TButton')

        self.log.grid(        row=1, column=0, sticky='NSEW', padx=(6, 0), pady=0)
        self.scrollbar.grid(  row=1, column=1, sticky='NSW',  padx=(0, 6), pady=0)
        self.btn_abort.grid(  row=2, columnspan=2, padx=6, pady=(4, 6))

        self.scrollbar.config(command=self.log.yview)

    # Прервать обработку
    def abort_process(self):
        global process_status
        process_status = 'abort'
        btn_disable(self.btn_abort)
        self.progressbar_f_d['style'] = 'Aborted.Horizontal.TProgressbar'
        self.progressbar_fr['style'] = 'Aborted.Horizontal.TProgressbar'

    # Завершение обработки
    def done(self):
        global process_status
        process_status = 'done'
        btn_disable(self.btn_abort)
        self.progressbar_f_d['style'] = 'Done.Horizontal.TProgressbar'
        self.progressbar_fr['style'] = 'Done.Horizontal.TProgressbar'

    # Добавить запись в журнал
    def add_log(self, msg='', tab=0, end='\n'):
        self.log['state'] = 'normal'
        if self.log.yview()[1] == 1.0:
            self.log.insert(tk.END, '~ ' * tab + str(msg) + end)
            self.log.yview_moveto(1.0)
        else:
            self.log.insert(tk.END, '~ ' * tab + str(msg) + end)
        self.log['state'] = 'disabled'

    # Установить прогресс (файлы и папки)
    def set_progress_f_d(self, num: int, den: int):
        self.progressbar_f_d['value'] = 100 * num / den
        self.str_progress_f_d.set(f'{num}/{den}')

    # Установить прогресс (кадры)
    def set_progress_fr(self, num: int, den: int):
        self.progressbar_fr['value'] = 100 * num / den
        self.str_progress_fr.set(f'{num}/{den}')

    def open(self):
        self.grab_set()
        self.wait_window()


# Окно уведомления о выходе новой версии
class LastVersionW(tk.Toplevel):
    def __init__(self, parent, last_version: str):
        super().__init__(parent)
        self.title('New version available')
        self.configure(bg=ST_BG[th])

        self.var_url = tk.StringVar(value=URL_GITHUB)  # Ссылка, для загрузки новой версии

        self.lbl_msg = ttk.Label(self, text=f'Доступна новая версия программы\n'
                                            f'{last_version}',
                                 justify='center', style='Default.TLabel')
        self.entry_url = ttk.Entry(self, textvariable=self.var_url, state='readonly', width=45, justify='center',
                                   style='Default.TEntry')
        self.btn_update = ttk.Button(self, text='Обновить', command=self.download_and_install, takefocus=False,
                                     style='Default.TButton')
        self.btn_close = ttk.Button(self, text='Закрыть', command=self.destroy, takefocus=False,
                                    style='Default.TButton')

        self.lbl_msg.grid(   row=1, columnspan=2, padx=6, pady=(4, 0))
        self.entry_url.grid( row=2, columnspan=2, padx=6, pady=(0, 4))
        self.btn_update.grid(row=3, column=0,     padx=6, pady=4)
        self.btn_close.grid( row=3, column=1,     padx=6, pady=4)

    # Скачать и установить обновление
    def download_and_install(self):
        try:  # Загрузка
            print('\ndownload zip')
            wget.download(URL_DOWNLOAD_ZIP, out=os.path.dirname(__file__))  # Скачиваем архив с обновлением
        except:
            PopupMsgW(self, 'Не удалось загрузить обновление!', title='Warning').open()
            self.destroy()
        try:  # Установка
            # Распаковываем архив во временную папку
            print('extracting')
            with zipfile.ZipFile(NEW_VERSION_ZIP, 'r') as zip_file:
                zip_file.extractall(os.path.dirname(__file__))
            # Удаляем архив
            print('delete zip')
            os.remove(NEW_VERSION_ZIP)
            # Удаляем файлы текущей версии
            print('delete old files')
            os.remove('ver')
            os.remove('README.md')
            os.remove('README_ru.txt')
            os.remove('main.py')
            # Из временной папки достаём файлы новой версии
            print('set new files')
            os.replace(os.path.join(NEW_VERSION_DIR, 'ver'), 'ver')
            os.replace(os.path.join(NEW_VERSION_DIR, 'README.md'), 'README.md')
            os.replace(os.path.join(NEW_VERSION_DIR, 'README_ru.txt'), 'README_ru.txt')
            os.replace(os.path.join(NEW_VERSION_DIR, 'main.py'), 'main.py')
            # Удаляем временную папку
            print('delete tmp dir')
            rmtree(NEW_VERSION_DIR)
            PopupMsgW(self, 'Обновление успешно установлено\nПрограмма закроется').open()
        except:
            PopupMsgW(self, 'Не удалось установить обновление!', title='Warning').open()
            self.destroy()
        else:
            exit(777)

    def open(self):
        self.grab_set()
        self.wait_window()


""" Графический интерфейс - основные окна """


# Окно настроек
class SettingsW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Media encrypter - Settings')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])
        self.parent = parent

        self.key = tk.StringVar()

        # Переменные, к которым привязаны настройки
        self.var_style         = tk.StringVar(value=settings['theme'])
        self.var_show_updates  = tk.BooleanVar(value=str_to_bool(settings['show_updates']))
        self.var_support_ru    = tk.BooleanVar(value=str_to_bool(settings['support_ru']))
        self.var_processing_ru = tk.StringVar(value=settings['processing_ru'])
        self.var_naming_mode   = tk.StringVar(value=settings['naming_mode'])
        self.var_count_from    = tk.StringVar(value=str(settings['count_from']))
        self.var_format        = tk.StringVar(value=str(settings['format']))
        self.var_marker_enc    = tk.StringVar(value=settings['marker_enc'])
        self.var_marker_dec    = tk.StringVar(value=settings['marker_dec'])
        self.var_src_dir_enc   = tk.StringVar(value=settings['src_dir_enc'])
        self.var_dst_dir_enc   = tk.StringVar(value=settings['dst_dir_enc'])
        self.var_src_dir_dec   = tk.StringVar(value=settings['src_dir_dec'])
        self.var_dst_dir_dec   = tk.StringVar(value=settings['dst_dir_dec'])
        self.var_example_key   = tk.StringVar(value=settings['example_key'])
        self.var_print_info    = tk.StringVar(value=settings['print_info'])

        # Функции для валидации
        self.vcmd_natural = (self.register(lambda value: validate_natural_and_len(value, 3)), '%P')
        self.vcmd_num     = (self.register(validate_num), '%P')
        self.vcmd_key     = (self.register(validate_key), '%P')

        """
        *---TOPLEVEL-------------------------------------------------*
        |  *---FRAME-ALL------------------------------------------*  |
        |  |  *---FRAME-FIELDS---------------------------------*  |  |
        |  |  |  <Label> <Combobox>                            |  |  |
        |  |  |  <Label> <Entry>                               |  |  |
        |  |  |  <Label> <Frame (внутренние фреймы)>           |  |  |
        |  |  |  ...                                           |  |  |
        |  |  *------------------------------------------------*  |  |
        |  |    [Set defaults]    [Save]    [Load]    [Remove]    |  |
        |  *------------------------------------------------------*  |
        |                [Accept]             [Close]                |
        *------------------------------------------------------------*
        """

        # Внешние фреймы
        self.frame_all    = ttk.Frame(self,           style='Default.TFrame')
        self.frame_fields = ttk.Frame(self.frame_all, style='Default.TFrame')

        # Названия настроек
        self.lbl_style         = ttk.Label(self.frame_fields, text='Style',                                        style='Default.TLabel')
        self.lbl_show_updates  = ttk.Label(self.frame_fields, text='Show update notifications',                    style='Default.TLabel')
        self.lbl_support_ru    = ttk.Label(self.frame_fields, text='Russian letters in filenames support',         style='Default.TLabel')
        self.lbl_processing_ru = ttk.Label(self.frame_fields, text='Russian letters in filenames processing mode', style='Default.TLabel')
        self.lbl_naming_mode   = ttk.Label(self.frame_fields, text='File names conversion mode',                   style='Default.TLabel')
        self.lbl_count_from    = ttk.Label(self.frame_fields, text='Start numbering files from',                   style='Default.TLabel')
        self.lbl_format        = ttk.Label(self.frame_fields, text='Minimal number of characters in number',       style='Default.TLabel')
        self.lbl_marker_enc    = ttk.Label(self.frame_fields, text='Marker for encoded files',                     style='Default.TLabel')
        self.lbl_marker_dec    = ttk.Label(self.frame_fields, text='Marker for decoded files',                     style='Default.TLabel')
        self.lbl_src_dir_enc   = ttk.Label(self.frame_fields, text='Source folder when encoding',                  style='Default.TLabel')
        self.lbl_dst_dir_enc   = ttk.Label(self.frame_fields, text='Destination folder when encoding',             style='Default.TLabel')
        self.lbl_src_dir_dec   = ttk.Label(self.frame_fields, text='Source folder when decoding',                  style='Default.TLabel')
        self.lbl_dst_dir_dec   = ttk.Label(self.frame_fields, text='Destination folder when decoding',             style='Default.TLabel')
        self.lbl_example_key   = ttk.Label(self.frame_fields, text='Example of a key',                             style='Default.TLabel')
        self.lbl_print_info    = ttk.Label(self.frame_fields, text='Whether to print info',                        style='Default.TLabel')

        # Сами настройки
        self.combo_style         = ttk.Combobox(   self.frame_fields, textvariable=self.var_style,         values=THEME_MODES,               state='readonly', style='Default.TCombobox')
        self.check_show_updates  = ttk.Checkbutton(self.frame_fields,     variable=self.var_show_updates,                                                      style='Default.TCheckbutton')
        self.check_support_ru    = ttk.Checkbutton(self.frame_fields,     variable=self.var_support_ru,    command=self.processing_ru_state,                   style='Default.TCheckbutton')
        self.combo_processing_ru = ttk.Combobox(   self.frame_fields, textvariable=self.var_processing_ru, values=PROCESSING_RU_MODES,       state='readonly', style='Default.TCombobox')
        self.combo_naming_mode   = ttk.Combobox(   self.frame_fields, textvariable=self.var_naming_mode,   values=NAMING_MODES,              state='readonly', style='Default.TCombobox')
        self.frame_count_from    = ttk.Frame(self.frame_fields, style='Invis.TFrame')
        self.frame_format        = ttk.Frame(self.frame_fields, style='Invis.TFrame')
        self.frame_marker_enc    = ttk.Frame(self.frame_fields, style='Invis.TFrame')
        self.frame_marker_dec    = ttk.Frame(self.frame_fields, style='Invis.TFrame')
        self.frame_src_dir_enc   = ttk.Frame(self.frame_fields, style='Invis.TFrame')
        self.frame_dst_dir_enc   = ttk.Frame(self.frame_fields, style='Invis.TFrame')
        self.frame_src_dir_dec   = ttk.Frame(self.frame_fields, style='Invis.TFrame')
        self.frame_dst_dir_dec   = ttk.Frame(self.frame_fields, style='Invis.TFrame')
        self.entry_example_key   = ttk.Entry(   self.frame_fields, textvariable=self.var_example_key, width=KEY_LEN, validate='key', validatecommand=self.vcmd_key, font='TkFixedFont', style='Default.TEntry')
        self.combo_print_info    = ttk.Combobox(self.frame_fields, textvariable=self.var_print_info, values=PRINT_INFO_MODES, state='readonly', style='Default.TCombobox')

        if not self.var_support_ru.get():
            self.combo_processing_ru['state'] = 'disabled'

        # Содержимое настроек с фреймами
        min_len_marker = 10
        max_len_marker = 70
        min_len_dir = 50
        max_len_dir = 120
        self.entry_count_from  = ttk.Entry(self.frame_count_from,  textvariable=self.var_count_from,  width=10, validate='key', validatecommand=self.vcmd_num, style='Default.TEntry')
        self.entry_format      = ttk.Entry(self.frame_format,      textvariable=self.var_format,      width=5,  validate='key', validatecommand=self.vcmd_natural, style='Default.TEntry')
        self.entry_marker_enc  = ttk.Entry(self.frame_marker_enc,  textvariable=self.var_marker_enc,  width=min(max_len_marker,  max(min_len_marker, len(self.var_marker_enc.get()))),  font='TkFixedFont', validate='key', style='Default.TEntry')
        self.entry_marker_dec  = ttk.Entry(self.frame_marker_dec,  textvariable=self.var_marker_dec,  width=min(max_len_marker,  max(min_len_marker, len(self.var_marker_dec.get()))),  font='TkFixedFont', validate='key', style='Default.TEntry')
        self.entry_src_dir_enc = ttk.Entry(self.frame_src_dir_enc, textvariable=self.var_src_dir_enc, width=min(max_len_dir,     max(min_len_dir,    len(self.var_src_dir_enc.get()))), font='TkFixedFont', validate='key', style='Default.TEntry')
        self.entry_dst_dir_enc = ttk.Entry(self.frame_dst_dir_enc, textvariable=self.var_dst_dir_enc, width=min(max_len_dir,     max(min_len_dir,    len(self.var_dst_dir_enc.get()))), font='TkFixedFont', validate='key', style='Default.TEntry')
        self.entry_src_dir_dec = ttk.Entry(self.frame_src_dir_dec, textvariable=self.var_src_dir_dec, width=min(max_len_dir,     max(min_len_dir,    len(self.var_src_dir_dec.get()))), font='TkFixedFont', validate='key', style='Default.TEntry')
        self.entry_dst_dir_dec = ttk.Entry(self.frame_dst_dir_dec, textvariable=self.var_dst_dir_dec, width=min(max_len_dir,     max(min_len_dir,    len(self.var_dst_dir_dec.get()))), font='TkFixedFont', validate='key', style='Default.TEntry')
        self.entry_marker_enc ['validatecommand'] = (self.register(lambda value: validate_expand(value, self.entry_marker_enc,  min_len_marker, max_len_marker)), '%P')
        self.entry_marker_dec ['validatecommand'] = (self.register(lambda value: validate_expand(value, self.entry_marker_dec,  min_len_marker, max_len_marker)), '%P')
        self.entry_src_dir_enc['validatecommand'] = (self.register(lambda value: validate_expand(value, self.entry_src_dir_enc, min_len_dir,    max_len_dir)),    '%P')
        self.entry_dst_dir_enc['validatecommand'] = (self.register(lambda value: validate_expand(value, self.entry_dst_dir_enc, min_len_dir,    max_len_dir)),    '%P')
        self.entry_src_dir_dec['validatecommand'] = (self.register(lambda value: validate_expand(value, self.entry_src_dir_dec, min_len_dir,    max_len_dir)),    '%P')
        self.entry_dst_dir_dec['validatecommand'] = (self.register(lambda value: validate_expand(value, self.entry_dst_dir_dec, min_len_dir,    max_len_dir)),    '%P')

        self.lbl_note_count_from = ttk.Label(self.frame_count_from, text='(if the numbering name processing mode is selected)',      style='Default.TLabel')
        self.lbl_note_format     = ttk.Label(self.frame_format,     text='(if the numbering name processing mode is selected)',      style='Default.TLabel')
        self.lbl_note_marker_enc = ttk.Label(self.frame_marker_enc, text='(if the prefix/postfix name processing mode is selected)', style='Default.TLabel')
        self.lbl_note_marker_dec = ttk.Label(self.frame_marker_dec, text='(if the prefix/postfix name processing mode is selected)', style='Default.TLabel')
        try:
            self.img_search = tk.PhotoImage(file=os.path.join(IMAGES_PATH, 'search.png'))
            self.btn_src_enc = ttk.Button(self.frame_src_dir_enc, image=self.img_search, command=self.choose_source_enc, takefocus=False, style='Image.TButton')
            self.btn_dst_enc = ttk.Button(self.frame_dst_dir_enc, image=self.img_search, command=self.choose_dest_enc, takefocus=False,   style='Image.TButton')
            self.btn_src_dec = ttk.Button(self.frame_src_dir_dec, image=self.img_search, command=self.choose_source_dec, takefocus=False, style='Image.TButton')
            self.btn_dst_dec = ttk.Button(self.frame_dst_dir_dec, image=self.img_search, command=self.choose_dest_dec, takefocus=False,   style='Image.TButton')
        except:
            self.btn_src_enc = ttk.Button(self.frame_src_dir_enc, text='Search', command=self.choose_source_enc, style='Default.TButton')
            self.btn_dst_enc = ttk.Button(self.frame_dst_dir_enc, text='Search', command=self.choose_dest_enc,   style='Default.TButton')
            self.btn_src_dec = ttk.Button(self.frame_src_dir_dec, text='Search', command=self.choose_source_dec, style='Default.TButton')
            self.btn_dst_dec = ttk.Button(self.frame_dst_dir_dec, text='Search', command=self.choose_dest_dec,   style='Default.TButton')

        # Кнопки общего фрейма
        self.btn_def           = ttk.Button(self.frame_all, text='Set default settings',                          command=self.set_default_settings, takefocus=False,   style='Default.TButton')
        self.btn_save_custom   = ttk.Button(self.frame_all, text='Save current settings as your custom settings', command=self.save_custom_settings, takefocus=False,   style='Default.TButton')
        self.btn_load_custom   = ttk.Button(self.frame_all, text='Load your custom settings',                     command=self.load_custom_settings, takefocus=False,   style='Default.TButton')
        self.btn_remove_custom = ttk.Button(self.frame_all, text='Remove your custom settings',                   command=self.remove_custom_settings, takefocus=False, style='Default.TButton')

        # Кнопки окна
        self.btn_save  = ttk.Button(self, text='Accept', command=self.save, takefocus=False, style='Yes.TButton')
        self.btn_close = ttk.Button(self, text='Close',  command=self.close, takefocus=False, style='No.TButton')

        # Расположение настроек
        self.frame_all.grid(   row=0, column=0, columnspan=2, padx=4, pady=4)
        self.frame_fields.grid(row=0, column=0, columnspan=2, padx=4, pady=4)

        self.lbl_style.grid(        row=0,  column=0, padx=(6, 1), pady=(4, 1), sticky='E')
        self.lbl_show_updates.grid( row=1,  column=0, padx=(6, 1), pady=1,      sticky='E')
        self.lbl_support_ru.grid(   row=2,  column=0, padx=(6, 1), pady=1,      sticky='E')
        self.lbl_processing_ru.grid(row=3,  column=0, padx=(6, 1), pady=1,      sticky='E')
        self.lbl_naming_mode.grid(  row=4,  column=0, padx=(6, 1), pady=1,      sticky='E')
        self.lbl_count_from.grid(   row=5,  column=0, padx=(6, 1), pady=1,      sticky='E')
        self.lbl_format.grid(       row=6,  column=0, padx=(6, 1), pady=1,      sticky='E')
        self.lbl_marker_enc.grid(   row=7,  column=0, padx=(6, 1), pady=1,      sticky='E')
        self.lbl_marker_dec.grid(   row=8,  column=0, padx=(6, 1), pady=1,      sticky='E')
        self.lbl_src_dir_enc.grid(  row=9,  column=0, padx=(6, 1), pady=1,      sticky='E')
        self.lbl_dst_dir_enc.grid(  row=10, column=0, padx=(6, 1), pady=1,      sticky='E')
        self.lbl_src_dir_dec.grid(  row=11, column=0, padx=(6, 1), pady=1,      sticky='E')
        self.lbl_dst_dir_dec.grid(  row=12, column=0, padx=(6, 1), pady=1,      sticky='E')
        self.lbl_example_key.grid(  row=13, column=0, padx=(6, 1), pady=1,      sticky='E')
        self.lbl_print_info.grid(   row=14, column=0, padx=(6, 1), pady=(1, 4), sticky='E')

        self.combo_style.grid(        row=0,  column=1, padx=(0, 6), pady=(4, 1), sticky='W')
        self.check_show_updates.grid( row=1,  column=1, padx=(0, 6), pady=1,      sticky='W')
        self.check_support_ru.grid(   row=2,  column=1, padx=(0, 6), pady=1,      sticky='W')
        self.combo_processing_ru.grid(row=3,  column=1, padx=(0, 6), pady=1,      sticky='W')
        self.combo_naming_mode.grid(  row=4,  column=1, padx=(0, 6), pady=1,      sticky='W')
        self.frame_count_from.grid(   row=5,  column=1, padx=(0, 6), pady=1,      sticky='W')
        self.frame_format.grid(       row=6,  column=1, padx=(0, 6), pady=1,      sticky='W')
        self.frame_marker_enc.grid(   row=7,  column=1, padx=(0, 6), pady=1,      sticky='W')
        self.frame_marker_dec.grid(   row=8,  column=1, padx=(0, 6), pady=1,      sticky='W')
        self.frame_src_dir_enc.grid(  row=9,  column=1, padx=(0, 6), pady=1,      sticky='W')
        self.frame_dst_dir_enc.grid(  row=10, column=1, padx=(0, 6), pady=1,      sticky='W')
        self.frame_src_dir_dec.grid(  row=11, column=1, padx=(0, 6), pady=1,      sticky='W')
        self.frame_dst_dir_dec.grid(  row=12, column=1, padx=(0, 6), pady=1,      sticky='W')
        self.entry_example_key.grid(  row=13, column=1, padx=(0, 6), pady=1,      sticky='W')
        self.combo_print_info.grid(   row=14, column=1, padx=(0, 6), pady=(1, 4), sticky='W')

        self.entry_count_from.grid( row=0, column=0, padx=(0, 1))
        self.entry_format.grid(     row=0, column=0, padx=(0, 1))
        self.entry_marker_enc.grid( row=0, column=0, padx=(0, 1))
        self.entry_marker_dec.grid( row=0, column=0, padx=(0, 1))
        self.entry_src_dir_enc.grid(row=0, column=0, padx=(0, 1))
        self.entry_dst_dir_enc.grid(row=0, column=0, padx=(0, 1))
        self.entry_src_dir_dec.grid(row=0, column=0, padx=(0, 1))
        self.entry_dst_dir_dec.grid(row=0, column=0, padx=(0, 1))

        self.lbl_note_count_from.grid(row=0, column=1)
        self.lbl_note_format.grid(    row=0, column=1)
        self.lbl_note_marker_enc.grid(row=0, column=1)
        self.lbl_note_marker_dec.grid(row=0, column=1)

        self.btn_src_enc.grid(row=0, column=1)
        self.btn_dst_enc.grid(row=0, column=1)
        self.btn_src_dec.grid(row=0, column=1)
        self.btn_dst_dec.grid(row=0, column=1)

        self.btn_def.grid(          row=1, column=0, padx=4,      pady=(0, 4), sticky='E')
        self.btn_save_custom.grid(  row=1, column=1, padx=(0, 4), pady=(0, 4), sticky='W')
        self.btn_load_custom.grid(  row=2, column=0, padx=4,      pady=(0, 4), sticky='E')
        self.btn_remove_custom.grid(row=2, column=1, padx=(0, 4), pady=(0, 4), sticky='W')

        self.btn_save.grid( row=2, column=0, pady=(0, 4))
        self.btn_close.grid(row=2, column=1, pady=(0, 4))

    # Заблокировать/разблокировать изменение настройки обработки кириллицы
    def processing_ru_state(self):
        if not self.var_support_ru.get():
            self.combo_processing_ru['state'] = 'disabled'
            self.var_processing_ru.set(DEFAULT_SETTINGS['processing_ru'])
        else:
            self.combo_processing_ru['state'] = 'readonly'

    # Были ли изменены настройки
    def has_changes(self):
        return str(settings['count_from']) != self.var_count_from.get() or\
            str(settings['format']) != self.var_format.get() or \
            str_to_bool(settings['show_updates']) != self.var_show_updates.get() or\
            str_to_bool(settings['support_ru']) != self.var_support_ru.get() or\
            settings['processing_ru'] != self.var_processing_ru.get() or\
            settings['naming_mode'] != self.var_naming_mode.get() or\
            settings['print_info'] != self.var_print_info.get() or\
            settings['theme'] != self.var_style.get() or\
            settings['marker_enc'] != self.var_marker_enc.get() or\
            settings['marker_dec'] != self.var_marker_dec.get() or\
            settings['src_dir_enc'] != self.var_src_dir_enc.get() or\
            settings['dst_dir_enc'] != self.var_dst_dir_enc.get() or\
            settings['src_dir_dec'] != self.var_src_dir_dec.get() or\
            settings['dst_dir_dec'] != self.var_dst_dir_dec.get() or\
            settings['example_key'] != self.var_example_key.get()

    # Выбор папки источника при шифровке
    def choose_source_enc(self):
        directory = askdirectory(initialdir=os.path.dirname(__file__))
        self.var_src_dir_enc.set(directory)

    # Выбор папки назначения при шифровке
    def choose_dest_enc(self):
        directory = askdirectory(initialdir=os.path.dirname(__file__))
        self.var_dst_dir_enc.set(directory)

    # Выбор папки источника при дешифровке
    def choose_source_dec(self):
        directory = askdirectory(initialdir=os.path.dirname(__file__))
        self.var_src_dir_dec.set(directory)

    # Выбор папки назначения при дешифровке
    def choose_dest_dec(self):
        directory = askdirectory(initialdir=os.path.dirname(__file__))
        self.var_dst_dir_dec.set(directory)

    # Установить настройки по умолчанию
    def set_default_settings(self):
        self.var_count_from.set(str(DEFAULT_SETTINGS['count_from']))
        self.var_format.set(str(DEFAULT_SETTINGS['format']))
        self.var_show_updates.set(str_to_bool(DEFAULT_SETTINGS['show_updates']))
        self.var_support_ru.set(str_to_bool(DEFAULT_SETTINGS['support_ru']))
        self.var_processing_ru.set(DEFAULT_SETTINGS['processing_ru'])
        self.var_naming_mode.set(DEFAULT_SETTINGS['naming_mode'])
        self.var_print_info.set(DEFAULT_SETTINGS['print_info'])
        self.var_style.set(DEFAULT_SETTINGS['theme'])
        self.var_marker_enc.set(DEFAULT_SETTINGS['marker_enc'])
        self.var_marker_dec.set(DEFAULT_SETTINGS['marker_dec'])
        self.var_src_dir_enc.set(DEFAULT_SETTINGS['src_dir_enc'])
        self.var_dst_dir_enc.set(DEFAULT_SETTINGS['dst_dir_enc'])
        self.var_src_dir_dec.set(DEFAULT_SETTINGS['src_dir_dec'])
        self.var_dst_dir_dec.set(DEFAULT_SETTINGS['dst_dir_dec'])
        self.var_example_key.set(DEFAULT_SETTINGS['example_key'])

    # Сохранить пользовательские настройки
    def save_custom_settings(self):
        if self.has_changes():  # Если были изменения, то предлагается сохранить их
            window = PopupDialogueW(self, f'There are unsaved changes!\n Do you want to continue?', title='Warning')
            self.wait_window(window)
            answer = window.open()
            if not answer:
                return
        window = EnterSaveNameW(self)
        filename_is_correct, filename = window.open()
        if not filename_is_correct:
            return
        copyfile(SETTINGS_PATH, os.path.join(CUSTOM_SETTINGS_PATH, f'{filename}.txt'))

    # Выбрать файл с сохранением
    def choose_custom_save(self, cmd_name: str):
        csf_count = 0
        csf_list = []
        for file_name in os.listdir(CUSTOM_SETTINGS_PATH):
            base_name, ext = os.path.splitext(file_name)
            if ext == '.txt':
                csf_list += [base_name]
                csf_count += 1
        if csf_count == 0:  # Если нет сохранённых настроек
            PopupMsgW(self, 'There are no saves!', title='Warning').open()
            return False, ''
        else:
            window = PopupChooseW(self, csf_list, f'Choose a save you want to {cmd_name}', default_value=csf_list[0])
            filename = window.open()
            return True, f'{filename}.txt'

    # Загрузить пользовательские настройки
    def load_custom_settings(self):
        has_saves, filename = self.choose_custom_save('load')
        if not has_saves:
            return
        filepath = os.path.join(CUSTOM_SETTINGS_PATH, filename)

        with open(filepath, 'r') as file:  # Загрузка настроек из файла
            tmp = file.readline().strip()
            if not is_num(tmp):
                tmp = DEFAULT_SETTINGS['count_from']
            self.var_count_from.set(tmp)

            tmp = file.readline().strip()
            if not tmp.isnumeric():
                tmp = DEFAULT_SETTINGS['format']
            self.var_format.set(tmp)

            tmp = file.readline().strip()
            if tmp not in SHOW_UPDATES_MODES:
                tmp = DEFAULT_SETTINGS['show_updates']
            self.var_show_updates.set(str_to_bool(tmp))

            tmp_ = file.readline().strip()
            if tmp_ not in SUPPORT_RU_MODES:
                tmp_ = DEFAULT_SETTINGS['support_ru']
            self.var_support_ru.set(str_to_bool(tmp_))

            tmp = file.readline().strip()
            if tmp_ == DEFAULT_SETTINGS['support_ru']:
                tmp = DEFAULT_SETTINGS['processing_ru']
                self.combo_processing_ru['state'] = 'disabled'
            else:
                self.combo_processing_ru['state'] = 'readonly'
                if tmp not in PROCESSING_RU_MODES:
                    tmp = DEFAULT_SETTINGS['processing_ru']
            self.var_processing_ru.set(tmp)

            tmp = file.readline().strip()
            if tmp not in NAMING_MODES:
                tmp = DEFAULT_SETTINGS['naming_mode']
            self.var_naming_mode.set(tmp)

            tmp = file.readline().strip()
            if tmp not in PRINT_INFO_MODES:
                tmp = DEFAULT_SETTINGS['print_info']
            self.var_print_info.set(tmp)

            tmp = file.readline().strip()
            if tmp not in THEME_MODES:
                tmp = DEFAULT_SETTINGS['theme']
            self.var_style.set(tmp)

            self.var_marker_enc.set( file.readline().strip())
            self.var_marker_dec.set( file.readline().strip())
            self.var_src_dir_enc.set(file.readline().strip())
            self.var_dst_dir_enc.set(file.readline().strip())
            self.var_src_dir_dec.set(file.readline().strip())
            self.var_dst_dir_dec.set(file.readline().strip())

            tmp = file.readline().strip()
            if check_key(tmp)[0] != '+':
                tmp = DEFAULT_SETTINGS['example_key']
            self.var_example_key.set(tmp)

    # Удалить пользовательские настройки
    def remove_custom_settings(self):
        has_saves, filename = self.choose_custom_save('remove')
        if not has_saves:
            return
        custom_settings_file = os.path.join(CUSTOM_SETTINGS_PATH, filename)

        os.remove(custom_settings_file)

    # Сохранить изменения
    def save(self):
        global th

        has_errors = False

        if self.var_count_from.get() in ['', '-']:
            self.entry_count_from.config(style='Error.TEntry')
            has_errors = True
        else:
            self.entry_count_from.config(style='Default.TEntry')

        if self.var_format.get() == '':
            self.entry_format.config(style='Error.TEntry')
            has_errors = True
        else:
            self.entry_format.config(style='Default.TEntry')

        if len(self.var_example_key.get()) != KEY_LEN:
            self.entry_example_key.config(style='Error.TEntry')
            has_errors = True
        else:
            self.entry_example_key.config(style='Default.TEntry')

        if has_errors:
            return

        settings['count_from']    = int(self.var_count_from.get())
        settings['format']        = int(self.var_format.get())
        settings['show_updates']  = bool_to_str(self.var_show_updates.get())
        settings['support_ru']    = bool_to_str(self.var_support_ru.get())
        settings['processing_ru'] = self.var_processing_ru.get()
        settings['naming_mode']   = self.var_naming_mode.get()
        settings['print_info']    = self.var_print_info.get()
        settings['theme']         = self.var_style.get()
        settings['marker_enc']    = self.var_marker_enc.get()
        settings['marker_dec']    = self.var_marker_dec.get()
        settings['src_dir_enc']   = self.var_src_dir_enc.get()
        settings['dst_dir_enc']   = self.var_dst_dir_enc.get()
        settings['src_dir_dec']   = self.var_src_dir_dec.get()
        settings['dst_dir_dec']   = self.var_dst_dir_dec.get()
        settings['example_key']   = self.var_example_key.get()

        th = settings['theme']

        self.configure(bg=ST_BG[th])
        self.parent.configure(bg=ST_BG[th])
        try:
            window_last_version.configure(bg=ST_BG[th])
        except:  # Если окно обновления не открыто
            pass

        self.parent.set_ttk_styles()
        save_settings_to_file()

    # Закрыть окно без сохранения
    def close(self):
        if self.has_changes():  # Если были изменения, то предлагается сохранить их
            window = PopupDialogueW(self, f'If you close the window, the changes will not be saved!\n Close settings?', title='Warning')
            self.wait_window(window)
            answer = window.open()
            if answer:
                self.destroy()
        else:
            self.destroy()

    def open(self):
        self.grab_set()
        self.wait_window()


# Окно режима ручного управления
class ManualW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Media encrypter - MCM')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.mode = ''

        self.var_mult_blocks_h_r = tk.StringVar()  # Множитель блоков по вертикали для красного канала
        self.var_mult_blocks_h_g = tk.StringVar()  # Множитель блоков по вертикали для зелёного канала
        self.var_mult_blocks_h_b = tk.StringVar()  # Множитель блоков по вертикали для синего канала
        self.var_mult_blocks_w_r = tk.StringVar()  # Множитель блоков по горизонтали для красного канала
        self.var_mult_blocks_w_g = tk.StringVar()  # Множитель блоков по горизонтали для зелёного канала
        self.var_mult_blocks_w_b = tk.StringVar()  # Множитель блоков по горизонтали для синего канала
        self.var_shift_h_r = tk.StringVar()  # Сдвиг блоков по вертикали для красного канала
        self.var_shift_h_g = tk.StringVar()  # Сдвиг блоков по вертикали для зелёного канала
        self.var_shift_h_b = tk.StringVar()  # Сдвиг блоков по вертикали для синего канала
        self.var_shift_w_r = tk.StringVar()  # Сдвиг блоков по горизонтали для красного канала
        self.var_shift_w_g = tk.StringVar()  # Сдвиг блоков по горизонтали для зелёного канала
        self.var_shift_w_b = tk.StringVar()  # Сдвиг блоков по горизонтали для синего канала
        self.var_shift_r = tk.StringVar()  # Первичное смещение цвета для красного канала
        self.var_shift_g = tk.StringVar()  # Первичное смещение цвета для зелёного канала
        self.var_shift_b = tk.StringVar()  # Первичное смещение цвета для синего канала
        self.var_mult_r = tk.StringVar()  # Цветовой множитель для красного канала
        self.var_mult_g = tk.StringVar()  # Цветовой множитель для зелёного канала
        self.var_mult_b = tk.StringVar()  # Цветовой множитель для синего канала
        self.var_shift2_r = tk.StringVar()  # Вторичное смещение цвета для красного канала
        self.var_shift2_g = tk.StringVar()  # Вторичное смещение цвета для зелёного канала
        self.var_shift2_b = tk.StringVar()  # Вторичное смещение цвета для синего канала
        self.var_order = tk.StringVar(value='3')  # Порядок следования каналов после перемешивания
        self.var_mult_name = tk.StringVar()  # Сдвиг букв в имени файла

        self.vcmd = (self.register(validate_natural), '%P')

        self.frame_all = ttk.Frame(self,           style='Default.TFrame')
        self.frame_rgb = ttk.Frame(self.frame_all, style='RGB.TFrame')
        self.frame_all.grid(row=0, column=0, columnspan=3, padx=4, pady=4)
        self.frame_rgb.grid(row=0, column=0, columnspan=4, padx=4, pady=4)

        ttk.Label(self.frame_rgb, text='RED', style='Red.TLabel').grid(    row=0, column=1, pady=(4, 1))
        ttk.Label(self.frame_rgb, text='GREEN', style='Green.TLabel').grid(row=0, column=2, pady=(4, 1))
        ttk.Label(self.frame_rgb, text='BLUE', style='Blue.TLabel').grid(  row=0, column=3, pady=(4, 1))

        ttk.Label(self.frame_rgb, text='H multiplier',          style='RGB.TLabel').grid(row=1, column=0, padx=(6, 1), pady=1,      sticky='E')
        ttk.Label(self.frame_rgb, text='W multiplier',          style='RGB.TLabel').grid(row=2, column=0, padx=(6, 1), pady=1,      sticky='E')
        ttk.Label(self.frame_rgb, text='H shift',               style='RGB.TLabel').grid(row=3, column=0, padx=(6, 1), pady=1,      sticky='E')
        ttk.Label(self.frame_rgb, text='W shift',               style='RGB.TLabel').grid(row=4, column=0, padx=(6, 1), pady=1,      sticky='E')
        ttk.Label(self.frame_rgb, text='Primary color shift',   style='RGB.TLabel').grid(row=6, column=0, padx=(6, 1), pady=1,      sticky='E')
        ttk.Label(self.frame_rgb, text='Color multiplier',      style='RGB.TLabel').grid(row=7, column=0, padx=(6, 1), pady=1,      sticky='E')
        ttk.Label(self.frame_rgb, text='Secondary color shift', style='RGB.TLabel').grid(row=8, column=0, padx=(6, 1), pady=(1, 4), sticky='E')

        self.entry_mult_blocks_h_r = ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_mult_blocks_h_r, validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_mult_blocks_h_g = ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_mult_blocks_h_g, validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_mult_blocks_h_b = ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_mult_blocks_h_b, validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_mult_blocks_w_r = ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_mult_blocks_w_r, validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_mult_blocks_w_g = ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_mult_blocks_w_g, validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_mult_blocks_w_b = ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_mult_blocks_w_b, validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_shift_h_r =       ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_shift_h_r,       validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_shift_h_g =       ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_shift_h_g,       validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_shift_h_b =       ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_shift_h_b,       validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_shift_w_r =       ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_shift_w_r,       validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_shift_w_g =       ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_shift_w_g,       validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_shift_w_b =       ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_shift_w_b,       validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_shift_r =         ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_shift_r,         validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_shift_g =         ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_shift_g,         validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_shift_b =         ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_shift_b,         validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_mult_r =          ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_mult_r,          validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_mult_g =          ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_mult_g,          validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_mult_b =          ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_mult_b,          validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_shift2_r =        ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_shift2_r,        validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_shift2_g =        ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_shift2_g,        validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.entry_shift2_b =        ttk.Entry(self.frame_rgb, width=10, textvariable=self.var_shift2_b,        validate='key', validatecommand=self.vcmd, style='Default.TEntry')

        self.entry_mult_blocks_h_r.grid(row=1, column=1, padx=(0, 6), pady=1)
        self.entry_mult_blocks_h_g.grid(row=1, column=2, padx=(0, 6), pady=1)
        self.entry_mult_blocks_h_b.grid(row=1, column=3, padx=(0, 6), pady=1)
        self.entry_mult_blocks_w_r.grid(row=2, column=1, padx=(0, 6), pady=1)
        self.entry_mult_blocks_w_g.grid(row=2, column=2, padx=(0, 6), pady=1)
        self.entry_mult_blocks_w_b.grid(row=2, column=3, padx=(0, 6), pady=1)
        self.entry_shift_h_r.grid(      row=3, column=1, padx=(0, 6), pady=1)
        self.entry_shift_h_g.grid(      row=3, column=2, padx=(0, 6), pady=1)
        self.entry_shift_h_b.grid(      row=3, column=3, padx=(0, 6), pady=1)
        self.entry_shift_w_r.grid(      row=4, column=1, padx=(0, 6), pady=1)
        self.entry_shift_w_g.grid(      row=4, column=2, padx=(0, 6), pady=1)
        self.entry_shift_w_b.grid(      row=4, column=3, padx=(0, 6), pady=1)
        self.entry_shift_r.grid(        row=6, column=1, padx=(0, 6), pady=1)
        self.entry_shift_g.grid(        row=6, column=2, padx=(0, 6), pady=1)
        self.entry_shift_b.grid(        row=6, column=3, padx=(0, 6), pady=1)
        self.entry_mult_r.grid(         row=7, column=1, padx=(0, 6), pady=1)
        self.entry_mult_g.grid(         row=7, column=2, padx=(0, 6), pady=1)
        self.entry_mult_b.grid(         row=7, column=3, padx=(0, 6), pady=1)
        self.entry_shift2_r.grid(       row=8, column=1, padx=(0, 6), pady=(1, 4))
        self.entry_shift2_g.grid(       row=8, column=2, padx=(0, 6), pady=(1, 4))
        self.entry_shift2_b.grid(       row=8, column=3, padx=(0, 6), pady=(1, 4))

        ttk.Label(self.frame_all, text='Multiplier for filenames', style='Default.TLabel').grid(row=1, column=0, padx=(6, 1), pady=(0, 4), sticky='E')
        ttk.Label(self.frame_all, text='Channels order',           style='Default.TLabel').grid(row=1, column=2, padx=(6, 1), pady=(0, 4), sticky='E')

        self.entry_mult_name = ttk.Entry(self.frame_all, width=10, textvariable=self.var_mult_name, validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        self.spin_order = ttk.Spinbox(self.frame_all, width=3, textvariable=self.var_order, values=[str(i) for i in range(6)], state='readonly', validate='key', validatecommand=self.vcmd, style='Default.TSpinbox')

        self.entry_mult_name.grid(row=1, column=1, padx=(0, 6), pady=4, sticky='W')
        self.spin_order.grid(     row=1, column=3, padx=(0, 6), pady=4, sticky='W')

        self.cmd = tk.BooleanVar(value=False)

        self.btn_encode = ttk.Button(self, text='Encode', command=self.pre_encode, takefocus=False, style='Default.TButton')
        self.btn_decode = ttk.Button(self, text='Decode', command=self.pre_decode, takefocus=False, style='Default.TButton')
        self.frame_scan = ttk.Frame(self, style='RGB.TFrame')
        self.btn_encode.grid(row=1, column=0, pady=(0, 4))
        self.btn_decode.grid(row=1, column=1, pady=(0, 4))
        self.frame_scan.grid(row=1, column=2, pady=(0, 4))

        ttk.Label(self.frame_scan, text='Scanning', style='Default.TLabel').grid(row=1, column=2, padx=(4, 1), pady=4)
        self.check_mode = ttk.Checkbutton(self.frame_scan, variable=self.cmd, style='Default.TCheckbutton')
        self.check_mode.grid(row=1, column=3, padx=(0, 4), pady=4)

    # Заполнить ключевые значения
    def set_key_vales(self):
        global mult_blocks_h_r, mult_blocks_h_g, mult_blocks_h_b, mult_blocks_w_r, mult_blocks_w_g, mult_blocks_w_b,\
            shift_h_r, shift_h_g, shift_h_b, shift_w_r, shift_w_g, shift_w_b, shift_r, shift_g, shift_b, mult_r,\
            mult_g, mult_b, shift2_r, shift2_g, shift2_b, order, mult_name

        if self.var_mult_blocks_h_r.get() == '' or\
            self.var_mult_blocks_h_g.get() == '' or\
            self.var_mult_blocks_h_b.get() == '' or\
            self.var_mult_blocks_w_r.get() == '' or\
            self.var_mult_blocks_w_g.get() == '' or\
            self.var_mult_blocks_w_b.get() == '' or\
            self.var_shift_h_r.get() == '' or\
            self.var_shift_h_g.get() == '' or\
            self.var_shift_h_b.get() == '' or\
            self.var_shift_w_r.get() == '' or\
            self.var_shift_w_g.get() == '' or\
            self.var_shift_w_b.get() == '' or\
            self.var_shift_r.get() == '' or\
            self.var_shift_g.get() == '' or\
            self.var_shift_b.get() == '' or\
            self.var_mult_r.get() == '' or\
            self.var_mult_g.get() == '' or\
            self.var_mult_b.get() == '' or\
            self.var_shift2_r.get() == '' or\
            self.var_shift2_g.get() == '' or\
            self.var_shift2_b.get() == '' or\
            self.var_mult_name.get() == '':
            PopupMsgW(self, 'All fields must be filled', title='Warning').open()
            return False

        mult_blocks_h_r = int(self.var_mult_blocks_h_r.get())
        mult_blocks_h_g = int(self.var_mult_blocks_h_g.get())
        mult_blocks_h_b = int(self.var_mult_blocks_h_b.get())
        mult_blocks_w_r = int(self.var_mult_blocks_w_r.get())
        mult_blocks_w_g = int(self.var_mult_blocks_w_g.get())
        mult_blocks_w_b = int(self.var_mult_blocks_w_b.get())
        shift_h_r = int(self.var_shift_h_r.get())
        shift_h_g = int(self.var_shift_h_g.get())
        shift_h_b = int(self.var_shift_h_b.get())
        shift_w_r = int(self.var_shift_w_r.get())
        shift_w_g = int(self.var_shift_w_g.get())
        shift_w_b = int(self.var_shift_w_b.get())
        order = int(self.var_order.get()) % 6
        shift_r = int(self.var_shift_r.get())
        shift_g = int(self.var_shift_g.get())
        shift_b = int(self.var_shift_b.get())
        mult_r = int(self.var_mult_r.get())
        mult_g = int(self.var_mult_g.get())
        mult_b = int(self.var_mult_b.get())
        shift2_r = int(self.var_shift2_r.get())
        shift2_g = int(self.var_shift2_g.get())
        shift2_b = int(self.var_shift2_b.get())
        mult_name = int(self.var_mult_name.get())
        return True

    # Отправить на шифровку
    def pre_encode(self):
        res = self.set_key_vales()
        if not res:
            return
        self.mode = 'E'
        self.destroy()

    # Отправить на дешифровку
    def pre_decode(self):
        res = self.set_key_vales()
        if not res:
            return
        self.mode = 'D'
        self.destroy()

    def open(self):
        self.grab_set()
        self.wait_window()
        if self.cmd:
            return self.mode, 1
        else:
            return self.mode, 2


# Главное окно
class MainW(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(PROGRAM_NAME)
        self.eval('tk::PlaceWindow . center')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.set_ttk_styles()

        self.frame_head = ttk.Frame(self, style='Default.TFrame')
        self.frame_head.grid(row=0, padx=6, pady=4)

        self.lbl_header1 = ttk.Label(self.frame_head, text='Anenokil development presents', style='Header.TLabel')
        self.lbl_header2 = ttk.Label(self.frame_head, text=PROGRAM_NAME, style='Logo.TLabel')
        self.lbl_header1.grid(row=0, padx=7, pady=(7, 0))
        self.lbl_header2.grid(row=1, padx=7, pady=(0, 7))

        self.btn_settings = ttk.Button(self, text='Settings',       command=self.settings, takefocus=False, style='Default.TButton')
        self.btn_encode   = ttk.Button(self, text='Encode',         command=self.encode, takefocus=False,   style='Default.TButton')
        self.btn_decode   = ttk.Button(self, text='Decode',         command=self.decode, takefocus=False,   style='Default.TButton')
        self.btn_mcm      = ttk.Button(self, text='Manual Control', command=self.mcm, takefocus=False,      style='Default.TButton')
        self.btn_close    = ttk.Button(self, text='Close',          command=self.quit, takefocus=False,     style='Default.TButton')
        self.btn_settings.grid(row=2, pady=5)
        self.btn_encode.grid(  row=3, pady=5)
        self.btn_decode.grid(  row=4, pady=5)
        self.btn_mcm.grid(     row=5, pady=5)
        self.btn_close.grid(   row=6, pady=5)

        self.lbl_footer = ttk.Label(self, text=f'{PROGRAM_VERSION}\n'
                                               f'{PROGRAM_DATE}',
                                    justify='center', style='Footer.TLabel')
        self.lbl_footer.grid(row=7, padx=7, pady=(0, 3), sticky='S')

    # Перейти в настройки
    def settings(self):
        SettingsW(self).open()

    # Отправить на шифровку
    def encode(self):
        window = EnterKeyW(self, 'Encode')
        has_key, key, cmd = window.open()
        if not has_key:
            return

        global fn_symbols, fn_symbols_num
        if settings['support_ru'] == 'no':
            fn_symbols = FN_SYMBOLS_WITHOUT_RU
            fn_symbols_num = FN_SYMBOLS_WITHOUT_RU_NUM
        else:
            fn_symbols = FN_SYMBOLS_WITH_RU
            fn_symbols_num = FN_SYMBOLS_WITH_RU_NUM

        global process_status
        process_status = 'work'

        self.logger = LoggerW(self)
        t1 = Thread(target=self.logger.open)
        t1.start()

        extract_key_values(key_to_bites(key))
        t2 = Thread(target=encode, args=[cmd])
        t2.start()

    # Отправить на дешифровку
    def decode(self):
        window = EnterKeyW(self, 'Decode')
        has_key, key, cmd = window.open()
        if not has_key:
            return

        global fn_symbols, fn_symbols_num
        if settings['support_ru'] == 'no':
            fn_symbols = FN_SYMBOLS_WITHOUT_RU
            fn_symbols_num = FN_SYMBOLS_WITHOUT_RU_NUM
        else:
            fn_symbols = FN_SYMBOLS_WITH_RU
            fn_symbols_num = FN_SYMBOLS_WITH_RU_NUM

        global process_status
        process_status = 'work'

        self.logger = LoggerW(self)
        t1 = Thread(target=self.logger.open)
        t1.start()

        extract_key_values(key_to_bites(key))
        t2 = Thread(target=decode, args=[cmd])
        t2.start()

    # Перейти в режим ручного управления
    def mcm(self):
        window = ManualW(self)
        action, cmd = window.open()

        global fn_symbols, fn_symbols_num
        if settings['support_ru'] == 'no':
            fn_symbols = FN_SYMBOLS_WITHOUT_RU
            fn_symbols_num = FN_SYMBOLS_WITHOUT_RU_NUM
        else:
            fn_symbols = FN_SYMBOLS_WITH_RU
            fn_symbols_num = FN_SYMBOLS_WITH_RU_NUM

        if action in ['E', 'D']:
            global process_status
            process_status = 'work'
            self.logger = LoggerW(self)
            t1 = Thread(target=self.logger.open)
            t1.start()
            if action == 'E':
                t2 = Thread(target=encode, args=[cmd])
            else:
                t2 = Thread(target=decode, args=[cmd])
            t2.start()

    # Установить ttk-стили
    def set_ttk_styles(self):
        # Стиль label "default"
        self.st_lbl_default = ttk.Style()
        self.st_lbl_default.theme_use('alt')
        self.st_lbl_default.configure('Default.TLabel',
                                      font=('StdFont', 10),
                                      background=ST_BG[th],
                                      foreground=ST_FG[th])

        # Стиль label "header"
        self.st_lbl_header = ttk.Style()
        self.st_lbl_header.theme_use('alt')
        self.st_lbl_header.configure('Header.TLabel',
                                     font=('StdFont', 15),
                                     background=ST_BG[th],
                                     foreground=ST_FG[th])

        # Стиль label "logo"
        self.st_lbl_logo = ttk.Style()
        self.st_lbl_logo.theme_use('alt')
        self.st_lbl_logo.configure('Logo.TLabel',
                                   font=('Times', 21),
                                   background=ST_BG[th],
                                   foreground=ST_FG_LOGO[th])

        # Стиль label "footer"
        self.st_lbl_footer = ttk.Style()
        self.st_lbl_footer.theme_use('alt')
        self.st_lbl_footer.configure('Footer.TLabel',
                                     font=('StdFont', 8),
                                     background=ST_BG[th],
                                     foreground=ST_FG_FOOTER[th])

        # Стиль label "rgb"
        self.st_lbl_rgb = ttk.Style()
        self.st_lbl_rgb.theme_use('alt')
        self.st_lbl_rgb.configure('RGB.TLabel',
                                  font=('StdFont', 10),
                                  background=ST_BG_RGB[th],
                                  foreground=ST_FG[th])

        # Стиль label "red"
        self.st_lbl_red = ttk.Style()
        self.st_lbl_red.theme_use('alt')
        self.st_lbl_red.configure('Red.TLabel',
                                  font=('StdFont', 10),
                                  background=ST_BG_RGB[th],
                                  foreground='#FF0000')

        # Стиль label "green"
        self.st_lbl_green = ttk.Style()
        self.st_lbl_green.theme_use('alt')
        self.st_lbl_green.configure('Green.TLabel',
                                    font=('StdFont', 10),
                                    background=ST_BG_RGB[th],
                                    foreground='#00FF00')

        # Стиль label "blue"
        self.st_lbl_blue = ttk.Style()
        self.st_lbl_blue.theme_use('alt')
        self.st_lbl_blue.configure('Blue.TLabel',
                                   font=('StdFont', 10),
                                   background=ST_BG_RGB[th],
                                   foreground='#0000FF')

        # Стиль entry "default"
        self.st_entry_default = ttk.Style()
        self.st_entry_default.theme_use('alt')
        self.st_entry_default.configure('Default.TEntry',
                                        font=('StdFont', 10))
        self.st_entry_default.map('Default.TEntry',
                                  fieldbackground=[('readonly', ST_BG[th]),
                                                   ('!readonly', ST_BG_FIELDS[th])],
                                  foreground=[('readonly', ST_FG[th]),
                                              ('!readonly', ST_FG[th])],
                                  selectbackground=[('readonly', ST_SELECT[th]),
                                                    ('!readonly', ST_SELECT[th])],
                                  selectforeground=[('readonly', ST_FG[th]),
                                                    ('!readonly', ST_FG[th])])

        # Стиль entry "error"
        self.st_entry_error = ttk.Style()
        self.st_entry_error.theme_use('alt')
        self.st_entry_error.configure('Error.TEntry',
                                      font=('StdFont', 10))
        self.st_entry_error.map('Error.TEntry',
                                fieldbackground=[('readonly', ST_BG_ERR[th]),
                                                 ('!readonly', ST_BG_ERR[th])],
                                foreground=[('readonly', ST_FG[th]),
                                            ('!readonly', ST_FG[th])],
                                selectbackground=[('readonly', ST_SELECT[th]),
                                                  ('!readonly', ST_SELECT[th])],
                                selectforeground=[('readonly', ST_FG[th]),
                                                  ('!readonly', ST_FG[th])])

        # Стиль entry "key"
        self.st_entry_key = ttk.Style()
        self.st_entry_key.theme_use('alt')
        self.st_entry_key.configure('Key.TEntry',
                                    font='TkFixedFont')
        self.st_entry_key.map('Key.TEntry',
                              fieldbackground=[('readonly', ST_BG[th]),
                                               ('!readonly', ST_BG_FIELDS[th])],
                              foreground=[('readonly', ST_FG_KEY[th]),
                                          ('!readonly', ST_FG_KEY[th])],
                              selectbackground=[('readonly', ST_SELECT[th]),
                                                ('!readonly', ST_SELECT[th])],
                              selectforeground=[('readonly', ST_FG_KEY[th]),
                                                ('!readonly', ST_FG_KEY[th])])

        # Стиль button "default"
        self.st_btn_default = ttk.Style()
        self.st_btn_default.theme_use('alt')
        self.st_btn_default.configure('Default.TButton',
                                      font=('StdFont', 12),
                                      borderwidth=1)
        self.st_btn_default.map('Default.TButton',
                                relief=[('pressed', 'sunken'),
                                        ('active', 'flat'),
                                        ('!active', 'raised')],
                                background=[('pressed', ST_BTN_SELECT[th]),
                                            ('active', ST_BTN[th]),
                                            ('!active', ST_BTN[th])],
                                foreground=[('pressed', ST_FG[th]),
                                            ('active', ST_FG[th]),
                                            ('!active', ST_FG[th])])

        # Стиль button "disabled" (для выключенных "default")
        self.st_btn_disabled = ttk.Style()
        self.st_btn_disabled.theme_use('alt')
        self.st_btn_disabled.configure('Disabled.TButton',
                                       font=('StdFont', 12),
                                       borderwidth=1)
        self.st_btn_disabled.map('Disabled.TButton',
                                 relief=[('active', 'raised'),
                                         ('!active', 'raised')],
                                 background=[('active', ST_BG[th]),
                                             ('!active', ST_BG[th])],
                                 foreground=[('active', ST_FG[th]),
                                             ('!active', ST_FG[th])])

        # Стиль button "yes"
        self.st_btn_yes = ttk.Style()
        self.st_btn_yes.theme_use('alt')
        self.st_btn_yes.configure('Yes.TButton',
                                  font=('StdFont', 12),
                                  borderwidth=1)
        self.st_btn_yes.map('Yes.TButton',
                            relief=[('pressed', 'sunken'),
                                    ('active', 'flat'),
                                    ('!active', 'raised')],
                            background=[('pressed', ST_BTN_Y_SELECT[th]),
                                        ('active', ST_BTN_Y[th]),
                                        ('!active', ST_BTN_Y[th])],
                            foreground=[('pressed', ST_FG[th]),
                                        ('active', ST_FG[th]),
                                        ('!active', ST_FG[th])])

        # Стиль button "no"
        self.st_btn_no = ttk.Style()
        self.st_btn_no.theme_use('alt')
        self.st_btn_no.configure('No.TButton',
                                 font=('StdFont', 12),
                                 borderwidth=1)
        self.st_btn_no.map('No.TButton',
                           relief=[('pressed', 'sunken'),
                                   ('active', 'flat'),
                                   ('!active', 'raised')],
                           background=[('pressed', ST_BTN_N_SELECT[th]),
                                       ('active', ST_BTN_N[th]),
                                       ('!active', ST_BTN_N[th])],
                           foreground=[('pressed', ST_FG[th]),
                                       ('active', ST_FG[th]),
                                       ('!active', ST_FG[th])])

        # Стиль button "image"
        self.st_btn_image = ttk.Style()
        self.st_btn_image.theme_use('alt')
        self.st_btn_image.configure('Image.TButton',
                                    font=('StdFont', 12),
                                    borderwidth=0)
        self.st_btn_image.map('Image.TButton',
                              relief=[('pressed', 'flat'),
                                      ('active', 'flat'),
                                      ('!active', 'flat')],
                              background=[('pressed', ST_BTN_SELECT[th]),
                                          ('active', ST_BTN_SELECT[th]),
                                          ('!active', ST_BG[th])],
                              foreground=[('pressed', ST_FG[th]),
                                          ('active', ST_FG[th]),
                                          ('!active', ST_FG[th])])

        # Стиль checkbutton "default"
        self.st_check = ttk.Style()
        self.st_check.theme_use('alt')
        self.st_check.map('Default.TCheckbutton',
                          background=[('active', ST_SELECT[th]),
                                      ('!active', ST_BG[th])])

        # Стиль combobox "default"
        self.st_combo_default = ttk.Style()
        self.st_combo_default.theme_use('alt')
        self.st_combo_default.configure('Default.TCombobox',
                                        font=('StdFont', 10))
        self.st_combo_default.map('Default.TCombobox',
                                  background=[('readonly', ST_BTN[th]),
                                              ('!readonly', ST_BTN[th])],
                                  fieldbackground=[('readonly', ST_BG_FIELDS[th]),
                                                   ('!readonly', ST_BG_FIELDS[th])],
                                  selectbackground=[('readonly', ST_BG_FIELDS[th]),
                                                    ('!readonly', ST_BG_FIELDS[th])],
                                  highlightbackground=[('readonly', ST_BORDER[th]),
                                                       ('!readonly', ST_BORDER[th])],
                                  foreground=[('readonly', ST_FG[th]),
                                              ('!readonly', ST_FG[th])],
                                  selectforeground=[('readonly', ST_FG[th]),
                                            ('!readonly', ST_FG[th])])

        # Стиль всплывающего списка combobox
        self.option_add('*TCombobox*Listbox*Font', ('StdFont', 10))
        self.option_add('*TCombobox*Listbox*Background', ST_BG_FIELDS[th])
        self.option_add('*TCombobox*Listbox*Foreground', ST_FG[th])
        self.option_add('*TCombobox*Listbox*selectBackground', ST_SELECT[th])
        self.option_add('*TCombobox*Listbox*selectForeground', ST_FG[th])

        # Стиль scrollbar "vertical"
        self.st_vscroll = ttk.Style()
        self.st_vscroll.theme_use('alt')
        self.st_vscroll.map('Vertical.TScrollbar',
                            troughcolor=[('disabled', ST_BG[th]),
                                         ('pressed', ST_BG[th]),
                                         ('!pressed', ST_BG[th])],
                            background=[('disabled', ST_BTN[th]),
                                        ('pressed', ST_BTN[th]),
                                        ('!pressed', ST_BTN[th])])

        # Стиль frame "default"
        self.st_frame_default = ttk.Style()
        self.st_frame_default.theme_use('alt')
        self.st_frame_default.configure('Default.TFrame',
                                        borderwidth=1,
                                        relief=ST_RELIEF[th],
                                        background=ST_BG[th],
                                        bordercolor=ST_BORDER[th])

        # Стиль frame "rgb"
        self.st_frame_rgb = ttk.Style()
        self.st_frame_rgb.theme_use('alt')
        self.st_frame_rgb.configure('RGB.TFrame',
                                    borderwidth=1,
                                    relief=ST_RELIEF[th],
                                    background=ST_BG_RGB[th],
                                    bordercolor=ST_BORDER[th])

        # Стиль frame "invis"
        self.st_frame_invis = ttk.Style()
        self.st_frame_invis.theme_use('alt')
        self.st_frame_invis.configure('Invis.TFrame',
                                      borderwidth=0,
                                      relief=ST_RELIEF[th],
                                      background=ST_BG[th])

        # Стиль progressbar "default"
        self.st_progress_default = ttk.Style()
        self.st_progress_default.theme_use('alt')
        self.st_progress_default.configure('Default.Horizontal.TProgressbar',
                                           troughcolor=ST_BG_FIELDS[th],
                                           background=ST_PROG[th])

        # Стиль progressbar "aborted"
        self.st_progress_aborted = ttk.Style()
        self.st_progress_aborted.theme_use('alt')
        self.st_progress_aborted.configure('Aborted.Horizontal.TProgressbar',
                                           troughcolor=ST_BG_FIELDS[th],
                                           background=ST_PROG_ABORT[th])

        # Стиль progressbar "done"
        self.st_progress_done = ttk.Style()
        self.st_progress_done.theme_use('alt')
        self.st_progress_done.configure('Done.Horizontal.TProgressbar',
                                        troughcolor=ST_BG_FIELDS[th],
                                        background=ST_PROG_DONE[th])

        # Стиль spinbox "default"
        self.st_spin_default = ttk.Style()
        self.st_spin_default.theme_use('alt')
        self.st_spin_default.configure('Default.TSpinbox',
                                       font=('StdFont', 10))
        self.st_spin_default.map('Default.TSpinbox',
                                 background=[('readonly', ST_BTN[th]),
                                             ('!readonly', ST_BTN[th])],
                                 fieldbackground=[('readonly', ST_BG_FIELDS[th]),
                                                  ('!readonly', ST_BG_FIELDS[th])],
                                 selectbackground=[('readonly', ST_BG_FIELDS[th]),
                                                   ('!readonly', ST_BG_FIELDS[th])],
                                 highlightbackground=[('readonly', ST_BORDER[th]),
                                                      ('!readonly', ST_BORDER[th])],
                                 foreground=[('readonly', ST_FG[th]),
                                             ('!readonly', ST_FG[th])],
                                 selectforeground=[('readonly', ST_FG[th]),
                                                   ('!readonly', ST_FG[th])])


# Вывод информации о программе
print(f'======================================================================================\n')
print(f'                            {Fore.RED}Anenokil development{Style.RESET_ALL}  presents')
print(f'                            ' + (30 - len(PROGRAM_NAME) - len(PROGRAM_VERSION) - 2) // 2 * ' ' + f'{Fore.MAGENTA}{PROGRAM_NAME}{Style.RESET_ALL}  {PROGRAM_VERSION}')
print(f'                            ' + (30 - len(PROGRAM_DATE)) // 2 * ' ' + PROGRAM_DATE + '\n')
print(f'======================================================================================')

upload_themes(THEMES)  # Загружаем темы

try:
    load_settings(SETTINGS_PATH)
except FileNotFoundError:  # Если файл с настройками отсутствует, то устанавливаются настройки по умолчанию
    set_default_settings()

th = settings['theme']

gui = MainW()
window_last_version = check_updates(gui, str_to_bool(settings['show_updates']))  # Проверка наличия обновлений
gui.mainloop()

# v1.0.0
# v2.0.0 - добавлены настройки
# v3.0.0 - добавлена обработка гифок
# v4.0.0 - добавлена обработка видео
# v5.0.0 - добавлена обработка вложенных папок
# v6.0.0 - добавлен графический интерфейс
# v7.0.0 - добавлены журнал, загрузка обновлений и пользовательские темы

# заменить abort на pause
# добавить выбор расширений
# добавить варианты фпс
# - больше картинок
# - всплывающие подсказки
# цвета в журнале
# показывать общее время выполнения
# is closed
