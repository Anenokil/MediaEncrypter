from skimage.io import imread, imsave
from numpy import dstack, uint8, arange
from math import gcd  # НОД
from transliterate import translit  # Транслитерация
from shutil import copyfile  # Копирование файлов
from PIL import Image  # Разбиение gif-изображений на кадры
import imageio.v2 as io  # Составление gif-изображений из кадров
from moviepy.editor import VideoFileClip  # Разбиение видео на кадры
import cv2  # Составление видео из кадров
import os
import tkinter as tk
import tkinter.ttk as ttk

PROGRAM_NAME = 'Media encrypter v6.0.0_PRE-1'
PROGRAM_DATE = '26.12.2022  2:39'

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
NAME_MODE_DEF = '0'
COUNT_FROM_DEF = '1'
FORMAT_DEF = '1'
MARKER_ENC_DEF = '_ENC_'
MARKER_DEC_DEF = '_DEC_'
RU_DEF_LETTERS = '0'
DIR_ENC_FROM_DEF = 'f_src'
DIR_ENC_TO_DEF = 'f_enc'
DIR_DEC_FROM_DEF = 'f_enc'
DIR_DEC_TO_DEF = 'f_dec'
EXAMPLE_KEY_DEF = 'This_Is-The_Example-Of_A-Correct_Key-012'
PRINT_INFO_DEF = '0'

# Варианты настроек с перечислимым типом
NAMING_MODES = ['encryption', 'numeration', 'add prefix', 'add postfix', 'don`t change']  # Варианты настройки именования выходных файлов
RU_LANG_MODES = ['transliterate to latin', 'don`t change']  # Варианты настройки обработки кириллических букв
PRINT_INFO_MODES = ['don`t print', 'print']  # Варианты настройки печати информации

""" Ключ """
KEY_SYMBOLS = "0123456789-abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # Допустимые в ключе символы
KEY_LEN = 40  # Длина ключа


# Вывод сообщения об ошибке
def print_exc(text):
    print('{!!!} ' + text + ' {!!!}')


# Установка значений по умолчанию для всех настроек
def set_default_settings():
    global _s_name_mode_, _s_count_from_, _s_format_, _s_marker_enc_, _s_marker_dec_, _s_ru_, _s_dir_enc_from_,\
        _s_dir_enc_to_, _s_dir_dec_from_, _s_dir_dec_to_, _s_example_key_, _s_print_info_

    _s_name_mode_ = NAME_MODE_DEF
    _s_count_from_ = COUNT_FROM_DEF
    _s_format_ = FORMAT_DEF
    _s_marker_enc_ = MARKER_ENC_DEF
    _s_marker_dec_ = MARKER_DEC_DEF
    _s_ru_ = RU_DEF_LETTERS
    _s_dir_enc_from_ = DIR_ENC_FROM_DEF
    _s_dir_enc_to_ = DIR_ENC_TO_DEF
    _s_dir_dec_from_ = DIR_DEC_FROM_DEF
    _s_dir_dec_to_ = DIR_DEC_TO_DEF
    _s_example_key_ = EXAMPLE_KEY_DEF
    _s_print_info_ = PRINT_INFO_DEF


# Ввод ключа и преобразование его в массив битов
def key_to_bites(key):
    bits = [[0] * KEY_LEN for _ in range(6)]  # Преобразование ключа в массив битов (каждый символ - в 6 битов)
    for _i in range(KEY_LEN):
        temp = KEY_SYMBOLS.find(key[_i])
        for j in range(6):
            bits[j][_i] = temp // (2 ** j) % 2
    return bits


# Нахождение числа по его битам
def bites_sum(*bites):
    s = 0
    for _i in bites:
        if type(_i) == list:  # Можно передавать массивы
            for j in _i:
                s = 2 * s + j
        else:  # А можно числа
            s = 2 * s + _i
    return s


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

    if _s_print_info_ == '1':  # Вывод ключевых значений
        print('=================================== KEY  CONSTANTS ===================================')
        print(f'  ML BH: {mult_blocks_h_r}, {mult_blocks_h_g}, {mult_blocks_h_b}')
        print(f'  ML BW: {mult_blocks_w_r}, {mult_blocks_w_g}, {mult_blocks_w_b}')
        print(f'  SH  H: {shift_h_r}, {shift_h_g}, {shift_h_b}')
        print(f'  SH  W: {shift_w_r}, {shift_w_g}, {shift_w_b}')
        print(f'  ORDER: {order}')
        print(f'  SH1 C: {shift_r}, {shift_g}, {shift_b}')
        print(f'  ML  C: {mult_r}, {mult_g}, {mult_b}')
        print(f'  SH2 C: {shift2_r}, {shift2_g}, {shift2_b}')
        print(f'  ML  N: {mult_name}')
        print('======================================================================================')


# Разделение полотна на блоки и их перемешивание
def mix_blocks(img, mult_h, mult_w, shift_h, shift_w):
    h = img.shape[0]  # Высота изображения
    w = img.shape[1]  # Ширина изображения

    while gcd(mult_h, h) != 1 or mult_h % h == 1:  # Нахождение наименьшего числа, взаимно-простого с h,
                                                   # большего чем mult_h, дающего при делении на h в остатке 1
        mult_h += 1
    while gcd(mult_w, w) != 1 or mult_w % w == 1:  # Нахождение наименьшего числа, взаимно-простого с w,
                                                   # большего чем mult_w, дающего при делении на w в остатке 1
        mult_w += 1
    if _s_print_info_ == '1':
        print(f'{h}x{w}: {mult_h} {mult_w}')

    img_tmp = img.copy()
    for _i in range(h):
        for j in range(w):
            jj = (j + shift_w * _i) % w
            ii = (_i + shift_h * jj) % h
            iii = (ii * mult_h) % h
            jjj = (jj * mult_w) % w
            img[iii][jjj] = img_tmp[_i][j]


