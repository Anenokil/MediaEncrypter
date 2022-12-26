import os
from skimage.io import imread, imsave
from numpy import dstack, uint8, arange
from math import gcd  # НОД
from transliterate import translit  # Транслитерация
from shutil import copyfile  # Копирование файлов
from PIL import Image  # Разбиение gif-изображений на кадры
import imageio.v2 as io  # Составление gif-изображений из кадров
from moviepy.editor import VideoFileClip  # Разбиение видео на кадры
import cv2  # Составление видео из кадров
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory
import time

PROGRAM_NAME = 'Media encrypter v6.0.0_PRE-8'
PROGRAM_DATE = '27.12.2022  1:05'

NORMAL_COLOR = '#FFFFFF'
ERROR_COLOR = '#DD4444'

""" Пути """
RESOURCES_DIR = 'resources'  # Главная папка с ресурсами
TMP_FILE = 'tmp.png'  # Временный файл для обработки gif-изображений и видео
TMP_PATH = os.path.join(RESOURCES_DIR, TMP_FILE)
SETTINGS_PATH = os.path.join(RESOURCES_DIR, 'settings.txt')  # Файл с настройками
CUSTOM_SETTINGS_DIR = os.path.join(RESOURCES_DIR, 'custom_settings')  # Папка с сохранёнными пользовательскими настройками

FN_SYMBOLS = "#' 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@$%^&()[]{}-=_+`~;,."\
             "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"  # Допустимые в названии файлов символы (Windows)
FN_SYMB_NUM = len(FN_SYMBOLS)  # Количество допустимых символов

""" Настройки """
SETTINGS_NUM = 12  # Количество настроек

# Значения настроек по умолчанию
settings = {}

NAMING_MODE_DEF = '0'
COUNT_FROM_DEF = '1'
FORMAT_DEF = '1'
MARKER_ENC_DEF = '_ENC_'
MARKER_DEC_DEF = '_DEC_'
RU_LETTERS_DEF = '0'
DIR_ENC_FROM_DEF = 'f_src'
DIR_ENC_TO_DEF = 'f_enc'
DIR_DEC_FROM_DEF = 'f_enc'
DIR_DEC_TO_DEF = 'f_dec'
EXAMPLE_KEY_DEF = '_123456789_123456789_123456789_123456789'
PRINT_INFO_DEF = '0'

SETTINGS_NAMES = ['naming_mode', 'count_from', 'format', 'marker_enc', 'marker_dec', 'ru_letters',
                  'dir_enc_from', 'dir_enc_to', 'dir_dec_from', 'dir_dec_to', 'example_key', 'print_info']

# Варианты настроек с перечислимым типом
NAMING_MODES = ['encryption', 'numeration', 'add prefix', 'add postfix', 'don`t change']  # Варианты настройки именования выходных файлов
RU_LETTERS_MODES = ['transliterate to latin', 'don`t change']  # Варианты настройки обработки кириллических букв
PRINT_INFO_MODES = ['don`t print', 'print']  # Варианты настройки печати информации

""" Ключ """
KEY_SYMBOLS = '0123456789-abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ'  # Допустимые в ключе символы
KEY_LEN = 40  # Длина ключа


""" Общие функции """


# Вывод предупреждения в консоль
def print_warn(text):
    print(f'[!!!] {text} [!!!]')


# Является ли строка целым числом
def is_num(line):
    return line.isnumeric() or (len(line) > 1 and line[0] == '-' and line[1:].isnumeric())


# Проверка ключа на корректность
def check_key(key):
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
    settings['naming_mode'] = NAMING_MODE_DEF
    settings['count_from'] = COUNT_FROM_DEF
    settings['format'] = FORMAT_DEF
    settings['marker_enc'] = MARKER_ENC_DEF
    settings['marker_dec'] = MARKER_DEC_DEF
    settings['ru_letters'] = RU_LETTERS_DEF
    settings['dir_enc_from'] = DIR_ENC_FROM_DEF
    settings['dir_enc_to'] = DIR_ENC_TO_DEF
    settings['dir_dec_from'] = DIR_DEC_FROM_DEF
    settings['dir_dec_to'] = DIR_DEC_TO_DEF
    settings['example_key'] = EXAMPLE_KEY_DEF
    settings['print_info'] = PRINT_INFO_DEF


# Загрузка настроек из файла
def load_settings(filename):
    with open(filename, 'r') as file:  # Загрузка настроек из файла
        for name in SETTINGS_NAMES:
            settings[name] = file.readline().strip()


# Проверка и исправление настроек
def correct_settings():
    if settings['naming_mode'] not in ['0', '1', '2', '3', '4']:
        settings['naming_mode'] = NAMING_MODE_DEF
    if not is_num(settings['count_from']):
        settings['count_from'] = COUNT_FROM_DEF
    if not settings['format'].isnumeric():
        settings['format'] = FORMAT_DEF
    if settings['ru_letters'] not in ['0', '1']:
        settings['ru_letters'] = RU_LETTERS_DEF
    if check_key(settings['example_key']) != '+':
        settings['example_key'] = EXAMPLE_KEY_DEF
    if settings['print_info'] not in ['0', '1']:
        settings['print_info'] = PRINT_INFO_DEF


# Сохранить настройки в файл
def save_settings_to_file(filename=SETTINGS_PATH):
    with open(filename, 'w') as file:  # Запись исправленных настроек в файл
        file.write(
            settings['naming_mode'] + '\n' + settings['count_from'] + '\n' + settings['format'] + '\n' +
            settings['marker_enc'] + '\n' + settings['marker_dec'] + '\n' + settings['ru_letters'] + '\n' +
            settings['dir_enc_from'] + '\n' + settings['dir_enc_to'] + '\n' + settings['dir_dec_from'] + '\n' +
            settings['dir_dec_to'] + '\n' + settings['example_key'] + '\n' + settings['print_info'])


# Преобразование ключа в массив битов (каждый символ - в 6 битов)
def key_to_bites(key):
    bits = [[0] * KEY_LEN for _ in range(6)]
    for i in range(KEY_LEN):
        symbol = KEY_SYMBOLS.find(key[i])
        for j in range(6):
            bits[j][i] = symbol // (2 ** j) % 2
    return bits


# Нахождение числа по его битам
def bites_sum(*bites):
    res = 0
    for i in bites:
        if type(i) == list:  # Можно передавать массивы
            for j in i:
                res = 2 * res + j
        else:  # А можно числа
            res = 2 * res + i
    return res


# Извлечение ключевых значений
def extract_key_values(b):
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
    mult_name = bites_sum(b[0][39], b[1][38:40], b[2][36], b[3][0:2], b[4][4:6], b[5][3]) % (FN_SYMB_NUM - 1) + 1  # Сдвиг букв в имени файла

    if settings['print_info'] == '1':  # Вывод ключевых значений
        print('                                    KEY  CONSTANTS')
        print(f'  ML BH: {mult_blocks_h_r}, {mult_blocks_h_g}, {mult_blocks_h_b}')
        print(f'  ML BW: {mult_blocks_w_r}, {mult_blocks_w_g}, {mult_blocks_w_b}')
        print(f'  SH  H: {shift_h_r}, {shift_h_g}, {shift_h_b}')
        print(f'  SH  W: {shift_w_r}, {shift_w_g}, {shift_w_b}')
        print(f'  ORDER: {order}')
        print(f'  SH1 C: {shift_r}, {shift_g}, {shift_b}')
        print(f'  ML  C: {mult_r}, {mult_g}, {mult_b}')
        print(f'  SH2 C: {shift2_r}, {shift2_g}, {shift2_b}')
        print(f'  ML  N: {mult_name}')


