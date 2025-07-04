import os
import shutil
import click

# デフォルト値を定数として定義
DEFAULT_RAW_DIR = "ARW"
DEFAULT_JPG_DIR = "JPG"
DEFAULT_RAW_EXTENSIONS = [".arw"]
DEFAULT_JPG_EXTENSIONS = [".jpg"]
DEFAULT_ORPHAN_DIR = "orphans"


def normalize_ext(filename):
    return os.path.splitext(filename)[0]


def find_raw_files(raw_dir, raw_extensions):
    """RAWファイルをステム名でマッピングして返す"""
    raw_files = {}
    if not os.path.exists(raw_dir):
        return raw_files

    for root, dirs, files in os.walk(raw_dir):
        for file in files:
            stem, ext = os.path.splitext(file)
            if ext.lower() in raw_extensions:
                raw_files[stem] = os.path.join(root, file)
    return raw_files


def log_and_echo(message, logfile=None, error=False):
    click.echo(message, err=error)
    if logfile:
        with open(logfile, "a", encoding="utf-8") as f:
            f.write(message + "\n")


def move_or_copy(src, dst, copy=False, dry_run=False, logfile=None):
    action = (
        "Would copy"
        if copy
        else "Would move" if dry_run else "Copying" if copy else "Moving"
    )
    message = f"{action}: {src} → {dst}"
    log_and_echo(f"📝 {message}", logfile)
    if not dry_run:
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if copy:
                shutil.copy2(src, dst)
            else:
                shutil.move(src, dst)
        except Exception as e:
            error_msg = f"❌ Error processing {src}: {e}"
            log_and_echo(error_msg, logfile, error=True)
            return False
    return True


def initialize_sync(
    root_dir, raw_dir, jpg_dir, raw_extensions, jpg_extensions, log_file
):
    """同期処理の初期化を行う"""
    raw_ext_list = [ext.strip() for ext in raw_extensions.split(",")]
    jpg_ext_list = [ext.strip() for ext in jpg_extensions.split(",")]

    raw_dir_path = os.path.join(root_dir, raw_dir)
    jpg_dir_path = os.path.join(root_dir, jpg_dir)
    orphan_dir = os.path.join(raw_dir_path, DEFAULT_ORPHAN_DIR)

    if log_file:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"# RAW/JPG sync log\n# Root: {os.path.abspath(root_dir)}\n")
            f.write(f"# RAW dir: {raw_dir}\n# JPG dir: {jpg_dir}\n\n")

    return raw_ext_list, jpg_ext_list, raw_dir_path, jpg_dir_path, orphan_dir


def sync_raw_to_jpg_structure(
    jpg_dir_path, raw_dir_path, raw_files, jpg_ext_list, copy, dry_run, log_file
):
    """JPG構造に合わせてRAWファイルを同期する"""
    matched_raws = set()
    log_and_echo("🔍 Matching RAW files to JPG structure...", log_file)

    for root, dirs, files in os.walk(jpg_dir_path):
        for file in files:
            if os.path.splitext(file)[1].lower() not in jpg_ext_list:
                continue

            jpg_name = os.path.splitext(file)[0]
            rel_path = os.path.relpath(root, jpg_dir_path)
            raw_dest_dir = os.path.join(raw_dir_path, rel_path)

            # 対応するRAWファイルを検索
            if jpg_name in raw_files:
                raw_src_path = raw_files[jpg_name]
                raw_file = os.path.basename(raw_src_path)
                raw_dest_path = os.path.join(raw_dest_dir, raw_file)
                move_or_copy(
                    raw_src_path,
                    raw_dest_path,
                    copy=copy,
                    dry_run=dry_run,
                    logfile=log_file,
                )
                matched_raws.add(jpg_name)
            else:
                log_and_echo(
                    f"⚠️ No RAW found for JPG: {jpg_name}", log_file, error=True
                )

    return matched_raws