# Шифровка файла
def encode(img):
    if len(img.shape) < 3:
        red, green, blue = img.copy(), img.copy(), img.copy()
    else:
        red, green, blue = [img[:, :, _i].copy() for _i in range(3)]  # Разделение изображения на RGB-каналы

    mix_blocks(red,   mult_blocks_h_r, mult_blocks_w_r, shift_h_r, shift_w_r)  # Перемешивание блоков для каждого канала
    mix_blocks(green, mult_blocks_h_g, mult_blocks_w_g, shift_h_g, shift_w_g)
    mix_blocks(blue,  mult_blocks_h_b, mult_blocks_w_b, shift_h_b, shift_w_b)

    red = (red + shift_r) % 256  # Начальное смещение цвета для каждого канала
    green = (green + shift_g) % 256
    blue = (blue + shift_b) % 256

    red = (red * mult_r) % 256  # Мультипликативное смещение цвета для каждого канала
    green = (green * mult_g) % 256
    blue = (blue * mult_b) % 256

    red = (red + shift2_r) % 256  # Конечное смещение цвета для каждого канала
    green = (green + shift2_g) % 256
    blue = (blue + shift2_b) % 256

    if len(img.shape) < 3:
        img = red
    else:
        if order == 0:  # Перемешивание и объединение каналов
            img = dstack((red, green, blue))
        elif order == 1:
            img = dstack((red, blue, green))
        elif order == 2:
            img = dstack((green, red, blue))
        elif order == 3:
            img = dstack((green, blue, red))
        elif order == 4:
            img = dstack((blue, red, green))
        elif order == 5:
            img = dstack((blue, green, red))

    return img


# Вычисление параметров для recover_blocks
def recover_blocks_calc(h, w, mult_h, mult_w):
    while gcd(mult_h, h) != 1 or mult_h % h == 1:  # Нахождение наименьшего числа, взаимно-простого с h,
                                                   # большего чем mult_h, дающего при делении на h в остатке 1
        mult_h += 1
    while gcd(mult_w, w) != 1 or mult_w % w == 1:  # Нахождение наименьшего числа, взаимно-простого с w,
                                                   # большего чем mult_w, дающего при делении на w в остатке 1
        mult_w += 1
    if _s_print_info_ == '1':
        print(f'{h}x{w}: {mult_h} {mult_w}')

    dec_h = [0] * h  # Составление массива обратных сдвигов по вертикали
    for _i in range(h):
        dec_h[(_i * mult_h) % h] = _i
    dec_w = [0] * w  # Составление массива обратных сдвигов по горизонтали
    for _i in range(w):
        dec_w[(_i * mult_w) % w] = _i

    return dec_h, dec_w


# Разделение полотна на блоки и восстановление из них исходного изображения
def recover_blocks(img, h, w, shift_h, shift_w, dec_h, dec_w):
    img_tmp = img.copy()
    for _i in range(h):
        for j in range(w):
            ii = dec_h[_i]
            jj = dec_w[j]
            iii = (ii + (h - shift_h) * jj) % h
            jjj = (jj + (w - shift_w) * iii) % w
            img[iii][jjj] = img_tmp[_i][j]


# Вычисление параметров для decode
def decode_calc(img):
    h = img.shape[0]  # Высота изображения
    w = img.shape[1]  # Ширина изображения

    dec_h_r, dec_w_r = recover_blocks_calc(h, w, mult_blocks_h_r, mult_blocks_w_r)  # Массивы обратных сдвигов для красного канала
    dec_h_g, dec_w_g = recover_blocks_calc(h, w, mult_blocks_h_g, mult_blocks_w_g)  # Массивы обратных сдвигов для зелёного канала
    dec_h_b, dec_w_b = recover_blocks_calc(h, w, mult_blocks_h_b, mult_blocks_w_b)  # Массивы обратных сдвигов для синего канала

    return h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b


# Дешифровка файла
def decode(img, h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b):
    if len(img.shape) < 3:
        red, green, blue = img.copy(), img.copy(), img.copy()
    else:
        if order == 0:  # Разделение изображения на RGB-каналы и отмена их перемешивания
            red, green, blue = [img[:, :, _i].copy() for _i in range(3)]
        elif order == 1:
            red, blue, green = [img[:, :, _i].copy() for _i in range(3)]
        elif order == 2:
            green, red, blue = [img[:, :, _i].copy() for _i in range(3)]
        elif order == 3:
            green, blue, red = [img[:, :, _i].copy() for _i in range(3)]
        elif order == 4:
            blue, red, green = [img[:, :, _i].copy() for _i in range(3)]
        elif order == 5:
            blue, green, red = [img[:, :, _i].copy() for _i in range(3)]

    red = (red - shift2_r) % 256  # Отмена конечного смещения цвета для каждого канала
    green = (green - shift2_g) % 256
    blue = (blue - shift2_b) % 256

    for _i in range(h):  # Отмена мультипликативного смещения цвета для каждого канала
        for j in range(w):
            red[_i][j] = DEC_R[red[_i][j]]
            green[_i][j] = DEC_G[green[_i][j]]
            blue[_i][j] = DEC_B[blue[_i][j]]

    red = (red - shift_r) % 256  # Отмена начального смещения цвета для каждого канала
    green = (green - shift_g) % 256
    blue = (blue - shift_b) % 256

    recover_blocks(red,   h, w, shift_h_r, shift_w_r, dec_h_r, dec_w_r)
    recover_blocks(green, h, w, shift_h_g, shift_w_g, dec_h_g, dec_w_g)
    recover_blocks(blue,  h, w, shift_h_b, shift_w_b, dec_h_b, dec_w_b)

    if len(img.shape) < 3:
        img = red
    else:
        img = dstack((red, green, blue))  # Объединение каналов

    return img