""" Алгоритм шифровки/дешифровки """


# Разделение полотна на блоки и их перемешивание
def mix_blocks(img, mult_h, mult_w, shift_h, shift_w):
    h = img.shape[0]  # Высота изображения
    w = img.shape[1]  # Ширина изображения

    # Нахождение наименьшего числа, взаимно-простого с h, большего чем mult_h, дающего при делении на h в остатке 1
    while gcd(mult_h, h) != 1 or mult_h % h == 1:
        mult_h += 1
    # Нахождение наименьшего числа, взаимно-простого с w, большего чем mult_w, дающего при делении на w в остатке 1
    while gcd(mult_w, w) != 1 or mult_w % w == 1:
        mult_w += 1

    if settings['print_info'] == '1':
        print(f'{h}x{w}: {mult_h} {mult_w}')

    img_tmp = img.copy()
    for i in range(h):
        for j in range(w):
            jj = (j + shift_w * i) % w
            ii = (i + shift_h * jj) % h
            iii = (ii * mult_h) % h
            jjj = (jj * mult_w) % w
            img[iii][jjj] = img_tmp[i][j]


# Шифровка файла
def encode_file(img):
    # Разделение изображения на RGB-каналы
    if len(img.shape) < 3:  # Если в изображении меньше трёх каналов
        red, green, blue = img.copy(), img.copy(), img.copy()
    else:
        red, green, blue = [img[:, :, i].copy() for i in range(3)]

    # Перемешивание блоков для каждого канала
    mix_blocks(red,   mult_blocks_h_r, mult_blocks_w_r, shift_h_r, shift_w_r)
    mix_blocks(green, mult_blocks_h_g, mult_blocks_w_g, shift_h_g, shift_w_g)
    mix_blocks(blue,  mult_blocks_h_b, mult_blocks_w_b, shift_h_b, shift_w_b)

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
def recover_blocks_calc(h, w, mult_h, mult_w):
    # Нахождение наименьшего числа, взаимно-простого с h, большего чем mult_h, дающего при делении на h в остатке 1
    while gcd(mult_h, h) != 1 or mult_h % h == 1:
        mult_h += 1
    # Нахождение наименьшего числа, взаимно-простого с w, большего чем mult_w, дающего при делении на w в остатке 1
    while gcd(mult_w, w) != 1 or mult_w % w == 1:
        mult_w += 1

    if settings['print_info'] == '1':
        print(f'{h}x{w}: {mult_h} {mult_w}')

    dec_h = [0] * h  # Составление массива обратных сдвигов по вертикали
    for i in range(h):
        dec_h[(i * mult_h) % h] = i
    dec_w = [0] * w  # Составление массива обратных сдвигов по горизонтали
    for i in range(w):
        dec_w[(i * mult_w) % w] = i

    return dec_h, dec_w


# Разделение полотна на блоки и восстановление из них исходного изображения
def recover_blocks(img, h, w, shift_h, shift_w, dec_h, dec_w):
    img_tmp = img.copy()
    for i in range(h):
        for j in range(w):
            ii = dec_h[i]
            jj = dec_w[j]
            iii = (ii + (h - shift_h) * jj) % h
            jjj = (jj + (w - shift_w) * iii) % w
            img[iii][jjj] = img_tmp[i][j]


# Вычисление параметров для decode_file
def decode_file_calc(img):
    h = img.shape[0]  # Высота изображения
    w = img.shape[1]  # Ширина изображения

    dec_h_r, dec_w_r = recover_blocks_calc(h, w, mult_blocks_h_r, mult_blocks_w_r)  # Массивы обратных сдвигов для красного канала
    dec_h_g, dec_w_g = recover_blocks_calc(h, w, mult_blocks_h_g, mult_blocks_w_g)  # Массивы обратных сдвигов для зелёного канала
    dec_h_b, dec_w_b = recover_blocks_calc(h, w, mult_blocks_h_b, mult_blocks_w_b)  # Массивы обратных сдвигов для синего канала

    return h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b


# Дешифровка файла
def decode_file(img, h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b):
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
def encode_filename(name):
    if settings['ru_letters'] == '0':  # Транслитерация кириллицы
        name = translit(name, language_code='ru', reversed=True)

    # Нахождение наименьшего числа, взаимно-простого с FN_SYMB_NUM, большего чем mult_name + len(name)
    mn = mult_name + len(name)
    while gcd(mn, FN_SYMB_NUM) != 1:
        mn += 1

    new_name = ''
    for letter in name:  # Шифровка
        letter = FN_SYMBOLS[(FN_SYMBOLS.find(letter) + 3) * mn % FN_SYMB_NUM]
        new_name = letter + new_name
    new_name = f'_{new_name}_'  # Защита от потери крайних пробелов
    return new_name


# Дешифровка имени файла
def decode_filename(name):
    name = name[1:-1]  # Защита от потери крайних пробелов

    # Нахождение наименьшего числа, взаимно-простого с FN_SYMB_NUM, большего чем mult_name + len(name)
    mn = mult_name + len(name)
    while gcd(mn, FN_SYMB_NUM) != 1:
        mn += 1

    arr = [0] * FN_SYMB_NUM  # Дешифровочный массив
    for i in range(FN_SYMB_NUM):
        arr[(i + 3) * mn % FN_SYMB_NUM] = i

    new_name = ''
    for letter in name:  # Дешифровка
        letter = FN_SYMBOLS[arr[FN_SYMBOLS.find(letter)]]
        new_name = letter + new_name

    if settings['ru_letters'] == '0':  # Транслитерация кириллицы
        new_name = translit(new_name, language_code='ru', reversed=True)

    return new_name


# Преобразование имени файла
def filename_processing(op_mode, naming_mode, base_name, ext, outp_dir, marker, count_correct):
    if op_mode == 'E':  # При шифровке
        count_same = 1  # Счётчик файлов с таким же именем
        counter = ''
        while True:
            if naming_mode == '0':
                new_name = encode_filename(base_name + counter)
            elif naming_mode == '1':
                new_name = ('{:0' + settings['format'] + '}').format(count_correct) + counter
            elif naming_mode == '2':
                new_name = marker + base_name + counter
            elif naming_mode == '3':
                new_name = base_name + marker + counter
            else:
                new_name = base_name + counter
            new_name += ext

            if new_name not in os.listdir(outp_dir):  # Если нет файлов с таким же именем, то завершаем цикл
                break
            count_same += 1
            counter = ' [' + str(count_same) + ']'  # Если уже есть файл с таким именем, то добавляется индекс
    else:  # При дешифровке
        if naming_mode == '0':
            new_name = decode_filename(base_name)
        elif naming_mode == '1':
            new_name = ('{:0' + settings['format'] + '}').format(count_correct)
        elif naming_mode == '2':
            new_name = marker + base_name
        elif naming_mode == '3':
            new_name = base_name + marker
        else:
            new_name = base_name

        count_same = 1  # Счётчик файлов с таким же именем
        temp_name = new_name + ext
        while temp_name in os.listdir(outp_dir):  # Если уже есть файл с таким именем, то добавляется индекс
            count_same += 1
            temp_name = f'{new_name} [{count_same}]{ext}'
        new_name = temp_name
    return new_name


