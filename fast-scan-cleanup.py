from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path
from shutil import which
from subprocess import run
from tempfile import TemporaryDirectory

from argh import dispatch_command
from pypdf import PdfMerger, PdfReader
from rich.console import Console
from rich.markup import escape

console = Console()
run = partial(run, capture_output=True, check=True)


def worker(src: Path, *, language: str) -> Path:
    if which("unpaper"):
        console.log(f"Found [b]unpaper[/], unpaper-ing [i]{escape(str(src))}")
        unpapered = src.with_suffix(".unpaper.ppm")
        run(("unpaper", src, unpapered))
        src = unpapered
    console.log(f"Running [b]tesseract[/] on [i]{escape(str(src))}")
    run(("tesseract", "-l", language, src, src.with_suffix(".ocr"), "pdf"))
    console.log(f"Ran [b]tesseract[/] on [i]{escape(str(src))}")
    return src.with_suffix(".ocr.pdf")


def main(*, input: str = "input.pdf", output: str = "output.pdf", language: str) -> None:
    "Unpaper & tesseract all the things!"
    if not which("unpaper"):
        console.log("[b]unpaper not found[/], will not be ran")
    console.log("Converting PDF to PPM")
    with TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir, ProcessPoolExecutor() as pool:
        tmpdir = Path(tmpdir)
        run(("pdftoppm", input, tmpdir / "page"), check=True)
        processed = pool.map(partial(worker, language=language), tmpdir.glob("*.ppm"))
        merger = PdfMerger()
        console.log("Merging pages")
        for page in processed:
            merger.append(str(page))
        if (reader := PdfReader(input)).metadata is not None:
            merger.add_metadata(reader.metadata)
        console.log("Writing output")
        merger.write(output)
    console.log("Bye!")


if __name__ == "__main__":
    dispatch_command(main)