# Шифровка имени файла
def encode_filename(name):
    if _s_ru_ == '0':  # Транслитерация кириллицы
        name = translit(name, language_code='ru', reversed=True)

    mn = mult_name + len(name)  # Нахождение наименьшего числа, взаимно-простого с SYMB_NUM, большего чем mult_name + len(name)
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

    mn = mult_name + len(name)  # Нахождение наименьшего числа, взаимно-простого с SYMB_NUM, большего чем mult_name + len(name)
    while gcd(mn, FN_SYMB_NUM) != 1:
        mn += 1

    arr = [0] * FN_SYMB_NUM  # Дешифровочный массив
    for _i in range(FN_SYMB_NUM):
        arr[(_i + 3) * mn % FN_SYMB_NUM] = _i

    new_name = ''
    for letter in name:  # Дешифровка
        letter = FN_SYMBOLS[arr[FN_SYMBOLS.find(letter)]]
        new_name = letter + new_name

    if _s_ru_ == '0':  # Транслитерация кириллицы
        new_name = translit(new_name, language_code='ru', reversed=True)

    return new_name


# Преобразование имени файла
def rename_file(op_mode, name_mode, _base_name, _ext, outp_dir, _marker, count_correct):
    if op_mode == '1':  # При шифровке
        count_same = 1  # Счётчик файлов с таким же именем
        counter = ''
        while True:
            if name_mode == '0':
                new_name = encode_filename(_base_name + counter)
            elif name_mode == '1':
                new_name = ('{:0' + _s_format_ + '}').format(count_correct) + counter
            elif name_mode == '2':
                new_name = _marker + _base_name + counter
            elif name_mode == '3':
                new_name = _base_name + _marker + counter
            else:
                new_name = _base_name + counter
            new_name += _ext

            if new_name not in os.listdir(outp_dir):  # Если нет файлов с таким же именем, то завершаем цикл
                break
            count_same += 1
            counter = ' [' + str(count_same) + ']'  # Если уже есть файл с таким именем, то добавляется индекс
    else:  # При дешифровке
        if name_mode == '0':
            new_name = decode_filename(_base_name)
        elif name_mode == '1':
            new_name = ('{:0' + _s_format_ + '}').format(count_correct)
        elif name_mode == '2':
            new_name = _marker + _base_name
        elif name_mode == '3':
            new_name = _base_name + _marker
        else:
            new_name = _base_name

        count_same = 1  # Счётчик файлов с таким же именем
        temp_name = new_name + _ext
        while temp_name in os.listdir(outp_dir):  # Если уже есть файл с таким именем, то добавляется индекс
            count_same += 1
            temp_name = f'{new_name} [{count_same}]{_ext}'
        new_name = temp_name
    return new_name


