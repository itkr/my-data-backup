import os
import shutil
from datetime import datetime

import click


class FileMover:

    def __init__(self, path: str):
        self.path = path

    @classmethod
    def get_file_names(cls, suffix: str, import_dir: str = ".") -> list:
        return [f.name for f in os.scandir(import_dir) if f.name.endswith(f".{suffix}")]

    @property
    def stat(self) -> datetime:
        return datetime.fromtimestamp(os.stat(self.path).st_mtime)

    @property
    def extention(self) -> str:
        return self.path.split(".")[-1]

    def _get_export_dir(self, base_dir: str = ".") -> str:
        stat = self.stat
        ymd = "-".join(
            [
                str(stat.year),
                str(stat.month).zfill(2),
                str(stat.day).zfill(2),
            ]
        )
        return os.path.join(
            base_dir,
            str(stat.year),
            f"{str(stat.month).zfill(2)}月",
            ymd,
            self.extention,
        )

    def move(self, export_dir: str = "."):
        dir_name = self._get_export_dir(export_dir)
        os.makedirs(dir_name, exist_ok=True)
        try:
            print(os.path.join(dir_name, os.path.basename(self.path)))
            shutil.move(self.path, dir_name)
            color_print(f"Moved: {self.path} -> {dir_name}", colors["green"])
        except Exception as e:
            color_print(f"Error: {e}", colors["red"])


colors = {"red": "31", "green": "32"}


def color_print(text: str, color: str):
    print(f"\033[{color}m{text}\033[0m")


def get_suffixes():
    suffixes = []
    suffixes.extend(["JPEG", "JPG", "PNG", "GIF", "BMP", "HIF", "ARW"])
    suffixes.extend(["MOV", "MP4", "MPG", "MTS", "LRF", "LRV"])
    suffixes.extend(["XML"])
    suffixes.extend(["WAV", "MP3"])
    suffixes.extend(["PSD"])
    suffixes.extend([suffix.lower() for suffix in suffixes])
    suffixes.extend([suffix.upper() for suffix in suffixes])
    return sorted(list(set(suffixes)))


def move_files(suffix: str, import_dir: str = ".", export_dir: str = "."):
    for file_name in FileMover.get_file_names(suffix, import_dir):
        FileMover(os.path.join(import_dir, file_name)).move(export_dir)


@click.command()
@click.option("--import_dir", default=".", help="Import directory")
<<<<<<< HEAD
@click.option("--export_dir", default="", help="Export directory")
def main(import_dir, export_dir):
    if not export_dir:
        export_dir = import_dir
    for suffix in get_suffixes():
=======
@click.option("--export_dir", default="export", help="Export directory")
@click.option("--suffix", default=None, help="File suffix to move")
def main(import_dir, export_dir, suffix):
    suffixes = get_suffixes() if suffix is None else [suffix]
    for suffix in suffixes:
>>>>>>> d0106c5 (サフィックスを引数に追加)
        move_files(suffix, import_dir, export_dir)


if __name__ == "__main__":
    main()
