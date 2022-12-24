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
RU_DEF = '0'
DIR_ENC_FROM_DEF = 'f_src'
DIR_ENC_TO_DEF = 'f_enc'
DIR_DEC_FROM_DEF = 'f_enc'
DIR_DEC_TO_DEF = 'f_dec'
EXAMPLE_KEY_DEF = 'This_Is-The_Example-Of_A-Correct_Key-012'
PRINT_INFO_DEF = '0'

# Варианты настроек с перечислимым типом
NAMING_MODES = ['encryption', 'numeration', 'add prefix', 'add postfix', 'don`t change']  # Варианты настройки именования выходных файлов
RU_LANG_MODES = ['transliterate to latin', 'allowed']  # Варианты настройки обработки кириллических букв
PRINT_INFO_MODES = ['don`t print', 'print']  # Варианты настройки печати информации

""" Ключ """
KEY_SYMBOLS = "0123456789-abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # Допустимые в ключе символы
KEY_LEN = 40  # Длина ключа


# Проверка, корректировка и запись в файл настроек
def change_settings():
    global _s_name_mode_, _s_count_from_, _s_format_, _s_ru_, _s_example_key_, _s_print_info_

    if _s_name_mode_ not in ['0', '1', '2', '3', '4']:
        _s_name_mode_ = NAME_MODE_DEF
    if not _s_count_from_.isnumeric:
        _s_count_from_ = COUNT_FROM_DEF
    if not _s_format_.isnumeric:
        _s_format_ = FORMAT_DEF
    if _s_ru_ not in ['0', '1']:
        _s_ru_ = RU_DEF
    if len(_s_example_key_) != KEY_LEN or not _s_example_key_.isalnum:
        _s_example_key_ = EXAMPLE_KEY_DEF
    if _s_print_info_ not in ['0', '1']:
        _s_print_info_ = PRINT_INFO_DEF

    with open(SETTINGS_PATH, 'w') as settingsF:  # Запись исправленных настроек в файл
        settingsF.write(_s_name_mode_ + '\n' + _s_count_from_ + '\n' + _s_format_ + '\n' + _s_marker_enc_ + '\n' + _s_marker_dec_ + '\n' + _s_ru_ + '\n' +
                        _s_dir_enc_from_ + '\n' + _s_dir_enc_to_ + '\n' + _s_dir_dec_from_ + '\n' + _s_dir_dec_to_ + '\n' + _s_example_key_ + '\n' + _s_print_info_)


# Установка значений по умолчанию для всех настроек
def set_default_settings():
    global _s_name_mode_, _s_count_from_, _s_format_, _s_marker_enc_, _s_marker_dec_, _s_ru_, _s_dir_enc_from_,\
        _s_dir_enc_to_, _s_dir_dec_from_, _s_dir_dec_to_, _s_example_key_, _s_print_info_

    _s_name_mode_ = NAME_MODE_DEF
    _s_count_from_ = COUNT_FROM_DEF
    _s_format_ = FORMAT_DEF
    _s_marker_enc_ = MARKER_ENC_DEF
    _s_marker_dec_ = MARKER_DEC_DEF
    _s_ru_ = RU_DEF
    _s_dir_enc_from_ = DIR_ENC_FROM_DEF
    _s_dir_enc_to_ = DIR_ENC_TO_DEF
    _s_dir_dec_from_ = DIR_DEC_FROM_DEF
    _s_dir_dec_to_ = DIR_DEC_TO_DEF
    _s_example_key_ = EXAMPLE_KEY_DEF
    _s_print_info_ = PRINT_INFO_DEF


# Вывод текущих настроек
def print_settings():
    print('====================================== SETTINGS ======================================')
    print('   File names conversation mode: ' + NAMING_MODES[int(_s_name_mode_)])
    print('            Account starts with: ' + _s_count_from_ + ' [only for numerating file names conversation mode]')
    print('    Number of digits in numbers: ' + _s_format_ + ' [only for numerating file names conversation mode]')
    print('       Marker for encoded files: ' + _s_marker_enc_ + ' [only for prefix/postfix file names conversation mode]')
    print('       Marker for decoded files: ' + _s_marker_dec_ + ' [only for prefix/postfix file names conversation mode]')
    print(' Russian letter processing mode: ' + RU_LANG_MODES[int(_s_ru_)])
    print('     Source folder for encoding: ' + _s_dir_enc_from_)
    print('Destination folder for encoding: ' + _s_dir_enc_to_)
    print('     Source folder for decoding: ' + _s_dir_dec_from_)
    print('Destination folder for decoding: ' + _s_dir_dec_to_)
    print('             Example of the key: ' + _s_example_key_)
    print('          Whether to print info: ' + PRINT_INFO_MODES[int(_s_print_info_)])


