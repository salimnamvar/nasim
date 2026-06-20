import argparse
import os
from pathlib import Path


def merge_documents(input_paths, output_file):
    with open(output_file, "w", encoding="utf-8") as outfile:
        for path_str in input_paths:
            root_dir = Path(path_str)

            if not root_dir.exists():
                print(f"Warning: {path_str} does not exist. Skipping.")
                continue

            # Walk through the directory
            for root, dirs, files in os.walk(root_dir):
                current_path = Path(root)

                # Identify README files and other files
                readme_files = [f for f in files if f.lower().startswith("readme")]
                other_files = [f for f in files if not f.lower().startswith("readme")]

                # Process READMEs first in this directory
                for file_name in readme_files:
                    write_to_master(current_path / file_name, outfile)

                # Process remaining files
                for file_name in other_files:
                    write_to_master(current_path / file_name, outfile)


def write_to_master(file_path, outfile):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
            outfile.write(f"\n\n--- SOURCE: {file_path} ---\n\n")
            outfile.write(infile.read())
            outfile.write("\n")
    except Exception as e:
        print(f"Could not read {file_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge directory contents into one MD file.")
    parser.add_argument(
        "inputs",
        nargs="+",
        help="List of directories or files to process",
        default=["/home/salim/prj/salim/nasim/code/nasim/docs/C4"],
    )
    parser.add_argument("-o", "--output", help="Path to the output master .md file", default="c4.md")

    args = parser.parse_args()

    merge_documents(args.inputs, args.output)
    print(f"Successfully merged into {args.output}")