def handle_orphan_files(
    raw_files, matched_raws, orphan_dir, isolate_orphans, copy, dry_run, log_file
):
    """孤立RAWファイルを処理する"""
    orphan_files = {
        stem: path for stem, path in raw_files.items() if stem not in matched_raws
    }

    if isolate_orphans and orphan_files:
        log_and_echo("🧹 Checking for orphan RAW files...", log_file)
        for stem, raw_path in orphan_files.items():
            if not raw_path.startswith(orphan_dir):
                raw_file = os.path.basename(raw_path)
                dest = os.path.join(orphan_dir, raw_file)
                move_or_copy(
                    raw_path, dest, copy=copy, dry_run=dry_run, logfile=log_file
                )
    elif orphan_files:
        log_and_echo("📋 Listing orphan RAW files (not moved):", log_file)
        for stem, raw_path in orphan_files.items():
            log_and_echo(f"  - {os.path.basename(raw_path)}", log_file)


@click.command()
@click.option(
    "--root-dir",
    type=click.Path(exists=True, file_okay=False),
    default=".",
    help="Root directory (default: current directory)",
)
@click.option(
    "--raw-dir",
    default=DEFAULT_RAW_DIR,
    help=f"RAW files directory name (default: {DEFAULT_RAW_DIR})",
)
@click.option(
    "--jpg-dir",
    default=DEFAULT_JPG_DIR,
    help=f"JPG files directory name (default: {DEFAULT_JPG_DIR})",
)
@click.option(
    "--raw-extensions",
    default=",".join(DEFAULT_RAW_EXTENSIONS),
    help=f"RAW file extensions, comma-separated (default: {','.join(DEFAULT_RAW_EXTENSIONS)})",
)
@click.option(
    "--jpg-extensions",
    default=",".join(DEFAULT_JPG_EXTENSIONS),
    help=f"JPG file extensions, comma-separated (default: {','.join(DEFAULT_JPG_EXTENSIONS)})",
)
@click.option("--copy", is_flag=True, help="Copy files instead of moving them")
@click.option(
    "--isolate-orphans",
    is_flag=True,
    help="Move unmatched RAW files into RAW/orphans/",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would happen without making any changes",
)
@click.option(
    "--log-file",
    type=click.Path(dir_okay=False, writable=True),
    help="Path to a log file to write actions",
)
def cli(
    root_dir,
    raw_dir,
    jpg_dir,
    raw_extensions,
    jpg_extensions,
    copy,
    isolate_orphans,
    dry_run,
    log_file,
):
    """Sync RAW/ folder structure to match JPG/ structure in ROOT_DIR."""
    # 初期化処理
    raw_ext_list, jpg_ext_list, raw_dir_path, jpg_dir_path, orphan_dir = (
        initialize_sync(
            root_dir, raw_dir, jpg_dir, raw_extensions, jpg_extensions, log_file
        )
    )

    # ディレクトリ存在確認
    if not os.path.exists(jpg_dir_path):
        error_msg = f"❌ JPG directory not found: {jpg_dir_path}"
        log_and_echo(error_msg, log_file, error=True)
        raise click.ClickException(error_msg)

    if not os.path.exists(raw_dir_path):
        error_msg = f"❌ RAW directory not found: {raw_dir_path}"
        log_and_echo(error_msg, log_file, error=True)
        raise click.ClickException(error_msg)

    # RAWファイルを事前に検索
    raw_files = find_raw_files(raw_dir_path, raw_ext_list)

    if not raw_files:
        warning_msg = f"⚠️ No RAW files found in {raw_dir_path}"
        log_and_echo(warning_msg, log_file, error=True)

    # JPG構造に合わせてRAWファイルを同期
    matched_raws = sync_raw_to_jpg_structure(
        jpg_dir_path, raw_dir_path, raw_files, jpg_ext_list, copy, dry_run, log_file
    )

    # 孤立RAWファイルの処理
    handle_orphan_files(
        raw_files, matched_raws, orphan_dir, isolate_orphans, copy, dry_run, log_file
    )


if __name__ == "__main__":
    cli()