# Обработка папки с файлами
def encrypt_dir(op_mode, marker, formats, inp_dir, outp_dir, count_all):
    count_correct = int(settings['count_from']) - 1  # Счётчик количества обработанных файлов
    for filename in os.listdir(inp_dir):  # Проход по файлам
        base_name, ext = os.path.splitext(filename)
        count_all += 1

        pth = os.path.join(inp_dir, filename)
        isdir = os.path.isdir(pth)
        if ext.lower() not in formats and not isdir:  # Проверка формата
            print(f'({count_all}) <{filename}>')
            print_warn('Unsupported file extension')
            print()
            continue
        count_correct += 1

        start = time.perf_counter()
        if ext in ['.png', '.jpg', '.jpeg', '.bmp']:
            res_name = filename_processing(op_mode, settings['naming_mode'], base_name, '.png', outp_dir, marker, count_correct)  # Преобразование имени файла

            print(f'({count_all}) <{filename}>  ->  <{res_name}>')  # Вывод информации

            img = imread(os.path.join(inp_dir, filename))  # Считывание изображения
            if settings['print_info'] == '1':
                print(img.shape)

            outp_path = os.path.join(outp_dir, res_name)
            if op_mode == 'E':  # Запись результата
                imsave(outp_path, encode_file(img).astype(uint8))
            else:
                h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b = decode_file_calc(img)
                img = decode_file(img, h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b)
                imsave(outp_path, img.astype(uint8))
            print()
        elif ext == '.gif':
            res_name = filename_processing(op_mode, settings['naming_mode'], base_name, '', outp_dir, marker, count_correct)  # Преобразование имени файла

            print(f'({count_all}) <{filename}>  ->  <{res_name}>')  # Вывод информации

            res = os.path.join(outp_dir, res_name)
            if res_name not in os.listdir(outp_dir):
                os.mkdir(res)
            open(os.path.join(res, '_gif'), 'w')

            with Image.open(os.path.join(inp_dir, filename)) as im:
                for i in range(im.n_frames):
                    print(f'frame {i + 1}')
                    im.seek(i)
                    im.save(TMP_PATH)

                    fr = imread(TMP_PATH)
                    if settings['print_info'] == '1':  # Вывод информации о считывании
                        print(fr.shape)
                    outp_path = os.path.join(res, '{:05}.png'.format(i))
                    imsave(outp_path, encode_file(fr).astype(uint8))
                    print()
                imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
                os.remove(TMP_PATH)
        elif isdir and '_gif' in os.listdir(pth) and op_mode == 'D':
            res_name = filename_processing(op_mode, settings['naming_mode'], filename, '.gif', outp_dir, marker, count_correct)  # Преобразование имени файла

            print(f'({count_all}) <{filename}>  ->  <{res_name}>')  # Вывод информации

            inp_dir_tmp = os.path.join(inp_dir, filename)
            frames = sorted((fr for fr in os.listdir(inp_dir_tmp) if fr.endswith('.png')))
            res = os.path.join(outp_dir, res_name)

            img = imread(os.path.join(inp_dir_tmp, frames[0]))
            h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b = decode_file_calc(img)

            with io.get_writer(res, mode='I', duration=1/24) as writer:
                for i in range(len(frames)):
                    print(f'frame {i + 1}')
                    fr = imread(os.path.join(inp_dir_tmp, frames[i]))
                    if settings['print_info'] == '1':  # Вывод информации о считывании
                        print(fr.shape)
                    img = decode_file(fr, h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b)
                    imsave(TMP_PATH, img.astype(uint8))
                    writer.append_data(io.imread(TMP_PATH))
                    print()
                imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
                os.remove(TMP_PATH)
            writer.close()
        elif ext in ['.avi', '.mp4', '.webm']:
            tmp_name = filename_processing(op_mode, '1', base_name, '', outp_dir, marker, count_correct)  # Преобразование имени файла (cv2 не воспринимает русские буквы, поэтому приходится использовать временное имя)
            res_name = filename_processing(op_mode, settings['naming_mode'], base_name, '', outp_dir, marker, count_correct)

            print(f'({count_all}) <{filename}>  ->  <{res_name}>')  # Вывод информации

            res = os.path.join(outp_dir, tmp_name)
            if tmp_name not in os.listdir(outp_dir):
                os.mkdir(res)
            open(os.path.join(res, '_vid'), 'w')

            vid = VideoFileClip(os.path.join(inp_dir, filename))
            fps = min(vid.fps, 24)
            step = 1 / fps
            count = 0
            for current_duration in arange(0, vid.duration, step):
                frame_filename = os.path.join(res, '{:06}.png'.format(count))
                vid.save_frame(TMP_PATH, current_duration)
                print(f'frame {count + 1}')

                fr = imread(TMP_PATH)
                if settings['print_info'] == '1':  # Вывод информации о считывании
                    print(fr.shape)
                imsave(frame_filename, encode_file(fr).astype(uint8))
                count += 1
                print()
            imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
            os.remove(TMP_PATH)

            os.rename(res, os.path.join(outp_dir, res_name))
        elif isdir and '_vid' in os.listdir(pth) and op_mode == 'D':
            tmp_name = filename_processing(op_mode, '1', filename, '.mp4', outp_dir, marker, count_correct)  # Преобразование имени файла (cv2 не воспринимает русские буквы, поэтому приходится использовать временное имя)
            res_name = filename_processing(op_mode, settings['naming_mode'], filename, '.mp4', outp_dir, marker, count_correct)

            print(f'({count_all}) <{filename}>  ->  <{res_name}>')  # Вывод информации

            inp_dir_tmp = os.path.join(inp_dir, filename)
            res = os.path.join(outp_dir, tmp_name)

            img = imread(os.path.join(inp_dir_tmp, '000000.png'))
            height = img.shape[0]
            width = img.shape[1]
            fps = 24
            video = cv2.VideoWriter(res, 0, fps, (width, height))

            h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b = decode_file_calc(img)

            count = 0
            for f in os.listdir(inp_dir_tmp):
                if f.endswith('.png'):
                    print(f'frame {count + 1}')
                    img = imread(os.path.join(inp_dir_tmp, f))
                    if settings['print_info'] == '1':  # Вывод информации о считывании
                        print(img.shape)
                    fr = decode_file(img, h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b)
                    imsave(TMP_PATH, fr.astype(uint8))
                    video.write(cv2.imread(TMP_PATH))
                    count += 1
                    print()
            imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
            os.remove(TMP_PATH)
            video.release()

            os.rename(res, os.path.join(outp_dir, res_name))
        elif isdir:
            res_name = filename_processing(op_mode, settings['naming_mode'], base_name, '', outp_dir, marker, count_correct)  # Преобразование имени файла

            print(f'({count_all}) <{filename}>  ->  <{res_name}>')  # Вывод информации

            new_inp_dir = os.path.join(inp_dir, filename)
            new_outp_dir = os.path.join(outp_dir, res_name)

            if res_name not in os.listdir(outp_dir):
                os.mkdir(new_outp_dir)

            print()

            count_all = encrypt_dir(op_mode, marker, formats, new_inp_dir, new_outp_dir, count_all)
        print(f'Time: {time.perf_counter() - start}\n')
    return count_all


