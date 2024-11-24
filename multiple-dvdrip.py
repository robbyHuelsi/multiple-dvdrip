import argparse
import subprocess
from pathlib import Path

from tqdm import tqdm

from dvdrip import DVD, ConstructTasks, TaskFilenames


def main(
    input_folder: Path,
    output_folder: Path,
    first_audio: str | None = None,
    *,
    chapter_split: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
) -> None:
    dvd_dict = {
        str(ifo.parent.relative_to(input_folder)): {
            "input_folder": ifo.parent,
            "output_folder": output_folder / ifo.parent.relative_to(input_folder),
        }
        for ifo in sorted(input_folder.rglob("VIDEO_TS.IFO"))
    }

    # Scan
    for dvd_name, dvd_data in tqdm(dvd_dict.items(), desc="Scanning DVDs"):
        dvd_data["dvd"] = DVD(dvd_data["input_folder"], verbose=verbose)
        try:
            titles = tuple(dvd_data["dvd"].ScanTitles(title_numbers=None, verbose=verbose))
        except subprocess.CalledProcessError:
            print(f"Error scanning {dvd_name}")
            continue
        tasks = tuple(ConstructTasks(titles, chapter_split=chapter_split))
        filenames = TaskFilenames(tasks, dvd_data["output_folder"], dry_run=True)
        for task, filename in zip(tasks, filenames, strict=False):
            if not (filename := Path(filename)).is_file():
                dvd_data.setdefault("tasks_filenames", []).append((task, filename))

    # Rip
    total = sum(len(dvd_data.get("tasks_filenames", [])) for dvd_data in dvd_dict.values())
    with tqdm(total=total, desc="Ripping DVDs") as pbar:
        for dvd_name, dvd_data in dvd_dict.items():
            for task, filename in dvd_data.get("tasks_filenames", []):
                filename.parent.mkdir(parents=True, exist_ok=True)
                tmp_name = filename.with_suffix(".tmp" + filename.suffix)
                if tmp_name.is_file():
                    if dry_run:
                        if verbose:
                            print(f"Would delete temporary file {tmp_name}")
                    else:
                        if verbose:
                            print(f"Deleting temporary file {tmp_name}")
                        tmp_name.unlink()
                dvd_data["dvd"].RipTitle(
                    task, str(tmp_name), first_audio=first_audio, dry_run=dry_run, verbose=verbose
                )
                if dry_run:
                    if verbose:
                        print(f"Would rename temporary file {tmp_name} to {filename}")
                else:
                    if verbose:
                        print(f"Renaming temporary file {tmp_name} to {filename}")
                    tmp_name.rename(filename)

                pbar.update(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rip all DVDs files in a folder")
    parser.add_argument("input_folder", help="The folder where the DVD files are located", type=Path)
    parser.add_argument("output_folder", help="The folder where the ripped files will be saved", type=Path)
    parser.add_argument("--first-audio", help="The native language of the DVD", type=str)
    parser.add_argument("--chapter-split", help="Split the ripped files by chapter", action="store_true")
    parser.add_argument("--dry-run", help="Don't actually rip the files", action="store_true")
    parser.add_argument("--verbose", help="Print more information", action="store_true")
    args = parser.parse_args()

    main(
        input_folder=args.input_folder,
        output_folder=args.output_folder,
        first_audio=args.first_audio,
        chapter_split=args.chapter_split,
        dry_run=args.dry_run,
    )