# Обработка папки с файлами
def encrypt_dir(inp_dir, outp_dir, count_all):
    count_correct = int(_s_count_from_) - 1  # Счётчик количества обработанных файлов
    for _file_name in os.listdir(inp_dir):  # Проход по файлам
        _base_name, _ext = os.path.splitext(_file_name)
        count_all += 1

        pth = os.path.join(inp_dir, _file_name)
        isdir = os.path.isdir(pth)
        if _ext.lower() not in formats and not isdir:  # Проверка формата
            print(f'({count_all}) <{_file_name}>')
            print_exc('Unsupported file extension')
            print()
            continue
        count_correct += 1

        if _ext in ['.png', '.jpg', '.jpeg', '.bmp']:
            res_name = rename_file(op_cmd, _s_name_mode_, _base_name, '.png', outp_dir, marker, count_correct)  # Преобразование имени файла

            print(f'({count_all}) <{_file_name}>  ->  <{res_name}>')  # Вывод информации

            img = imread(os.path.join(inp_dir, _file_name))  # Считывание изображения
            if _s_print_info_ == '1':
                print(img.shape)

            outp_path = os.path.join(outp_dir, res_name)
            if op_cmd == 'E':  # Запись результата
                imsave(outp_path, encode(img).astype(uint8))
            else:
                h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b = decode_calc(img)
                img = decode(img, h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b)
                imsave(outp_path, img.astype(uint8))
            print()
        elif _ext == '.gif':
            res_name = rename_file(op_cmd, _s_name_mode_, _base_name, '', outp_dir, marker, count_correct)  # Преобразование имени файла

            print(f'({count_all}) <{_file_name}>  ->  <{res_name}>')  # Вывод информации

            res = os.path.join(outp_dir, res_name)
            if res_name not in os.listdir(outp_dir):
                os.mkdir(res)
            open(os.path.join(res, '_gif'), 'w')

            with Image.open(os.path.join(inp_dir, _file_name)) as im:
                for _i in range(im.n_frames):
                    print(f'frame {_i + 1}')
                    im.seek(_i)
                    im.save(TMP_PATH)

                    fr = imread(TMP_PATH)
                    if _s_print_info_ == '1':  # Вывод информации о считывании
                        print(fr.shape)
                    outp_path = os.path.join(res, '{:05}.png'.format(_i))
                    imsave(outp_path, encode(fr).astype(uint8))
                    print()
                imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
                os.remove(TMP_PATH)
        elif isdir and '_gif' in os.listdir(pth) and op_cmd == 'D':
            res_name = rename_file(op_cmd, _s_name_mode_, _file_name, '.gif', outp_dir, marker, count_correct)  # Преобразование имени файла

            print(f'({count_all}) <{_file_name}>  ->  <{res_name}>')  # Вывод информации

            inp_dir_tmp = os.path.join(inp_dir, _file_name)
            frames = sorted((fr for fr in os.listdir(inp_dir_tmp) if fr.endswith('.png')))
            res = os.path.join(outp_dir, res_name)

            img = imread(os.path.join(inp_dir_tmp, frames[0]))
            h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b = decode_calc(img)

            with io.get_writer(res, mode='I', duration=1/24) as writer:
                for _i in range(len(frames)):
                    print(f'frame {_i + 1}')
                    fr = imread(os.path.join(inp_dir_tmp, frames[_i]))
                    if _s_print_info_ == '1':  # Вывод информации о считывании
                        print(fr.shape)
                    img = decode(fr, h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b)
                    imsave(TMP_PATH, img.astype(uint8))
                    writer.append_data(io.imread(TMP_PATH))
                    print()
                imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
                os.remove(TMP_PATH)
            writer.close()
        elif _ext in ['.avi', '.mp4', '.webm']:
            tmp_name = rename_file(op_cmd, '1', _base_name, '', outp_dir, marker, count_correct)  # Преобразование имени файла (cv2 не воспринимает русские буквы, поэтому приходится использовать временное имя)
            res_name = rename_file(op_cmd, _s_name_mode_, _base_name, '', outp_dir, marker, count_correct)

            print(f'({count_all}) <{_file_name}>  ->  <{res_name}>')  # Вывод информации

            res = os.path.join(outp_dir, tmp_name)
            if tmp_name not in os.listdir(outp_dir):
                os.mkdir(res)
            open(os.path.join(res, '_vid'), 'w')

            vid = VideoFileClip(os.path.join(inp_dir, _file_name))
            fps = min(vid.fps, 24)
            step = 1 / fps
            count = 0
            for current_duration in arange(0, vid.duration, step):
                frame_filename = os.path.join(res, '{:06}.png'.format(count))
                vid.save_frame(TMP_PATH, current_duration)
                print(f'frame {count + 1}')

                fr = imread(TMP_PATH)
                if _s_print_info_ == '1':  # Вывод информации о считывании
                    print(fr.shape)
                imsave(frame_filename, encode(fr).astype(uint8))
                count += 1
                print()
            imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
            os.remove(TMP_PATH)

            os.rename(res, os.path.join(outp_dir, res_name))
        elif isdir and '_vid' in os.listdir(pth) and op_cmd == 'D':
            tmp_name = rename_file(op_cmd, '1', _file_name, '.mp4', outp_dir, marker, count_correct)  # Преобразование имени файла (cv2 не воспринимает русские буквы, поэтому приходится использовать временное имя)
            res_name = rename_file(op_cmd, _s_name_mode_, _file_name, '.mp4', outp_dir, marker, count_correct)

            print(f'({count_all}) <{_file_name}>  ->  <{res_name}>')  # Вывод информации

            inp_dir_tmp = os.path.join(inp_dir, _file_name)
            res = os.path.join(outp_dir, tmp_name)

            img = imread(os.path.join(inp_dir_tmp, '000000.png'))
            height = img.shape[0]
            width = img.shape[1]
            fps = 24
            video = cv2.VideoWriter(res, 0, fps, (width, height))

            h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b = decode_calc(img)

            count = 0
            for f in os.listdir(inp_dir_tmp):
                if f.endswith('.png'):
                    print(f'frame {count + 1}')
                    img = imread(os.path.join(inp_dir_tmp, f))
                    if _s_print_info_ == '1':  # Вывод информации о считывании
                        print(img.shape)
                    fr = decode(img, h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b)
                    imsave(TMP_PATH, fr.astype(uint8))
                    video.write(cv2.imread(TMP_PATH))
                    count += 1
                    print()
            imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
            os.remove(TMP_PATH)
            video.release()

            os.rename(res, os.path.join(outp_dir, res_name))
        elif isdir:
            res_name = rename_file(op_cmd, _s_name_mode_, _base_name, '', outp_dir, marker, count_correct)  # Преобразование имени файла

            print(f'({count_all}) <{_file_name}>  ->  <{res_name}>')  # Вывод информации

            new_inp_dir = os.path.join(inp_dir, _file_name)
            new_outp_dir = os.path.join(outp_dir, res_name)

            if res_name not in os.listdir(outp_dir):
                os.mkdir(new_outp_dir)

            print()

            count_all = encrypt_dir(new_inp_dir, new_outp_dir, count_all)
    return count_all


def validate_num(_value):
    return _value == "" or _value.isnumeric() or (_value[0] == '-' and _value[1:].isnumeric())


def validate_len(_value, _max_len):
    return len(_value) <= _max_len


def validate_symbols(_value, allowed_symbols):
    for _c in _value:
        if _c not in allowed_symbols:
            return False
    return True


class PopupMsgW(tk.Toplevel):
    def __init__(self, parent, msg, btn_text='OK'):
        super().__init__(parent)

        tk.Label(self, text=msg).grid(row=0, column=0)
        tk.Button(self, text=btn_text, command=self.destroy).grid(row=1, column=0)