# Ввод ключа и преобразование его в массив битов
def key_processing():
    print(' ' * 28 + _s_example_key_)  # Тестовый ключ
    print(' ' * 28 + 'v' * KEY_LEN)
    key = input('Enter the key (' + str(KEY_LEN) + ' symbols): ').lower()  # Ввод ключа
    if len(key) != KEY_LEN:  # Если неверная длина ключа
        print_exc('Wrong length of the password')
        print('======================================================================================')
        return key_processing()

    bits = [[0] * KEY_LEN for i in range(6)]  # Преобразование ключа в массив битов (каждый символ - в 6 битов)
    for i in range(KEY_LEN):
        temp = KEY_SYMBOLS.find(key[i])
        if temp == -1:  # Если ключ содержит недопустимые символы
            print_exc(f'Incorrect symbol "{key[i]}" (only latin letters, digits, - and _)')
            print('======================================================================================')
            return key_processing()
        for j in range(6):
            bits[j][i] = temp // (2 ** j) % 2
    return bits


# Нахождение числа по его битам
def bites_sum(*bites):
    s = 0
    for i in bites:
        if type(i) == list:  # Можно передавать массивы
            for j in i:
                s = 2 * s + j
        else:  # А можно числа
            s = 2 * s + i
    return s


# Разделение полотна на блоки и их перемешивание
def mix_blocks(img, mult_h, mult_w, shift_h, shift_w):
    h = img.shape[0]  # Высота изображения
    w = img.shape[1]  # Ширина изображения

    while gcd(mult_h, h) != 1 or mult_h % h == 1:  # Нахождение наименьшего числа, взаимно-простого с h, большего чем mult_h, дающего при делении на h в остатке 1
        mult_h += 1
    while gcd(mult_w, w) != 1 or mult_w % w == 1:  # Нахождение наименьшего числа, взаимно-простого с w, большего чем mult_w, дающего при делении на w в остатке 1
        mult_w += 1
    if _s_print_info_ == '1':
        print(str(h) + 'x' + str(w) + ':', mult_h, mult_w)

    img_tmp = img.copy()
    for i in range(h):
        for j in range(w):
            jj = (j + shift_w * i) % w
            ii = (i + shift_h * jj) % h
            iii = (ii * mult_h) % h
            jjj = (jj * mult_w) % w
            img[iii][jjj] = img_tmp[i][j]


# Шифровка файла
def encode(img):
    if len(img.shape) < 3:
        red, green, blue = img.copy(), img.copy(), img.copy()
    else:
        red, green, blue = [img[:, :, i].copy() for i in range(3)]  # Разделение изображения на RGB-каналы

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
        if (order == 0):  # Перемешивание и объединение каналов
            img = dstack((red, green, blue))
        elif (order == 1):
            img = dstack((red, blue, green))
        elif (order == 2):
            img = dstack((green, red, blue))
        elif (order == 3):
            img = dstack((green, blue, red))
        elif (order == 4):
            img = dstack((blue, red, green))
        elif (order == 5):
            img = dstack((blue, green, red))

    return img


