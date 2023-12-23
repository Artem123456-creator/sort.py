import sys
import scan
import shutil
import re
from pathlib import Path

# Нормалізація
UKRAINIAN_SYMBOLS = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")

TRANS = {}

for key, value in zip(UKRAINIAN_SYMBOLS, TRANSLATION):
    TRANS[ord(key)] = value
    TRANS[ord(key.upper())] = value.upper()

def custom_normalize(name: str) -> str:
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', '_', new_name)
    return f"{new_name}.{'.'.join(extension)}"

# Функція для обробки  файлів
def handle_file(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)
    path.replace(target_folder / custom_normalize(path.name))

# Функція для обробки архівів
def handle_archive(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)

    new_name = custom_normalize(path.name.replace(".zip", ''))

    archive_folder = target_folder / new_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path.resolve()), str(archive_folder.resolve()))
    except shutil.ReadError:
        archive_folder.rmdir()
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        return
    path.unlink()

# Функція для видалення порожніх папок
def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass

# Основна функція
def main(folder_path):
    print(folder_path)
    scan.scan(folder_path)

    # Обробка різних типів файлів
    for file in scan.jpeg_files:
        handle_file(file, folder_path, "JPEG")

    for file in scan.jpg_files:
        handle_file(file, folder_path, "JPG")

    for file in scan.png_files:
        handle_file(file, folder_path, "PNG")

    for file in scan.txt_files:
        handle_file(file, folder_path, "TXT")

    for file in scan.docx_files:
        handle_file(file, folder_path, "DOCX")

    for file in scan.others:
        handle_file(file, folder_path, "OTHER")

    for file in scan.archives:
        handle_archive(file, folder_path, "ARCHIVE")

    remove_empty_folders(folder_path)

if __name__ == '__main__':
    # Отримання шляху з командної строки
    path = sys.argv[1]
    print(f'Start in {path}')

    folder = Path(path)
    main(folder.resolve())

    # Виведення результатів сканування
    print(f"jpeg: {scan.jpeg_files}")
    print(f"jpg: {scan.jpg_files}")
    print(f"png: {scan.png_files}")
    print(f"txt: {scan.txt_files}")
    print(f"docx: {scan.docx_files}")
    print(f"archive: {scan.archives}")
    print(f"unknown: {scan.others}")
    print(f"All extensions: {scan.extensions}")
    print(f"Unknown extensions: {scan.unknown}")
    print(f"Folder: {scan.folders}")

    