class PopupDialogueW(tk.Toplevel):
    def __init__(self, parent, msg='Are you sure?', btn_yes='Yes', btn_no='Cancel'):
        super().__init__(parent)
        self.answer = False

        tk.Label(self, text=msg).grid(row=0, columnspan=2)
        tk.Button(self, text=btn_yes, command=self.yes).grid(row=1, column=0)
        tk.Button(self, text=btn_no, command=self.no).grid(row=1, column=2, columnspan=2)

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


class PopupInputW(tk.Toplevel):
    def __init__(self, parent, msg='Enter a value', btn_text='Confirm', allowed_symbols=None):
        super().__init__(parent)

        tk.Label(self, text=msg).grid(row=0)
        self.answer = tk.StringVar()
        if allowed_symbols is None:
            tk.Entry(self, textvariable=self.answer).grid(row=1)
        else:
            self.vcmd = (self.register(lambda _value: validate_symbols(_value, allowed_symbols)), '%P')
            tk.Entry(self, textvariable=self.answer, validate='key', validatecommand=self.vcmd).grid(row=1)
        tk.Button(self, text=btn_text, command=self.destroy).grid(row=2)

    def open(self):
        answer = self.answer.get()
        return answer


class PopupChooseW(tk.Toplevel):
    def __init__(self, parent, values, msg='Choose the one of these', btn_text='Confirm'):
        super().__init__(parent)

        tk.Label(self, text=msg).grid(row=0)
        self.answer = tk.StringVar()
        ttk.Combobox(self, textvariable=self.answer, values=values, state='readonly').grid(row=1)
        tk.Button(self, text=btn_text, command=self.destroy).grid(row=2)

    def open(self):
        answer = self.answer.get()
        return answer


class EnterKeyW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.key = tk.StringVar()

        tk.Label(self, text='v'*KEY_LEN).grid(row=1, column=1)#_s_example_key_
        tk.Label(self, text=f'Enter a key ({KEY_LEN} symbols; only latin letters, digits, - and _)').grid(row=0, columnspan=2)
        tk.Label(self, text='Enter a key:').grid(row=2, column=0, sticky='E')

        self.vcmd = (self.register(lambda _value: validate_len(_value, KEY_LEN)), '%P')
        self.entry_key = tk.Entry(self, textvariable=self.key, width=KEY_LEN, validate='key', validatecommand=self.vcmd)#, font=('Roboto', 15)
        self.btn_submit = tk.Button(self, text='Submit', command=self.check_key_and_return)

        self.entry_key.grid(row=2, column=1, sticky='W')
        self.btn_submit.grid(row=3, columnspan=2)

    def check_key_and_return(self):
        _key = self.key.get()
        _len = len(_key)
        if _len != KEY_LEN:  # Если неверная длина ключа
            PopupMsgW(self, f'Wrong length of the key: {_len}!\nShould be {KEY_LEN}')
            return
        for _i in range(_len):
            _pos = KEY_SYMBOLS.find(_key[_i])
            if _pos == -1:  # Если ключ содержит недопустимые символы
                PopupMsgW(self, f'Unexpected symbol "{_key[_i]}"!\nOnly latin letters, digits, - and _')
                return

        self.destroy()

    def open(self):
        self.grab_set()
        self.wait_window()
        _key = self.key.get()
        return key_to_bites(_key)