# Вычисление параметров для recover_blocks
def recover_blocks_calc(h, w, mult_h, mult_w):
    while gcd(mult_h, h) != 1 or mult_h % h == 1:  # Нахождение наименьшего числа, взаимно-простого с h, большего чем mult_h, дающего при делении на h в остатке 1
        mult_h += 1
    while gcd(mult_w, w) != 1 or mult_w % w == 1:  # Нахождение наименьшего числа, взаимно-простого с w, большего чем mult_w, дающего при делении на w в остатке 1
        mult_w += 1
    if _s_print_info_ == '1':
        print(str(h) + 'x' + str(w) + ':', mult_h, mult_w)

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
        if (order == 0):  # Разделение изображения на RGB-каналы и отмена их перемешивания
            red, green, blue = [img[:, :, i].copy() for i in range(3)]
        elif (order == 1):
            red, blue, green = [img[:, :, i].copy() for i in range(3)]
        elif (order == 2):
            green, red, blue = [img[:, :, i].copy() for i in range(3)]
        elif (order == 3):
            green, blue, red = [img[:, :, i].copy() for i in range(3)]
        elif (order == 4):
            blue, red, green = [img[:, :, i].copy() for i in range(3)]
        elif (order == 5):
            blue, green, red = [img[:, :, i].copy() for i in range(3)]

    red = (red - shift2_r) % 256  # Отмена конечного смещения цвета для каждого канала
    green = (green - shift2_g) % 256
    blue = (blue - shift2_b) % 256

    for i in range(h):  # Отмена мультипликативного смещения цвета для каждого канала
        for j in range(w):
            red[i][j] = DEC_R[red[i][j]]
            green[i][j] = DEC_G[green[i][j]]
            blue[i][j] = DEC_B[blue[i][j]]

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
    new_name = '_' + new_name + '_'  # Защита от потери крайних пробелов
    return new_name


# Дешифровка имени файла
def decode_filename(name):
    name = name[1:-1]  # Защита от потери крайних пробелов

    mn = mult_name + len(name)  # Нахождение наименьшего числа, взаимно-простого с SYMB_NUM, большего чем mult_name + len(name)
    while gcd(mn, FN_SYMB_NUM) != 1:
        mn += 1

    arr = [0] * FN_SYMB_NUM  # Дешифровочный массив
    for i in range(FN_SYMB_NUM):
        arr[(i + 3) * mn % FN_SYMB_NUM] = i

    new_name = ''
    for letter in name:  # Дешифровка
        letter = FN_SYMBOLS[arr[FN_SYMBOLS.find(letter)]]
        new_name = letter + new_name

    if _s_ru_ == '0':  # Транслитерация кириллицы
        new_name = translit(new_name, language_code='ru', reversed=True)

    return new_name


# Преобразование имени файла
def rename_file(op_mode, name_mode, base_name, ext, outp_dir, marker, count_correct):
    if op_mode == '1':  # При шифровке
        count_same = 1  # Счётчик файлов с таким же именем
        counter = ''
        while True:
            if name_mode == '0':
                new_name = encode_filename(base_name + counter)
            elif name_mode == '1':
                new_name = ('{:0' + _s_format_ + '}').format(count_correct) + counter
            elif name_mode == '2':
                new_name = marker + base_name + counter
            elif name_mode == '3':
                new_name = base_name + marker + counter
            else:
                new_name = base_name + counter
            new_name += ext

            if new_name not in os.listdir(outp_dir):  # Если нет файлов с таким же именем, то завершаем цикл
                break
            count_same += 1
            counter = ' [' + str(count_same) + ']'  # Если уже есть файл с таким именем, то добавляется индекс
    else:  # При дешифровке
        if name_mode == '0':
            new_name = decode_filename(base_name)
        elif name_mode == '1':
            new_name = ('{:0' + _s_format_ + '}').format(count_correct)
        elif name_mode == '2':
            new_name = marker + base_name
        elif name_mode == '3':
            new_name = base_name + marker
        else:
            new_name = base_name

        count_same = 1  # Счётчик файлов с таким же именем
        temp_name = new_name + ext
        while temp_name in os.listdir(outp_dir):  # Если уже есть файл с таким именем, то добавляется индекс
            count_same += 1
            temp_name = new_name + ' [' + str(count_same) + ']' + ext
        new_name = temp_name
    return new_name