# Шифровка
def encode():
    op_mode = 'E'
    input_dir = settings['dir_enc_from']
    output_dir = settings['dir_enc_to']
    marker = settings['marker_enc']
    formats = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.avi', '.mp4', '.webm']
    count_all = 0

    print('================================== START PROCESSING ==================================')
    encrypt_dir(op_mode, marker, formats, input_dir, output_dir, count_all)
    print('=============================== PROCESSING IS FINISHED ===============================')


# Дешифровка
def decode():
    global DEC_R, DEC_G, DEC_B
    DEC_R = [0] * 256  # Массив для отмены цветового множителя для красного канала
    DEC_G = [0] * 256  # Массив для отмены цветового множителя для зелёного канала
    DEC_B = [0] * 256  # Массив для отмены цветового множителя для синего канала
    for i in range(256):
        DEC_R[i * mult_r % 256] = i
        DEC_G[i * mult_g % 256] = i
        DEC_B[i * mult_b % 256] = i

    op_mode = 'D'
    input_dir = settings['dir_dec_from']
    output_dir = settings['dir_dec_to']
    marker = settings['marker_dec']
    formats = ['.png']
    count_all = 0

    print('================================== START PROCESSING ==================================')
    encrypt_dir(op_mode, marker, formats, input_dir, output_dir, count_all)
    print('=============================== PROCESSING IS FINISHED ===============================')


""" Графический интерфейс """


# Ввод только заданных символов
def validate_symbols(value, allowed_symbols):
    for c in value:
        if c not in allowed_symbols:
            return False
    return True


# Ввод только натуральных чисел
def validate_natural(value):
    return value == '' or value.isnumeric()


# Ввод только целых чисел
def validate_num(value):
    return value in ['', '-'] or value.isnumeric() or (value[0] == '-' and value[1:].isnumeric())


# Ввод только до заданной длины
def validate_len(value, max_len):
    return len(value) <= max_len


# Ввод только натуральных чисел до заданной длины
def validate_natural_and_len(value, max_len):
    return validate_natural(value) and validate_len(value, max_len)


# Ввод только целых чисел до заданной длины
def validate_num_and_len(value, max_len):
    return validate_num(value) and validate_len(value, max_len)


# Ввод только символов подходящих для ключа и до длины ключа
def validate_key(value):
    return validate_symbols(value, KEY_SYMBOLS) and validate_len(value, KEY_LEN)


# Всплывающее окно с сообщением
class PopupMsgW(tk.Toplevel):
    def __init__(self, parent, msg, btn_text='OK', title='Media encrypter'):
        super().__init__(parent)
        self.title(title)

        tk.Label(self, text=msg).grid(row=0, column=0)
        tk.Button(self, text=btn_text, command=self.destroy).grid(row=1, column=0)


# Всплывающее окно с сообщением и двумя кнопками
class PopupDialogueW(tk.Toplevel):
    def __init__(self, parent, msg='Are you sure?', btn_yes='Yes', btn_no='Cancel', title='Media encrypter'):
        super().__init__(parent)
        self.title(title)
        self.answer = False

        tk.Label(self, text=msg).grid(row=0, columnspan=2)
        tk.Button(self, text=btn_yes, command=self.yes).grid(row=1, column=0)
        tk.Button(self, text=btn_no, command=self.no).grid(row=1, column=1)

    def yes(self):
        self.answer = True
        self.destroy()

    def no(self):
        self.answer = False
        self.destroy()

    def open(self):
        self.grab_set()
        self.wait_window()
        return self.answer


# Всплывающее окно с полем tk.Entry
class PopupInputW(tk.Toplevel):
    def __init__(self, parent, msg='Enter a value', btn_text='Confirm', allowed_symbols=None, title='Media encrypter'):
        super().__init__(parent)
        self.title(title)

        tk.Label(self, text=msg).grid(row=0)
        self.answer = tk.StringVar()
        if allowed_symbols is None:
            tk.Entry(self, textvariable=self.answer).grid(row=1)
        else:
            self.vcmd = (self.register(lambda value: validate_symbols(value, allowed_symbols)), '%P')
            tk.Entry(self, textvariable=self.answer, validate='key', validatecommand=self.vcmd).grid(row=1)
        tk.Button(self, text=btn_text, command=self.destroy).grid(row=2)

    def open(self):
        answer = self.answer.get()
        return answer


# Всплывающее окно с полем ttk.Combobox
class PopupChooseW(tk.Toplevel):
    def __init__(self, parent, values, msg='Choose the one of these', btn_text='Confirm', title='Media encrypter'):
        super().__init__(parent)
        self.title(title)

        tk.Label(self, text=msg).grid(row=0)
        self.answer = tk.StringVar()
        ttk.Combobox(self, textvariable=self.answer, values=values, state='readonly').grid(row=1)
        tk.Button(self, text=btn_text, command=self.destroy).grid(row=2)

    def open(self):
        answer = self.answer.get()
        return answer


# Всплывающее окно ввода пароля
class EnterKeyW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Media encrypter - Key')
        self.key = tk.StringVar()
        self.has_key = False

        def focus_text(event):
            self.txt_example_key.config(state='normal')
            self.txt_example_key.focus()
            self.txt_example_key.config(state='disabled')

        self.txt_example_key = tk.Text(self, height=1, width=KEY_LEN, borderwidth=0, font='TkFixedFont')
        self.txt_example_key.insert(1.0, settings['example_key'])
        self.txt_example_key.grid(row=1, column=1)
        self.txt_example_key.configure(state='disabled')
        self.txt_example_key.bind('<Button-1>', focus_text)

        tk.Label(self, text=f'Enter a key ({KEY_LEN} symbols; only latin letters, digits, - and _)').grid(row=0, columnspan=2)
        tk.Label(self, text='An example of a key:').grid(row=1, column=0)
        tk.Label(self, text='Enter a key:').grid(row=2, column=0, sticky='E')

        self.vcmd = (self.register(validate_key), '%P')
        self.entry_key = tk.Entry(self, textvariable=self.key, width=KEY_LEN, validate='key', validatecommand=self.vcmd, font='TkFixedFont')
        self.btn_submit = tk.Button(self, text='Submit', command=self.check_key_and_return)

        self.entry_key.grid(row=2, column=1, sticky='W')
        self.btn_submit.grid(row=3, columnspan=2)

    # Проверить корректность ключа и, если корректен, сохранить
    def check_key_and_return(self):
        key = self.key.get()
        code, cause = check_key(key)
        if code == 'L':  # Если неверная длина ключа
            PopupMsgW(self, f'Wrong length of the key: {cause}!\nShould be {KEY_LEN}', title='Error')
            return
        self.has_key = True
        self.destroy()

    def open(self):
        self.grab_set()
        self.wait_window()
        key = self.key.get()
        return self.has_key, key


