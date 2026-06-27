import argparse
import sys
from pathlib import Path


class DocumentMerger:
    def __init__(self, input_dir: Path, output_file: Path):
        self.input_dir = input_dir
        self.output_file = output_file

    def merge(self):
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, "w", encoding="utf-8") as out:
            self._walk(self.input_dir, out)

    def _walk(self, directory: Path, out):
        entries = sorted(directory.iterdir(), key=lambda p: (p.is_dir(), p.name))

        readme = [e for e in entries if e.is_file() and e.name.lower().startswith("readme")]
        common = [e for e in entries if e.is_dir() and e.name == "common"]
        rest_files = [e for e in entries if e.is_file() and not e.name.lower().startswith("readme")]
        rest_dirs = [e for e in entries if e.is_dir() and e.name != "common"]

        for f in readme:
            self._emit(f, out)
        for d in common:
            self._walk(d, out)
        for f in rest_files:
            self._emit(f, out)
        for d in rest_dirs:
            self._walk(d, out)

    def _emit(self, path: Path, out):
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            out.write(f"\n\n--- SOURCE: {path} ---\n\n")
            out.write(content)
            out.write("\n")
        except Exception as e:
            print(f"Warning: could not read {path}: {e}", file=sys.stderr)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUTS = ["docs/C4", "docs/SQ", "docs/UC", "docs/SM"]
DEFAULT_OUTPUTS = [PROJECT_ROOT / f"{Path(d).name}.md" for d in DEFAULT_INPUTS]


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Merge doc directories into separate .md files."
    )
    p.add_argument(
        "-i", "--input", nargs="+", default=DEFAULT_INPUTS,
        help="Input directories (one per merge)",
    )
    p.add_argument(
        "-o", "--output", nargs="+", default=DEFAULT_OUTPUTS,
        help="Output .md files (one per input, same order)",
    )
    args = p.parse_args(argv)
    if len(args.input) != len(args.output):
        p.error("Number of --input and --output must match")
    return args


def main(argv=None):
    args = parse_args(argv)
    for in_dir, out_file in zip(args.input, args.output):
        in_path, out_path = Path(in_dir), Path(out_file)
        if not in_path.is_dir():
            print(f"Warning: {in_dir} is not a directory. Skipping.", file=sys.stderr)
            continue
        merger = DocumentMerger(in_path, out_path)
        merger.merge()
        print(f"Merged {in_dir} -> {out_file}")


if __name__ == "__main__":
    main()