# Обработка папки с файлами
def encrypt_dir(inp_dir, outp_dir, count_all):
    count_correct = int(_s_count_from_) - 1  # Счётчик количества обработанных файлов
    for file_name in os.listdir(inp_dir):  # Проход по файлам
        base_name, ext = os.path.splitext(file_name)
        count_all += 1

        pth = os.path.join(inp_dir, file_name)
        isdir = os.path.isdir(pth)
        if ext.lower() not in formats and not isdir:  # Проверка формата
            print(f'({count_all}) <{file_name}>')
            print_exc('Unsupported file extension')
            print()
            continue
        count_correct += 1

        if ext in ['.png', '.jpg', '.jpeg', '.bmp']:
            res_name = rename_file(op_cmd, _s_name_mode_, base_name, '.png', outp_dir, marker, count_correct)  # Преобразование имени файла

            print(f'({count_all}) <{file_name}>  ->  <{res_name}>')  # Вывод информации

            img = imread(os.path.join(inp_dir, file_name))  # Считывание изображения
            if _s_print_info_ == '1':
                print(img.shape)

            outp_path = os.path.join(outp_dir, res_name)
            if op_cmd == '1':  # Запись результата
                imsave(outp_path, encode(img).astype(uint8))
            else:
                h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b = decode_calc(img)
                img = decode(img, h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b)
                imsave(outp_path, img.astype(uint8))
            print()
        elif ext == '.gif':
            res_name = rename_file(op_cmd, _s_name_mode_, base_name, '', outp_dir, marker, count_correct)  # Преобразование имени файла

            print(f'({count_all}) <{file_name}>  ->  <{res_name}>')  # Вывод информации

            res = os.path.join(outp_dir, res_name)
            if res_name not in os.listdir(outp_dir):
                os.mkdir(res)
            open(os.path.join(res, '_gif'), 'w')

            with Image.open(os.path.join(inp_dir, file_name)) as im:
                for i in range(im.n_frames):
                    print(f'frame {i + 1}')
                    im.seek(i)
                    im.save(TMP_PATH)

                    fr = imread(TMP_PATH)
                    if _s_print_info_ == '1':  # Вывод информации о считывании
                        print(fr.shape)
                    outp_path = os.path.join(res, '{:05}.png'.format(i))
                    imsave(outp_path, encode(fr).astype(uint8))
                    print()
                imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
                os.remove(TMP_PATH)
        elif isdir and '_gif' in os.listdir(pth) and op_cmd == '2':
            res_name = rename_file(op_cmd, _s_name_mode_, file_name, '.gif', outp_dir, marker, count_correct)  # Преобразование имени файла

            print(f'({count_all}) <{file_name}>  ->  <{res_name}>')  # Вывод информации

            inp_dir_tmp = os.path.join(inp_dir, file_name)
            frames = sorted((fr for fr in os.listdir(inp_dir_tmp) if fr.endswith('.png')))
            res = os.path.join(outp_dir, res_name)

            img = imread(os.path.join(inp_dir_tmp, frames[0]))
            h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b = decode_calc(img)

            with io.get_writer(res, mode='I', duration=1/24) as writer:
                for i in range(len(frames)):
                    print(f'frame {i + 1}')
                    fr = imread(os.path.join(inp_dir_tmp, frames[i]))
                    if _s_print_info_ == '1':  # Вывод информации о считывании
                        print(fr.shape)
                    img = decode(fr, h, w, dec_h_r, dec_w_r, dec_h_g, dec_w_g, dec_h_b, dec_w_b)
                    imsave(TMP_PATH, img.astype(uint8))
                    writer.append_data(io.imread(TMP_PATH))
                    print()
                imsave(TMP_PATH, fr[0:1, 0:1] * 0)  # Затирание временного файла
                os.remove(TMP_PATH)
            writer.close()
        elif ext in ['.avi', '.mp4', '.webm']:
            tmp_name = rename_file(op_cmd, '1', base_name, '', outp_dir, marker, count_correct)  # Преобразование имени файла (cv2 не воспринимает русские буквы, поэтому приходится использовать временное имя)
            res_name = rename_file(op_cmd, _s_name_mode_, base_name, '', outp_dir, marker, count_correct)

            print(f'({count_all}) <{file_name}>  ->  <{res_name}>')  # Вывод информации

            res = os.path.join(outp_dir, tmp_name)
            if tmp_name not in os.listdir(outp_dir):
                os.mkdir(res)
            open(os.path.join(res, '_vid'), 'w')

            vid = VideoFileClip(os.path.join(inp_dir, file_name))
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
        elif isdir and '_vid' in os.listdir(pth) and op_cmd == '2':
            tmp_name = rename_file(op_cmd, '1', file_name, '.mp4', outp_dir, marker, count_correct)  # Преобразование имени файла (cv2 не воспринимает русские буквы, поэтому приходится использовать временное имя)
            res_name = rename_file(op_cmd, _s_name_mode_, file_name, '.mp4', outp_dir, marker, count_correct)

            print(f'({count_all}) <{file_name}>  ->  <{res_name}>')  # Вывод информации

            inp_dir_tmp = os.path.join(inp_dir, file_name)
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
            res_name = rename_file(op_cmd, _s_name_mode_, base_name, '', outp_dir, marker, count_correct)  # Преобразование имени файла

            print(f'({count_all}) <{file_name}>  ->  <{res_name}>')  # Вывод информации

            new_inp_dir = os.path.join(inp_dir, file_name)
            new_outp_dir = os.path.join(outp_dir, res_name)

            if res_name not in os.listdir(outp_dir):
                os.mkdir(new_outp_dir)

            print()

            count_all = encrypt_dir(new_inp_dir, new_outp_dir, count_all)
    return count_all