class SettingsW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.key = tk.StringVar()

        try:
            with open(SETTINGS_PATH, 'r') as settings_file:  # Загрузка настроек из файла
                self.name_mode, self.count_from, self.format, self.marker_enc, self.marker_dec, self.ru_letters,\
                    self.dir_enc_from, self.dir_enc_to, self.dir_dec_from, self.dir_dec_to, self.example_key,\
                    self.print_info = [settings_file.readline().strip() for _ in range(SETTINGS_NUM)]
        except FileNotFoundError:  # Если файл с настройками отсутствует, то устанавливаются настройки по умолчанию
            set_default_settings()
        self.check_settings()  # Проверка корректности настроек

        tk.Label(self, text='File names conversion mode').grid(row=0, column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Start counting files from (only for numerating file names conversion mode)').grid(row=1, column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Number of digits in numbers (only for numerating file names conversion mode)').grid(row=2, column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Marker for encoded files (only for prefix/postfix file names conversion mode)').grid(row=3, column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Marker for decoded files (only for prefix/postfix file names conversion mode)').grid(row=4, column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Russian letters processing mode').grid(row=5, column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Source folder when encoding').grid(row=6, column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Destination folder when encoding').grid(row=7, column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Source folder when decoding').grid(row=8, column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Destination folder when decoding').grid(row=9, column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Example of a key').grid(row=10, column=0, columnspan=2, sticky='E')
        tk.Label(self, text='Whether to print info').grid(row=11, column=0, columnspan=2, sticky='E')

        self.vcmd_num = (self.register(validate_num), '%P')
        self.vcmd_len = (self.register(lambda _value: validate_len(_value, KEY_LEN)), '%P')

        self.inp_name_mode    = tk.StringVar()
        self.inp_count_from   = tk.StringVar(value=self.count_from)
        self.inp_format       = tk.StringVar(value=self.format)
        self.inp_marker_enc   = tk.StringVar(value=self.marker_enc)
        self.inp_marker_dec   = tk.StringVar(value=self.marker_dec)
        self.inp_ru_letters   = tk.StringVar()
        self.inp_dir_enc_from = tk.StringVar(value=self.dir_enc_from)
        self.inp_dir_enc_to   = tk.StringVar(value=self.dir_enc_to)
        self.inp_dir_dec_from = tk.StringVar(value=self.dir_dec_from)
        self.inp_dir_dec_to   = tk.StringVar(value=self.dir_dec_to)
        self.inp_example_key  = tk.StringVar(value=self.example_key)
        self.inp_print_info   = tk.StringVar()

        self.combo_name_mode    = ttk.Combobox(self, textvariable=self.inp_name_mode, values=NAMING_MODES, state='readonly')
        self.entry_count_from   = tk.Entry(    self, textvariable=self.inp_count_from, width=10, validate='key', validatecommand=self.vcmd_num)
        self.entry_format       = tk.Entry(    self, textvariable=self.inp_format, width=10, validate='key', validatecommand=self.vcmd_num)
        self.entry_marker_enc   = tk.Entry(    self, textvariable=self.inp_marker_enc)
        self.entry_marker_dec   = tk.Entry(    self, textvariable=self.inp_marker_dec)
        self.combo_ru_letters   = ttk.Combobox(self, textvariable=self.inp_ru_letters, values=RU_LANG_MODES, state='readonly')
        self.entry_dir_enc_from = tk.Entry(    self, textvariable=self.inp_dir_enc_from, width=35)
        self.entry_dir_enc_to   = tk.Entry(    self, textvariable=self.inp_dir_enc_to, width=35)
        self.entry_dir_dec_from = tk.Entry(    self, textvariable=self.inp_dir_dec_from, width=35)
        self.entry_dir_dec_to   = tk.Entry(    self, textvariable=self.inp_dir_dec_to, width=35)
        self.entry_example_key  = tk.Entry(    self, textvariable=self.inp_example_key, width=KEY_LEN, validate='key', validatecommand=self.vcmd_len)
        self.combo_print_info   = ttk.Combobox(self, textvariable=self.inp_print_info, values=PRINT_INFO_MODES, state='readonly')

        self.combo_name_mode.current( int(self.name_mode))
        self.combo_ru_letters.current(int(self.ru_letters))
        self.combo_print_info.current(int(self.print_info))

        self.btn_def           = tk.Button(self, text='Set default settings',        command=self.set_default_settings)
        self.btn_save_custom   = tk.Button(self, text='Save your custom settings',   command=self.save_custom_settings)
        self.btn_load_custom   = tk.Button(self, text='Load your custom settings',   command=self.load_custom_settings)
        self.btn_remove_custom = tk.Button(self, text='Remove your custom settings', command=self.remove_custom_settings)
        self.btn_save  = tk.Button(self, text='Save',  command=self.save)
        self.btn_close = tk.Button(self, text='Close', command=self.close)

        self.combo_name_mode.grid(   row=0, column=2, columnspan=2, sticky='W')
        self.entry_count_from.grid(  row=1, column=2, columnspan=2, sticky='W')
        self.entry_format.grid(      row=2, column=2, columnspan=2, sticky='W')
        self.entry_marker_enc.grid(  row=3, column=2, columnspan=2, sticky='W')
        self.entry_marker_dec.grid(  row=4, column=2, columnspan=2, sticky='W')
        self.combo_ru_letters.grid(  row=5, column=2, columnspan=2, sticky='W')
        self.entry_dir_enc_from.grid(row=6, column=2, columnspan=2, sticky='W')
        self.entry_dir_enc_to.grid(  row=7, column=2, columnspan=2, sticky='W')
        self.entry_dir_dec_from.grid(row=8, column=2, columnspan=2, sticky='W')
        self.entry_dir_dec_to.grid(  row=9, column=2, columnspan=2, sticky='W')
        self.entry_example_key.grid( row=10, column=2, columnspan=2, sticky='W')
        self.combo_print_info.grid(  row=11, column=2, columnspan=2, sticky='W')

        self.btn_def.grid(          row=12, column=0)
        self.btn_save_custom.grid(  row=12, column=1)
        self.btn_load_custom.grid(  row=12, column=2)
        self.btn_remove_custom.grid(row=12, column=3)
        self.btn_save.grid(         row=13, column=1)
        self.btn_close.grid(        row=13, column=2)

    def save(self):
        self.name_mode    = str(NAMING_MODES.index(self.inp_name_mode.get()))
        self.count_from   = self.inp_count_from.get()
        self.format       = self.inp_format.get()
        self.marker_enc   = self.inp_marker_enc.get()
        self.marker_dec   = self.inp_marker_dec.get()
        self.ru_letters   = str(RU_LANG_MODES.index(self.inp_ru_letters.get()))
        self.dir_enc_from = self.inp_dir_enc_from.get()
        self.dir_enc_to   = self.inp_dir_enc_to.get()
        self.dir_dec_from = self.inp_dir_dec_from.get()
        self.dir_dec_to   = self.inp_dir_dec_to.get()
        self.example_key  = self.inp_example_key.get()
        self.print_info   = str(PRINT_INFO_MODES.index(self.inp_print_info.get()))
        self.save_settings_to_file()

    def close(self):
        window = PopupDialogueW(self, f'If you close the window, the changes will not be saved! Close settings?')
        answer = window.open()
        if answer:
            self.destroy()

    def set_default_settings(self):
        self.name_mode    = NAME_MODE_DEF
        self.count_from   = COUNT_FROM_DEF
        self.format       = FORMAT_DEF
        self.marker_enc   = MARKER_ENC_DEF
        self.marker_dec   = MARKER_DEC_DEF
        self.ru_letters   = RU_DEF_LETTERS
        self.dir_enc_from = DIR_ENC_FROM_DEF
        self.dir_enc_to   = DIR_ENC_TO_DEF
        self.dir_dec_from = DIR_DEC_FROM_DEF
        self.dir_dec_to   = DIR_DEC_TO_DEF
        self.example_key  = EXAMPLE_KEY_DEF
        self.print_info   = PRINT_INFO_DEF

        self.refresh()

    def refresh(self):
        self.inp_count_from.set(  self.count_from)
        self.inp_format.set(      self.format)
        self.inp_marker_enc.set(  self.marker_enc)
        self.inp_marker_dec.set(  self.marker_dec)
        self.inp_dir_enc_from.set(self.dir_enc_from)
        self.inp_dir_enc_to.set(  self.dir_enc_to)
        self.inp_dir_dec_from.set(self.dir_dec_from)
        self.inp_dir_dec_to.set(  self.dir_dec_to)
        self.inp_example_key.set( self.example_key)

        self.combo_name_mode.current( int(self.name_mode))
        self.combo_ru_letters.current(int(self.ru_letters))
        self.combo_print_info.current(int(self.print_info))

    def save_custom_settings(self):
        window = PopupInputW(self, 'Enter a name for save your custom settings', allowed_symbols=FN_SYMBOLS)
        self.wait_window(window)
        custom_settings_file = window.open() + '.txt'
        if custom_settings_file == '.txt':
            PopupMsgW(self, 'Incorrect name for save')
            return
        for _c in custom_settings_file:
            if _c not in FN_SYMBOLS:
                PopupMsgW(self, f'Incorrect symbol "{_c}" in the save name')
                return

        copyfile(SETTINGS_PATH, os.path.join(CUSTOM_SETTINGS_DIR, custom_settings_file))

    def choose_save(self, cmd_name):
        csf_count = 0
        csf_list = []
        for file_name in os.listdir(CUSTOM_SETTINGS_DIR):
            base_name, ext = os.path.splitext(file_name)
            if ext == '.txt':
                csf_list += [base_name]
                csf_count += 1
        if csf_count == 0:  # Если нет сохранённых настроек
            PopupMsgW(self, 'There are no saves!')
            return False, ''
        else:
            window = PopupChooseW(self, csf_list, 'Choose a save you want to ' + cmd_name)
            self.wait_window(window)
            filename = window.open() + '.txt'
            return True, filename

    def load_custom_settings(self):
        has_saves, filename = self.choose_save('load')
        if not has_saves:
            return
        custom_settings_file = os.path.join(CUSTOM_SETTINGS_DIR, filename)

        with open(custom_settings_file, 'r') as settings_file:  # Загрузка настроек из файла
            self.name_mode, self.count_from, self.format, self.marker_enc, self.marker_dec, self.ru_letters, \
                self.dir_enc_from, self.dir_enc_to, self.dir_dec_from, self.dir_dec_to, self.example_key, \
                self.print_info = [settings_file.readline().strip() for _ in range(SETTINGS_NUM)]

        self.refresh()

    def remove_custom_settings(self):
        has_saves, filename = self.choose_save('remove')
        if not has_saves:
            return
        custom_settings_file = os.path.join(CUSTOM_SETTINGS_DIR, filename)

        os.remove(custom_settings_file)

    def check_settings(self):
        if self.name_mode not in ['0', '1', '2', '3', '4']:
            self.name_mode = NAME_MODE_DEF
        if not self.count_from.isnumeric:
            self.count_from = COUNT_FROM_DEF
        if not self.format.isnumeric:
            self.format = FORMAT_DEF
        if self.ru_letters not in ['0', '1']:
            self.ru_letters = RU_DEF_LETTERS
        if len(self.example_key) != KEY_LEN or not self.example_key.isalnum:
            self.example_key = EXAMPLE_KEY_DEF
        if self.print_info not in ['0', '1']:
            self.print_info = PRINT_INFO_DEF

    def save_settings_to_file(self):
        with open(SETTINGS_PATH, 'w') as _settings_file:  # Запись исправленных настроек в файл
            _settings_file.write(
                self.name_mode + '\n' + self.count_from + '\n' + self.format + '\n' + self.marker_enc + '\n' +
                self.marker_dec + '\n' + self.ru_letters + '\n' + self.dir_enc_from + '\n' + self.dir_enc_to + '\n' +
                self.dir_dec_from + '\n' + self.dir_dec_to + '\n' + self.example_key + '\n' + self.print_info)

    def open(self):
        global _s_name_mode_, _s_count_from_, _s_format_, _s_marker_enc_, _s_marker_dec_, _s_ru_, _s_dir_enc_from_,\
            _s_dir_enc_to_, _s_dir_dec_from_, _s_dir_dec_to_, _s_example_key_, _s_print_info_

        self.grab_set()
        self.wait_window()

        _s_name_mode_, _s_count_from_, _s_format_, _s_marker_enc_, _s_marker_dec_, _s_ru_letters_,\
            _s_dir_enc_from_, _s_dir_enc_to_, _s_dir_dec_from_, _s_dir_dec_to_, _s_example_key_, _s_print_info_ =\
        self.name_mode, self.count_from, self.format, self.marker_enc, self.marker_dec, self.ru_letters,\
            self.dir_enc_from, self.dir_enc_to, self.dir_dec_from, self.dir_dec_to, self.example_key, self.print_info

        return self.name_mode, self.count_from, self.format, self.marker_enc, self.marker_dec, self.ru_letters,\
            self.dir_enc_from, self.dir_enc_to, self.dir_dec_from, self.dir_dec_to, self.example_key, self.print_info


