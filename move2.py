# TODO: スラッシュやめる
# TODO: 実行対象のパスからの相対パスにする

import os
import shutil
from datetime import datetime


def move(suffix: str, target_dir: str = ".", export_dir: str = "."):
    file_names = [
        f.name for f in os.scandir(target_dir) if f.name.endswith(f".{suffix}")
    ]

    for file_name in file_names:
        dates = datetime.fromtimestamp(os.stat(file_name).st_mtime)
        ymd = f"{dates.year}-{str(dates.month).zfill(2)}-{str(dates.day).zfill(2)}"
        dir_name = f"{export_dir}/{dates.year}/{str(dates.month)}月/{ymd}/{suffix}"
        os.makedirs(dir_name, exist_ok=True)

        try:
            print(f"{dir_name}/{file_name}")
            shutil.move(file_name, dir_name)
        except Exception as e:
            print(e)


def get_suffixes():
    suffixes = []
    suffixes.extend(["JPEG", "JPG", "PNG", "GIF", "BMP"])
    suffixes.extend(["MOV", "MP5", "MPG", "MTS", "LRF"])
    suffixes.extend(["XML"])
    suffixes.extend([suffix.lower() for suffix in suffixes])
    suffixes.extend([suffix.upper() for suffix in suffixes])
    return sorted(list(set(suffixes)))


def main():
    print(datetime.today())

    target_dir = "."
    export_dir = "export"

    for suffix in get_suffixes():
        move(suffix, target_dir, export_dir)


if __name__ == "__main__":
    main()