# Окно настроек
class SettingsW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Media encrypter - Settings')
        self.key = tk.StringVar()

        tk.Label(self, text='File names conversion mode').grid(      row=0,  column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Start counting files from').grid(       row=1,  column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Number of digits in numbers').grid(     row=2,  column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Marker for encoded files').grid(        row=3,  column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Marker for decoded files').grid(        row=4,  column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Russian letters processing mode').grid( row=5,  column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Source folder when encoding').grid(     row=6,  column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Destination folder when encoding').grid(row=7,  column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Source folder when decoding').grid(     row=8,  column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Destination folder when decoding').grid(row=9,  column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Example of a key').grid(                row=10, column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Whether to print info').grid(           row=11, column=0, columnspan=2, sticky='E')

        self.inp_naming_mode  = tk.StringVar()
        self.inp_count_from   = tk.StringVar(value=settings['count_from'])
        self.inp_format       = tk.StringVar(value=settings['format'])
        self.inp_marker_enc   = tk.StringVar(value=settings['marker_enc'])
        self.inp_marker_dec   = tk.StringVar(value=settings['marker_dec'])
        self.inp_ru_letters   = tk.StringVar()
        self.inp_dir_enc_from = tk.StringVar(value=settings['dir_enc_from'])
        self.inp_dir_enc_to   = tk.StringVar(value=settings['dir_enc_to'])
        self.inp_dir_dec_from = tk.StringVar(value=settings['dir_dec_from'])
        self.inp_dir_dec_to   = tk.StringVar(value=settings['dir_dec_to'])
        self.inp_example_key  = tk.StringVar(value=settings['example_key'])
        self.inp_print_info   = tk.StringVar()

        self.vcmd_natural = (self.register(lambda value: validate_natural_and_len(value, 3)), '%P')
        self.vcmd_num     = (self.register(validate_num), '%P')
        self.vcmd_key     = (self.register(lambda value: validate_len(value, KEY_LEN)), '%P')

        self.combo_naming_mode  = ttk.Combobox(self, textvariable=self.inp_naming_mode, values=NAMING_MODES, state='readonly')
        self.entry_count_from   = tk.Entry(    self, textvariable=self.inp_count_from, width=10, validate='key', validatecommand=self.vcmd_num)
        self.entry_format       = tk.Entry(    self, textvariable=self.inp_format,     width=10, validate='key', validatecommand=self.vcmd_natural)
        self.entry_marker_enc   = tk.Entry(    self, textvariable=self.inp_marker_enc)
        self.entry_marker_dec   = tk.Entry(    self, textvariable=self.inp_marker_dec)
        self.combo_ru_letters   = ttk.Combobox(self, textvariable=self.inp_ru_letters, values=RU_LETTERS_MODES, state='readonly')
        self.entry_dir_enc_from = tk.Entry(    self, textvariable=self.inp_dir_enc_from, width=35)
        self.entry_dir_enc_to   = tk.Entry(    self, textvariable=self.inp_dir_enc_to,   width=35)
        self.entry_dir_dec_from = tk.Entry(    self, textvariable=self.inp_dir_dec_from, width=35)
        self.entry_dir_dec_to   = tk.Entry(    self, textvariable=self.inp_dir_dec_to,   width=35)
        self.entry_example_key  = tk.Entry(    self, textvariable=self.inp_example_key,  width=KEY_LEN, font='TkFixedFont', validate='key', validatecommand=self.vcmd_key)
        self.combo_print_info   = ttk.Combobox(self, textvariable=self.inp_print_info, values=PRINT_INFO_MODES, state='readonly')

        self.combo_naming_mode.current(int(settings['naming_mode']))
        self.combo_ru_letters.current( int(settings['ru_letters']))
        self.combo_print_info.current( int(settings['print_info']))

        self.combo_naming_mode.grid( row=0,  column=2, columnspan=3, sticky='W')
        self.entry_count_from.grid(  row=1,  column=2, columnspan=2, sticky='W')
        self.entry_format.grid(      row=2,  column=2, columnspan=3, sticky='W')
        self.entry_marker_enc.grid(  row=3,  column=2, columnspan=3, sticky='W')
        self.entry_marker_dec.grid(  row=4,  column=2, columnspan=3, sticky='W')
        self.combo_ru_letters.grid(  row=5,  column=2, columnspan=3, sticky='W')
        self.entry_dir_enc_from.grid(row=6,  column=2, columnspan=2, sticky='W')
        self.entry_dir_enc_to.grid(  row=7,  column=2, columnspan=2, sticky='W')
        self.entry_dir_dec_from.grid(row=8,  column=2, columnspan=2, sticky='W')
        self.entry_dir_dec_to.grid(  row=9,  column=2, columnspan=2, sticky='W')
        self.entry_example_key.grid( row=10, column=2, columnspan=3, sticky='W')
        self.combo_print_info.grid(  row=11, column=2, columnspan=3, sticky='W')

        tk.Label(self, text='(only for numerating file names conversion mode)').grid(    row=1, column=3, columnspan=2, sticky='W')
        tk.Label(self, text='(only for numerating file names conversion mode)').grid(    row=2, column=3, columnspan=2, sticky='W')
        tk.Label(self, text='(only for prefix/postfix file names conversion mode)').grid(row=3, column=3, columnspan=2, sticky='W')
        tk.Label(self, text='(only for prefix/postfix file names conversion mode)').grid(row=4, column=3, columnspan=2, sticky='W')

        self.btn_source_enc = tk.Button(self, text='Search', command=self.choose_source_enc)
        self.btn_dest_enc   = tk.Button(self, text='Search', command=self.choose_dest_enc)
        self.btn_source_dec = tk.Button(self, text='Search', command=self.choose_source_dec)
        self.btn_dest_dec   = tk.Button(self, text='Search', command=self.choose_dest_dec)

        self.btn_source_enc.grid(row=6, column=4, sticky='W')
        self.btn_dest_enc.grid(  row=7, column=4, sticky='W')
        self.btn_source_dec.grid(row=8, column=4, sticky='W')
        self.btn_dest_dec.grid(  row=9, column=4, sticky='W')

        self.btn_def           = tk.Button(self, text='Set default settings',        command=self.set_default_settings)
        self.btn_save_custom   = tk.Button(self, text='Save your custom settings',   command=self.save_custom_settings)
        self.btn_load_custom   = tk.Button(self, text='Load your custom settings',   command=self.load_custom_settings)
        self.btn_remove_custom = tk.Button(self, text='Remove your custom settings', command=self.remove_custom_settings)
        self.btn_save  = tk.Button(self, text='Save',  command=self.save)
        self.btn_close = tk.Button(self, text='Close', command=self.close)

        self.btn_def.grid(          row=12, column=0)
        self.btn_save_custom.grid(  row=12, column=1)
        self.btn_load_custom.grid(  row=12, column=2, columnspan=2)
        self.btn_remove_custom.grid(row=12, column=4)
        self.btn_save.grid(         row=13, column=1)
        self.btn_close.grid(        row=13, column=2, columnspan=2)

    def choose_source_enc(self):
        directory = askdirectory()
        settings['dir_enc_from'] = directory
        self.inp_dir_enc_from.set(directory)

    def choose_dest_enc(self):
        directory = askdirectory()
        settings['dir_enc_to'] = directory
        self.inp_dir_enc_to = directory

    def choose_source_dec(self):
        directory = askdirectory()
        settings['dir_dec_from'] = directory
        self.inp_dir_dec_from = directory

    def choose_dest_dec(self):
        directory = askdirectory()
        settings['dir_dec_to'] = directory
        self.inp_dir_dec_to = directory

    # Сохранить изменения
    def save(self):
        has_errors = False

        if self.inp_count_from.get() in ['', '-']:
            PopupMsgW(self, 'Incorrect "start counting files from" value!', title='Error')
            self.entry_count_from['background'] = ERROR_COLOR
            has_errors = True
        else:
            self.entry_count_from['background'] = NORMAL_COLOR

        if self.inp_format.get() == '':
            PopupMsgW(self, 'Incorrect "number of digits in numbers" value!', title='Error')
            self.entry_format['background'] = ERROR_COLOR
            has_errors = True
        else:
            self.entry_format['background'] = NORMAL_COLOR

        if len(self.inp_example_key.get()) != KEY_LEN:
            PopupMsgW(self, f'Incorrect "example of a key" value!\nShould has {KEY_LEN} symbols', title='Error')
            self.entry_example_key['background'] = ERROR_COLOR
            has_errors = True
        else:
            self.entry_example_key['background'] = NORMAL_COLOR

        if has_errors:
            return

        settings['naming_mode']  = str(NAMING_MODES.index(self.inp_naming_mode.get()))
        settings['count_from']   = self.inp_count_from.get()
        settings['format']       = self.inp_format.get()
        settings['marker_enc']   = self.inp_marker_enc.get()
        settings['marker_dec']   = self.inp_marker_dec.get()
        settings['ru_letters']   = str(RU_LETTERS_MODES.index(self.inp_ru_letters.get()))
        settings['dir_enc_from'] = self.inp_dir_enc_from.get()
        settings['dir_enc_to']   = self.inp_dir_enc_to.get()
        settings['dir_dec_from'] = self.inp_dir_dec_from.get()
        settings['dir_dec_to']   = self.inp_dir_dec_to.get()
        settings['example_key']  = self.inp_example_key.get()
        settings['print_info']   = str(PRINT_INFO_MODES.index(self.inp_print_info.get()))

        save_settings_to_file()

    # Закрыть окно без сохранения
    def close(self):
        # Если были изменения, то предлагается сохранить их
        if settings['naming_mode'] == str(NAMING_MODES.index(self.inp_naming_mode.get())) and\
            settings['count_from'] == self.inp_count_from.get() and\
            settings['format'] == self.inp_format.get() and\
            settings['marker_enc'] == self.inp_marker_enc.get() and\
            settings['marker_dec'] == self.inp_marker_dec.get() and\
            settings['ru_letters'] == str(RU_LETTERS_MODES.index(self.inp_ru_letters.get())) and\
            settings['dir_enc_from'] == self.inp_dir_enc_from.get() and\
            settings['dir_enc_to'] == self.inp_dir_enc_to.get() and\
            settings['dir_dec_from'] == self.inp_dir_dec_from.get() and\
            settings['dir_dec_to'] == self.inp_dir_dec_to.get() and\
            settings['example_key'] == self.inp_example_key.get() and\
                settings['print_info'] == str(PRINT_INFO_MODES.index(self.inp_print_info.get())):
            self.destroy()
        else:
            window = PopupDialogueW(self, f'If you close the window, the changes will not be saved! Close settings?', title='Warning')
            answer = window.open()
            if answer:
                self.destroy()

    # Установить настройки по умолчанию
    def set_default_settings(self):
        set_default_settings()
        self.refresh()

    # Обновить отображаемые настройки
    def refresh(self):
        self.inp_count_from.set(  settings['count_from'])
        self.inp_format.set(      settings['format'])
        self.inp_marker_enc.set(  settings['marker_enc'])
        self.inp_marker_dec.set(  settings['marker_dec'])
        self.inp_dir_enc_from.set(settings['dir_enc_from'])
        self.inp_dir_enc_to.set(  settings['dir_enc_to'])
        self.inp_dir_dec_from.set(settings['dir_dec_from'])
        self.inp_dir_dec_to.set(  settings['dir_dec_to'])
        self.inp_example_key.set( settings['example_key'])

        self.combo_naming_mode.current(int(settings['naming_mode']))
        self.combo_ru_letters.current( int(settings['ru_letters']))
        self.combo_print_info.current( int(settings['print_info']))

    # Сохранить пользовательские настройки
    def save_custom_settings(self):
        window = PopupInputW(self, 'Enter a name for save your custom settings', allowed_symbols=FN_SYMBOLS)
        self.wait_window(window)
        custom_settings_file = window.open() + '.txt'
        if custom_settings_file == '.txt':
            PopupMsgW(self, 'Incorrect name for save', title='Error')
            return
        for c in custom_settings_file:
            if c not in FN_SYMBOLS:
                PopupMsgW(self, f'Incorrect symbol "{c}" in the save name', title='Error')
                return

        copyfile(SETTINGS_PATH, os.path.join(CUSTOM_SETTINGS_DIR, custom_settings_file))

    # Выбрать файл с сохранением
    def choose_save(self, cmd_name):
        csf_count = 0
        csf_list = []
        for file_name in os.listdir(CUSTOM_SETTINGS_DIR):
            base_name, ext = os.path.splitext(file_name)
            if ext == '.txt':
                csf_list += [base_name]
                csf_count += 1
        if csf_count == 0:  # Если нет сохранённых настроек
            PopupMsgW(self, 'There are no saves!', title='Error')
            return False, ''
        else:
            window = PopupChooseW(self, csf_list, 'Choose a save you want to ' + cmd_name)
            self.wait_window(window)
            filename = window.open() + '.txt'
            return True, filename

    # Загрузить пользовательские настройки
    def load_custom_settings(self):
        has_saves, filename = self.choose_save('load')
        if not has_saves:
            return
        custom_settings_file = os.path.join(CUSTOM_SETTINGS_DIR, filename)

        load_settings(custom_settings_file)
        correct_settings()
        self.refresh()

    # Удалить пользовательские настройки
    def remove_custom_settings(self):
        has_saves, filename = self.choose_save('remove')
        if not has_saves:
            return
        custom_settings_file = os.path.join(CUSTOM_SETTINGS_DIR, filename)

        os.remove(custom_settings_file)

    def open(self):
        self.grab_set()
        self.wait_window()


# Окно режима ручного управления
class ManualW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Media encrypter - MCM')
        self.geometry('300x510')
        self.mode = ''

        tk.Label(self, text='H multiplier for R: ').grid(         row=1,  column=0, sticky='E')  # Множитель блоков по горизонтали для красного канала
        tk.Label(self, text='H multiplier for G: ').grid(         row=2,  column=0, sticky='E')  # Множитель блоков по горизонтали для зелёного канала
        tk.Label(self, text='H multiplier for B: ').grid(         row=3,  column=0, sticky='E')  # Множитель блоков по горизонтали для синего канала
        tk.Label(self, text='W multiplier for R: ').grid(         row=4,  column=0, sticky='E')  # Множитель блоков по вертикали для красного канала
        tk.Label(self, text='W multiplier for G: ').grid(         row=5,  column=0, sticky='E')  # Множитель блоков по вертикали для зелёного канала
        tk.Label(self, text='W multiplier for B: ').grid(         row=6,  column=0, sticky='E')  # Множитель блоков по вертикали для синего канала
        tk.Label(self, text='H shift for R: ').grid(              row=7,  column=0, sticky='E')  # Сдвиг блоков по горизонтали для красного канала
        tk.Label(self, text='H shift for G: ').grid(              row=8,  column=0, sticky='E')  # Сдвиг блоков по горизонтали для зелёного канала
        tk.Label(self, text='H shift for B: ').grid(              row=9,  column=0, sticky='E')  # Сдвиг блоков по горизонтали для синего канала
        tk.Label(self, text='W shift for R: ').grid(              row=10, column=0, sticky='E')  # Сдвиг блоков по вертикали для красного канала
        tk.Label(self, text='W shift for G: ').grid(              row=11, column=0, sticky='E')  # Сдвиг блоков по вертикали для зелёного канала
        tk.Label(self, text='W shift for B: ').grid(              row=12, column=0, sticky='E')  # Сдвиг блоков по вертикали для синего канала
        tk.Label(self, text='Nels order: ').grid(                 row=13, column=0, sticky='E')  # Порядок следования каналов после перемешивания
        tk.Label(self, text='Primary color shift for R: ').grid(  row=14, column=0, sticky='E')  # Первичное смещение цвета для красного канала
        tk.Label(self, text='Primary color shift for G: ').grid(  row=15, column=0, sticky='E')  # Первичное смещение цвета для зелёного канала
        tk.Label(self, text='Primary color shift for B: ').grid(  row=16, column=0, sticky='E')  # Первичное смещение цвета для синего канала
        tk.Label(self, text='Color multiplier for R: ').grid(     row=17, column=0, sticky='E')  # Цветовой множитель для красного канала
        tk.Label(self, text='Color multiplier for G: ').grid(     row=18, column=0, sticky='E')  # Цветовой множитель для зелёного канала
        tk.Label(self, text='Color multiplier for B: ').grid(     row=19, column=0, sticky='E')  # Цветовой множитель для синего канала
        tk.Label(self, text='Secondary color shift for R: ').grid(row=20, column=0, sticky='E')  # Вторичное смещение цвета для красного канала
        tk.Label(self, text='Secondary color shift for G: ').grid(row=21, column=0, sticky='E')  # Вторичное смещение цвета для зелёного канала
        tk.Label(self, text='Secondary color shift for B: ').grid(row=22, column=0, sticky='E')  # Вторичное смещение цвета для синего канала
        tk.Label(self, text='Multiplier for filenames: ').grid(   row=23, column=0, sticky='E')  # Сдвиг букв в имени файла

        self.inp_mult_blocks_h_r = tk.StringVar()
        self.inp_mult_blocks_h_g = tk.StringVar()
        self.inp_mult_blocks_h_b = tk.StringVar()
        self.inp_mult_blocks_w_r = tk.StringVar()
        self.inp_mult_blocks_w_g = tk.StringVar()
        self.inp_mult_blocks_w_b = tk.StringVar()
        self.inp_shift_h_r = tk.StringVar()
        self.inp_shift_h_g = tk.StringVar()
        self.inp_shift_h_b = tk.StringVar()
        self.inp_shift_w_r = tk.StringVar()
        self.inp_shift_w_g = tk.StringVar()
        self.inp_shift_w_b = tk.StringVar()
        self.inp_order = tk.StringVar()
        self.inp_shift_r = tk.StringVar()
        self.inp_shift_g = tk.StringVar()
        self.inp_shift_b = tk.StringVar()
        self.inp_mult_r = tk.StringVar()
        self.inp_mult_g = tk.StringVar()
        self.inp_mult_b = tk.StringVar()
        self.inp_shift2_r = tk.StringVar()
        self.inp_shift2_g = tk.StringVar()
        self.inp_shift2_b = tk.StringVar()
        self.inp_mult_name = tk.StringVar()

        self.vcmd = (self.register(validate_natural), '%P')

        self.entry_mult_blocks_h_r = tk.Entry(self, textvariable=self.inp_mult_blocks_h_r, validate='key', validatecommand=self.vcmd)
        self.entry_mult_blocks_h_g = tk.Entry(self, textvariable=self.inp_mult_blocks_h_g, validate='key', validatecommand=self.vcmd)
        self.entry_mult_blocks_h_b = tk.Entry(self, textvariable=self.inp_mult_blocks_h_b, validate='key', validatecommand=self.vcmd)
        self.entry_mult_blocks_w_r = tk.Entry(self, textvariable=self.inp_mult_blocks_w_r, validate='key', validatecommand=self.vcmd)
        self.entry_mult_blocks_w_g = tk.Entry(self, textvariable=self.inp_mult_blocks_w_g, validate='key', validatecommand=self.vcmd)
        self.entry_mult_blocks_w_b = tk.Entry(self, textvariable=self.inp_mult_blocks_w_b, validate='key', validatecommand=self.vcmd)
        self.entry_shift_h_r =       tk.Entry(self, textvariable=self.inp_shift_h_r,       validate='key', validatecommand=self.vcmd)
        self.entry_shift_h_g =       tk.Entry(self, textvariable=self.inp_shift_h_g,       validate='key', validatecommand=self.vcmd)
        self.entry_shift_h_b =       tk.Entry(self, textvariable=self.inp_shift_h_b,       validate='key', validatecommand=self.vcmd)
        self.entry_shift_w_r =       tk.Entry(self, textvariable=self.inp_shift_w_r,       validate='key', validatecommand=self.vcmd)
        self.entry_shift_w_g =       tk.Entry(self, textvariable=self.inp_shift_w_g,       validate='key', validatecommand=self.vcmd)
        self.entry_shift_w_b =       tk.Entry(self, textvariable=self.inp_shift_w_b,       validate='key', validatecommand=self.vcmd)
        self.entry_order =           tk.Entry(self, textvariable=self.inp_order,           validate='key', validatecommand=self.vcmd)
        self.entry_shift_r =         tk.Entry(self, textvariable=self.inp_shift_r,         validate='key', validatecommand=self.vcmd)
        self.entry_shift_g =         tk.Entry(self, textvariable=self.inp_shift_g,         validate='key', validatecommand=self.vcmd)
        self.entry_shift_b =         tk.Entry(self, textvariable=self.inp_shift_b,         validate='key', validatecommand=self.vcmd)
        self.entry_mult_r =          tk.Entry(self, textvariable=self.inp_mult_r,          validate='key', validatecommand=self.vcmd)
        self.entry_mult_g =          tk.Entry(self, textvariable=self.inp_mult_g,          validate='key', validatecommand=self.vcmd)
        self.entry_mult_b =          tk.Entry(self, textvariable=self.inp_mult_b,          validate='key', validatecommand=self.vcmd)
        self.entry_shift2_r =        tk.Entry(self, textvariable=self.inp_shift2_r,        validate='key', validatecommand=self.vcmd)
        self.entry_shift2_g =        tk.Entry(self, textvariable=self.inp_shift2_g,        validate='key', validatecommand=self.vcmd)
        self.entry_shift2_b =        tk.Entry(self, textvariable=self.inp_shift2_b,        validate='key', validatecommand=self.vcmd)
        self.entry_mult_name =       tk.Entry(self, textvariable=self.inp_mult_name,       validate='key', validatecommand=self.vcmd)

        self.entry_mult_blocks_h_r.grid(row=1,  column=1, sticky='W')
        self.entry_mult_blocks_h_g.grid(row=2,  column=1, sticky='W')
        self.entry_mult_blocks_h_b.grid(row=3,  column=1, sticky='W')
        self.entry_mult_blocks_w_r.grid(row=4,  column=1, sticky='W')
        self.entry_mult_blocks_w_g.grid(row=5,  column=1, sticky='W')
        self.entry_mult_blocks_w_b.grid(row=6,  column=1, sticky='W')
        self.entry_shift_h_r.grid(      row=7,  column=1, sticky='W')
        self.entry_shift_h_g.grid(      row=8,  column=1, sticky='W')
        self.entry_shift_h_b.grid(      row=9,  column=1, sticky='W')
        self.entry_shift_w_r.grid(      row=10, column=1, sticky='W')
        self.entry_shift_w_g.grid(      row=11, column=1, sticky='W')
        self.entry_shift_w_b.grid(      row=12, column=1, sticky='W')
        self.entry_order.grid(          row=13, column=1, sticky='W')
        self.entry_shift_r.grid(        row=14, column=1, sticky='W')
        self.entry_shift_g.grid(        row=15, column=1, sticky='W')
        self.entry_shift_b.grid(        row=16, column=1, sticky='W')
        self.entry_mult_r.grid(         row=17, column=1, sticky='W')
        self.entry_mult_g.grid(         row=18, column=1, sticky='W')
        self.entry_mult_b.grid(         row=19, column=1, sticky='W')
        self.entry_shift2_r.grid(       row=20, column=1, sticky='W')
        self.entry_shift2_g.grid(       row=21, column=1, sticky='W')
        self.entry_shift2_b.grid(       row=22, column=1, sticky='W')
        self.entry_mult_name.grid(      row=23, column=1, sticky='W')

        self.btn_encode = tk.Button(self, text='Encode', command=self.pre_encode)
        self.btn_decode = tk.Button(self, text='Decode', command=self.pre_decode)

        self.btn_encode.grid(row=24, column=0)
        self.btn_decode.grid(row=24, column=1)

    # Заполнить ключевые значения
    def set_key_vales(self):
        global mult_blocks_h_r, mult_blocks_h_g, mult_blocks_h_b, mult_blocks_w_r, mult_blocks_w_g, mult_blocks_w_b,\
            shift_h_r, shift_h_g, shift_h_b, shift_w_r, shift_w_g, shift_w_b, shift_r, shift_g, shift_b, mult_r,\
            mult_g, mult_b, shift2_r, shift2_g, shift2_b, order, mult_name

        if self.inp_mult_blocks_h_r.get() == '' or\
            self.inp_mult_blocks_h_g.get() == '' or\
            self.inp_mult_blocks_h_b.get() == '' or\
            self.inp_mult_blocks_w_r.get() == '' or\
            self.inp_mult_blocks_w_g.get() == '' or\
            self.inp_mult_blocks_w_b.get() == '' or\
            self.inp_shift_h_r.get() == '' or\
            self.inp_shift_h_g.get() == '' or\
            self.inp_shift_h_b.get() == '' or\
            self.inp_shift_w_r.get() == '' or\
            self.inp_shift_w_g.get() == '' or\
            self.inp_shift_w_b.get() == '' or\
            self.inp_order.get() == '' or\
            self.inp_shift_r.get() == '' or\
            self.inp_shift_g.get() == '' or\
            self.inp_shift_b.get() == '' or\
            self.inp_mult_r.get() == '' or\
            self.inp_mult_g.get() == '' or\
            self.inp_mult_b.get() == '' or\
            self.inp_shift2_r.get() == '' or\
            self.inp_shift2_g.get() == '' or\
            self.inp_shift2_b.get() == '' or\
            self.inp_mult_name.get() == '':
            PopupMsgW(self, 'All fields should be filled', title='Error')
            return False

        mult_blocks_h_r = int(self.inp_mult_blocks_h_r.get())
        mult_blocks_h_g = int(self.inp_mult_blocks_h_g.get())
        mult_blocks_h_b = int(self.inp_mult_blocks_h_b.get())
        mult_blocks_w_r = int(self.inp_mult_blocks_w_r.get())
        mult_blocks_w_g = int(self.inp_mult_blocks_w_g.get())
        mult_blocks_w_b = int(self.inp_mult_blocks_w_b.get())
        shift_h_r = int(self.inp_shift_h_r.get())
        shift_h_g = int(self.inp_shift_h_g.get())
        shift_h_b = int(self.inp_shift_h_b.get())
        shift_w_r = int(self.inp_shift_w_r.get())
        shift_w_g = int(self.inp_shift_w_g.get())
        shift_w_b = int(self.inp_shift_w_b.get())
        order = int(self.inp_order.get()) % 6
        shift_r = int(self.inp_shift_r.get())
        shift_g = int(self.inp_shift_g.get())
        shift_b = int(self.inp_shift_b.get())
        mult_r = int(self.inp_mult_r.get())
        mult_g = int(self.inp_mult_g.get())
        mult_b = int(self.inp_mult_b.get())
        shift2_r = int(self.inp_shift2_r.get())
        shift2_g = int(self.inp_shift2_g.get())
        shift2_b = int(self.inp_shift2_b.get())
        mult_name = int(self.inp_mult_name.get())
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
        return self.mode


# Главное окно
class MainW(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Media encrypter')
        self.geometry('280x200')

        try:
            load_settings(SETTINGS_PATH)
        except FileNotFoundError:  # Если файл с настройками отсутствует, то устанавливаются настройки по умолчанию
            set_default_settings()
        else:
            correct_settings()  # Проверка корректности настроек

        self.lbl_header = tk.Label(self, text='Anenokil development  presents\n' +
                                              (30 - len(PROGRAM_NAME)) // 2 * ' ' + PROGRAM_NAME + '\n' +
                                              (30 - len(PROGRAM_DATE)) // 2 * ' ' + PROGRAM_DATE)
        self.lbl_header.pack()

        self.btn_settings = tk.Button(self, text='Settings', command=self.open_settings)
        self.btn_settings.pack()

        self.btn_encode = tk.Button(self, text='Encode', command=self.encode)
        self.btn_encode.pack()

        self.btn_decode = tk.Button(self, text='Decode', command=self.decode)
        self.btn_decode.pack()

        self.btn_mcm = tk.Button(self, text='Debug (MCM)', command=self.mcm)
        self.btn_mcm.pack()

        self.btn_close = tk.Button(self, text='Close', command=self.quit)
        self.btn_close.pack()

    # Перейти в настройки
    def open_settings(self):
        SettingsW(self)
        return

    # Отправить на шифровку
    def encode(self):
        window = EnterKeyW(self)
        has_key, key = window.open()
        if not has_key:
            return
        extract_key_values(key_to_bites(key))
        encode()

    # Отправить на дешифровку
    def decode(self):
        window = EnterKeyW(self)
        has_key, key = window.open()
        if not has_key:
            return
        extract_key_values(key_to_bites(key))
        decode()

    # Перейти в режим ручного управления
    def mcm(self):
        window = ManualW(self)
        action = window.open()

        if action == 'E':
            encode()
        elif action == 'D':
            decode()


# Затирание временного файла при запуске программы, если он остался с прошлого сеанса
if TMP_FILE in os.listdir(RESOURCES_DIR):
    open(TMP_PATH, 'w')
    os.remove(TMP_PATH)

# Вывод информации о программе
print('======================================================================================\n')
print('                            Anenokil development  presents')
print('                            ' + (30 - len(PROGRAM_NAME)) // 2 * ' ' + PROGRAM_NAME)
print('                            ' + (30 - len(PROGRAM_DATE)) // 2 * ' ' + PROGRAM_DATE + '\n')
print('======================================================================================')

gui = MainW()
gui.mainloop()

# v1.0.0
# v2.0.0 - добавлены настройки
# v3.0.0 - добавлена обработка гифок
# v4.0.0 - добавлена обработка видео
# v5.0.0 - добавлена обработка вложенных папок
# v6.0.0 - добавлен графический интерфейс