class ManualW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
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

        self.vcmd = (self.register(validate_num), '%P')

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
            PopupMsgW(self, 'All fields should be fill')
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

    def pre_encode(self):
        res = self.set_key_vales()
        if not res:
            return
        self.mode = 'E'
        self.destroy()

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


class MainW(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Media encrypter')
        self.geometry('400x200')

        try:
            with open(SETTINGS_PATH, 'r') as settings_file:  # Загрузка настроек из файла
                self.name_mode, self.count_from, self.format, self.marker_enc, self.marker_dec, self.ru_letters,\
                    self.dir_enc_from, self.dir_enc_to, self.dir_dec_from, self.dir_dec_to, self.example_key,\
                    self.print_info = [settings_file.readline().strip() for _ in range(SETTINGS_NUM)]
        except FileNotFoundError:  # Если файл с настройками отсутствует, то устанавливаются настройки по умолчанию
            set_default_settings()
        else:
            self.check_settings()  # Проверка корректности настроек

        self.lbl_header = tk.Label(self, text='Anenokil development  presents\n' +
            (30 - len(PROGRAM_NAME)) // 2 * ' ' + PROGRAM_NAME + '\n' +
            (30 - len(PROGRAM_DATE)) // 2 * ' ' + PROGRAM_DATE)
        self.lbl_header.pack()

        self.btn_settings = tk.Button(self, text='Settings', command=self.settings)
        self.btn_settings.pack()

        self.btn_encode = tk.Button(self, text='Encode', command=self.encode)
        self.btn_encode.pack()

        self.btn_decode = tk.Button(self, text='Decode', command=self.decode)
        self.btn_decode.pack()

        self.btn_mcm = tk.Button(self, text='Debug (MCM)', command=self.mcm)
        self.btn_mcm.pack()

        self.btn_close = tk.Button(self, text='Close', command=self.quit)
        self.btn_close.pack()

    def settings(self):
        window = SettingsW(self)
        self.name_mode, self.count_from, self.format, self.marker_enc, self.marker_dec, self.ru_letters, \
            self.dir_enc_from, self.dir_enc_to, self.dir_dec_from, self.dir_dec_to, self.example_key, \
            self.print_info = window.open()
        return

    def check_settings(self):
        if self.name_mode not in ['0', '1', '2', '3', '4']:
            self.name_mode = NAME_MODE_DEF
        if not self.count_from.isnumeric:
            self.count_from = COUNT_FROM_DEF
        if not self.format.isnumeric:
            self.format = FORMAT_DEF
        if self.ru_letters not in ['0', '1']:
            self.ru_letters = RU_DEF_LETTERS
        if len(self.example_key) != KEY_LEN or not self.example_key.isalnum:
            self.example_key = EXAMPLE_KEY_DEF
        if self.print_info not in ['0', '1']:
            self.print_info = PRINT_INFO_DEF

    def _encode(self):
        global DEC_R, DEC_G, DEC_B, op_cmd, input_dir, output_dir, marker, formats
        DEC_R = [0] * 256  # Массив для отмены цветового множителя для красного канала
        DEC_G = [0] * 256  # Массив для отмены цветового множителя для зелёного канала
        DEC_B = [0] * 256  # Массив для отмены цветового множителя для синего канала
        for i in range(256):
            DEC_R[i * mult_r % 256] = i
            DEC_G[i * mult_g % 256] = i
            DEC_B[i * mult_b % 256] = i
        op_cmd = 'E'
        input_dir = self.dir_enc_from
        output_dir = self.dir_enc_to
        marker = self.marker_enc
        formats = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.avi', '.mp4', '.webm']

        print('================================== START PROCESSING ==================================')
        encrypt_dir(input_dir, output_dir, 0)
        print('=============================== PROCESSING IS FINISHED ===============================')

    def encode(self):
        window = EnterKeyW(self)
        key_bits = window.open()
        extract_key_values(key_bits)

        self._encode()

    def _decode(self):
        global DEC_R, DEC_G, DEC_B, op_cmd, input_dir, output_dir, marker, formats
        DEC_R = [0] * 256  # Массив для отмены цветового множителя для красного канала
        DEC_G = [0] * 256  # Массив для отмены цветового множителя для зелёного канала
        DEC_B = [0] * 256  # Массив для отмены цветового множителя для синего канала
        for i in range(256):
            DEC_R[i * mult_r % 256] = i
            DEC_G[i * mult_g % 256] = i
            DEC_B[i * mult_b % 256] = i
        op_cmd = 'D'
        input_dir = self.dir_dec_from
        output_dir = self.dir_dec_to
        marker = self.marker_dec
        formats = ['.png']

        print('================================== START PROCESSING ==================================')
        encrypt_dir(input_dir, output_dir, 0)
        print('=============================== PROCESSING IS FINISHED ===============================')

    def decode(self):
        window = EnterKeyW(self)
        key_bits = window.open()
        extract_key_values(key_bits)

        self._decode()

    def mcm(self):
        window = ManualW(self)
        action = window.open()

        if action == 'E':
            self._encode()
        elif action == 'D':
            self._decode()


if TMP_FILE in os.listdir(RESOURCES_DIR):  # Затирание временного файла при запуске программы, если он остался с прошлого сеанса
    open(TMP_PATH, 'w')
    os.remove(TMP_PATH)

print('======================================================================================\n')  # Вывод информации о программе
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