# Вывод сообщения об ошибке
def print_exc(s):
    print('{!!!} ' + s + ' {!!!}')


if TMP_FILE in os.listdir(RESOURCES_DIR):  # Затирание временного файла при запуске программы, если он остался с прошлого сеанса
    open(TMP_PATH, 'w')
    os.remove(TMP_PATH)

print('======================================================================================\n')  # Вывод информации о программе
print('                            Anenokil development  presents')
print('                                Media encrypter v5.5.0')
print('                                   26.11.2022 14:49\n')

try:
    with open(SETTINGS_PATH, 'r') as settingsF:  # Загрузка настроек из файла
        _s_name_mode_, _s_count_from_, _s_format_, _s_marker_enc_, _s_marker_dec_, _s_ru_, _s_dir_enc_from_,\
            _s_dir_enc_to_, _s_dir_dec_from_, _s_dir_dec_to_, _s_example_key_, _s_print_info_ =\
            [settingsF.readline().strip() for i in range(SETTINGS_NUM)]
except FileNotFoundError:  # Если файл с настройками отсутствует, то устанавливаются настройки по умолчанию
    set_default_settings()
change_settings()  # Проверка корректности настроек
print_settings()  # Вывод текущих настроек

while True:  # Обработка пользовательских команд
    while True:  # Ввод команды
        print('======================================================================================')
        print('Choose one of the options:')
        print('[1] Start encode')
        print('[2] Start decode')
        print('[S] Edit settings')
        print('[T] Terminate program')
        print('[MCM] Enter manual control mode')
        op_cmd = input()
        if op_cmd.upper() in ['1', '2', 'S', 'T', 'MCM']:
            break
        print_exc('Incorrect option')

    if op_cmd.upper() == 'S':  # Изменение настроек
        while True:
            print('=================================== EDIT  SETTINGS ===================================')
            print('[0] File names conversation mode')
            print('[1] What number does the account start with (only for numerating file names conversation mode)')
            print('[2] Number of digits in numbers (only for numerating file names conversation mode)')
            print('[3] Marker for encoded files (only for prefix/postfix file names conversation mode)')
            print('[4] Marker for decoded files (only for prefix/postfix file names conversation mode)')
            print('[5] Russian letter processing mode')
            print('[6] Source folder for encoding')
            print('[7] Destination folder for encoding')
            print('[8] Source folder for decoding')
            print('[9] Destination folder for decoding')
            print('[10] An example of the key')
            print('[11] Whether to print info')
            print('[SV] Save your custom settings')
            print('[LD] Load your custom settings')
            print('[RM] Remove your custom settings')
            print('[DEF] Set default settings')
            print('[BACK] Return back')

            cmd = input()  # Выбор действия
            if cmd == '0':
                for i in range(len(NAMING_MODES)):
                    print(f'[{i}] {NAMING_MODES[i]}')
                _s_name_mode_ = input('Choose one of the suggested: ')
            elif cmd == '1':
                _s_count_from_ = input('Enter what number does the account start with: ')
            elif cmd == '2':
                _s_format_ = input('Enter number of digits in numbers: ')
            elif cmd == '3':
                _s_marker_enc_ = input('Enter marker for encoded files: ')
            elif cmd == '4':
                _s_marker_dec_ = input('Enter marker for decoded files: ')
            elif cmd == '5':
                for i in range(len(RU_LANG_MODES)):
                    print(f'[{i}] {RU_LANG_MODES[i]}')
                _s_ru_ = input('Choose one of the suggested: ')
            elif cmd == '6':
                _s_dir_enc_from_ = input('Enter source folder for encoding: ')
            elif cmd == '7':
                _s_dir_enc_to_ = input('Enter destination folder for encoding: ')
            elif cmd == '8':
                _s_dir_dec_from_ = input('Enter source folder for decoding: ')
            elif cmd == '9':
                _s_dir_dec_to_ = input('Enter destination folder for decoding: ')
            elif cmd == '10':
                print(' ' * 63 + 'v' * KEY_LEN)
                _s_example_key_ = input('Enter an example of the key (!!don`t enter your real key!!): ')
            elif cmd == '11':
                for i in range(len(PRINT_INFO_MODES)):
                    print(f'[{i}] {PRINT_INFO_MODES[i]}')
                _s_print_info_ = input('Choose one of the suggested: ')
            elif cmd.upper() == 'SV':
                custom_settings_file = input('Enter a name for save your custom settings: ') + '.txt'
                if '..\\' in custom_settings_file:
                    print_exc('You can`t use ..\\')
                    continue
                if '../' in custom_settings_file:
                    print_exc('You can`t use ../')
                    continue
                if custom_settings_file == '.txt':
                    print_exc('Incorrect name for save')
                    continue

                hasIncSymb = False
                for c in custom_settings_file:
                    if c not in FN_SYMBOLS:
                        print_exc(f'Incorrect symbol "{c}" in save name')
                        hasIncSymb = True
                        break
                if hasIncSymb:
                    continue

                copyfile(SETTINGS_PATH, os.path.join(CUSTOM_SETTINGS_DIR, custom_settings_file))
            elif cmd.upper() == 'LD':
                csf_count = 0
                csf_list = []
                for file_name in os.listdir(CUSTOM_SETTINGS_DIR):
                    base_name, ext = os.path.splitext(file_name)
                    if ext == '.txt':
                        print(f'[{csf_count}] <{base_name}>')
                        csf_list += [base_name]
                        csf_count += 1
                if csf_count == 0:  # Если нет сохранённых настроек
                    print('There are no saves here')
                    continue
                print('[CANCEL] Return back')

                csf_index = input('Choose a save you want to load: ')
                if csf_index.upper() == 'CANCEL':
                    continue
                try:
                    csf_index = int(csf_index)
                    custom_settings_file = csf_list[csf_index] + '.txt'
                except (ValueError, IndexError):
                    print_exc(f'There is no such option as "{csf_index}"')
                    continue
                custom_settings_file = os.path.join(CUSTOM_SETTINGS_DIR, custom_settings_file)

                with open(custom_settings_file, 'r') as settingsF:   # Загрузка настроек
                    _s_name_mode_, _s_count_from_, _s_format_, _s_marker_enc_, _s_marker_dec_, _s_ru_, _s_dir_enc_from_,\
                        _s_dir_enc_to_, _s_dir_dec_from_, _s_dir_dec_to_, _s_example_key_, _s_print_info_ = \
                        [settingsF.readline().strip() for i in range(SETTINGS_NUM)]
            elif cmd.upper() == 'RM':
                csf_count = 0
                csf_list = []
                for file_name in os.listdir(CUSTOM_SETTINGS_DIR):
                    base_name, ext = os.path.splitext(file_name)
                    if ext == '.txt':
                        print(f'[{csf_count}] <{base_name}>')
                        csf_list += [base_name]
                        csf_count += 1
                if csf_count == 0:  # Если нет сохранённых настроек
                    print('There are no saves here')
                    continue
                print('[CANCEL] Return back')

                csf_index = input('Choose a save you want to remove: ')
                if csf_index.upper() == 'CANCEL':
                    continue
                try:
                    csf_index = int(csf_index)
                    custom_settings_file = csf_list[csf_index] + '.txt'
                except (ValueError, IndexError):
                    print_exc(f'There is no such option as "{csf_index}"')
                    continue
                custom_settings_file = os.path.join(CUSTOM_SETTINGS_DIR, custom_settings_file)

                os.remove(custom_settings_file)
            elif cmd.upper() == 'DEF':
                set_default_settings()
            elif cmd.upper() == 'BACK':
                break
            else:
                print_exc('Incorrect input')

            change_settings()  # Внесение изменений в настройки
            print_settings()  # Вывод текущих настроек
    elif op_cmd.upper() == 'T':  # Завершение работы
        print('======================================================================================')
        print('The program is terminated')
        exit(7)
    elif op_cmd.upper() == 'MCM':  # Режим ручного управления (отладка)
        print('======================================================================================')
        mult_blocks_h_r = int(input('Enter the H multiplier for R: '))  # Множитель блоков по горизонтали для красного канала
        mult_blocks_h_g = int(input('Enter the H multiplier for G: '))  # Множитель блоков по горизонтали для зелёного канала
        mult_blocks_h_b = int(input('Enter the H multiplier for B: '))  # Множитель блоков по горизонтали для синего канала
        mult_blocks_w_r = int(input('Enter the W multiplier for R: '))  # Множитель блоков по вертикали для красного канала
        mult_blocks_w_g = int(input('Enter the W multiplier for G: '))  # Множитель блоков по вертикали для зелёного канала
        mult_blocks_w_b = int(input('Enter the W multiplier for B: '))  # Множитель блоков по вертикали для синего канала
        shift_h_r = int(input('Enter the H shift for R: '))  # Сдвиг блоков по горизонтали для красного канала
        shift_h_g = int(input('Enter the H shift for G: '))  # Сдвиг блоков по горизонтали для зелёного канала
        shift_h_b = int(input('Enter the H shift for B: '))  # Сдвиг блоков по горизонтали для синего канала
        shift_w_r = int(input('Enter the W shift for R: '))  # Сдвиг блоков по вертикали для красного канала
        shift_w_g = int(input('Enter the W shift for G: '))  # Сдвиг блоков по вертикали для зелёного канала
        shift_w_b = int(input('Enter the W shift for B: '))  # Сдвиг блоков по вертикали для синего канала
        order = int(input('Enter channels order: ')) % 6  # Порядок следования каналов после перемешивания
        shift_r = int(input('Enter the primary color shift for R: '))  # Первичное смещение цвета для красного канала
        shift_g = int(input('Enter the primary color shift for G: '))  # Первичное смещение цвета для зелёного канала
        shift_b = int(input('Enter the primary color shift for B: '))  # Первичное смещение цвета для синего канала
        mult_r = int(input('Enter the color multiplier for R: '))  # Цветовой множитель для красного канала
        mult_g = int(input('Enter the color multiplier for G: '))  # Цветовой множитель для зелёного канала
        mult_b = int(input('Enter the color multiplier for B: '))  # Цветовой множитель для синего канала
        shift2_r = int(input('Enter the secondary color shift for R: '))  # Вторичное смещение цвета для красного канала
        shift2_g = int(input('Enter the secondary color shift for G: '))  # Вторичное смещение цвета для зелёного канала
        shift2_b = int(input('Enter the secondary color shift for B: '))  # Вторичное смещение цвета для синего канала
        mult_name = int(input('Enter the multiplier for filenames: '))  # Сдвиг букв в имени файла

        while True:  # Ввод команды
            print('======================================================================================')
            print('Choose one of the options:')
            print('[1] Start encode')
            print('[2] Start decode')
            op_cmd = input()
            if op_cmd in ['1', '2']:
                break
            print_exc('Incorrect option')
        break
    else:
        print('======================================================================================')
        b = key_processing()

        # Определение ключевых значений шифра
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
        break

DEC_R = [0] * 256  # Массив для отмены цветового множителя для красного канала
DEC_G = [0] * 256  # Массив для отмены цветового множителя для зелёного канала
DEC_B = [0] * 256  # Массив для отмены цветового множителя для синего канала
for i in range(256):
    DEC_R[i * mult_r % 256] = i
    DEC_G[i * mult_g % 256] = i
    DEC_B[i * mult_b % 256] = i

if op_cmd == '1':  # Определение некоторых параметров обработки файлов в зависимости от режима работы
    input_dir = _s_dir_enc_from_
    output_dir = _s_dir_enc_to_
    marker = _s_marker_enc_
    formats = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.avi', '.mp4', '.webm']
else:
    input_dir = _s_dir_dec_from_
    output_dir = _s_dir_dec_to_
    marker = _s_marker_dec_
    formats = ['.png']

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
print('================================== START PROCESSING ==================================')

encrypt_dir(input_dir, output_dir, 0)  # Обработка папки с файлами

print('=============================== PROCESSING IS FINISHED ===============================')

# v1.0.0
# v2.0.0 - добавлены настройки
# v3.0.0 - добавлена обработка гифок
# v4.0.0 - добавлена обработка видео
# v5.0.0 - добавлена обработка вложенных папок
