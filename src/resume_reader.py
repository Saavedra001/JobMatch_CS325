import re
import sys
import unicodedata
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

# resumes/ folder in the project
RESUME_DIR = Path(__file__).resolve().parent.parent / "resumes"


def find_resume():
    """Return the resume in resumes/. If there are several, ask the user which one."""
    files = sorted(f for f in RESUME_DIR.glob("*") if f.suffix.lower() in (".pdf", ".txt"))

    # none
    if not files:
        raise FileNotFoundError("No resume found. Add a .pdf or .txt file to the resumes/ folder.")

    # one
    if len(files) == 1:
        return files[0]

    # several: ask which one
    print(f"Found {len(files)} resumes in resumes/:")
    for i, file in enumerate(files, 1):
        print(f"  {i}. {file.name}")
    while True:
        choice = input(f"Which one? (1-{len(files)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(files):
            return files[int(choice) - 1]
        print("Please type a number from the list.")


def read_resume(path):
    """Read a .pdf or .txt resume and return cleaned lowercase text."""
    return clean_text(extract_text(path))


def extract_text(path):
    """Return the raw text of a .pdf or .txt resume."""
    file = Path(path)

    # file exists?
    if not file.is_file():
        raise FileNotFoundError(f"Resume file not found: {path}")

    # right type?
    ext = file.suffix.lower()
    if ext not in (".pdf", ".txt"):
        raise ValueError(f"Wrong file type '{ext}'. Please use a .pdf or .txt file.")

    # empty file?
    if file.stat().st_size == 0:
        raise ValueError(f"Resume file is empty: {file.name}")

    # extract text
    if ext == ".pdf":
        try:
            reader = PdfReader(file)
            text = " ".join(page.extract_text() or "" for page in reader.pages)
        except PdfReadError:
            raise ValueError(f"Could not open PDF (file may be damaged): {file.name}")
    else:
        text = file.read_text(encoding="utf-8", errors="ignore")

    # no real text? (only spaces/symbols, or a scanned PDF)
    if not re.search(r"[A-Za-z0-9]", text):
        if ext == ".pdf":
            raise ValueError(f"No readable text in {file.name} (scanned/image PDFs are not supported).")
        raise ValueError(f"Resume file is empty: {file.name}")

    return text


# personal info patterns
EMAIL = r"\S+@\S+"
LINK = r"(https?://|www\.)\S+|\S*(linkedin|github)\.com\S*"
PHONE = r"(\+?\d{1,2}[\s.-]*)?\(?\d{3}\)?[\s.-]*\d{3}[\s.-]*\d{4}"


def clean_text(text):
    """Remove personal info and symbols, return lowercase text."""
    # fix PDF ligatures (e.g. "ﬃ" -> "ffi"), then lowercase
    text = unicodedata.normalize("NFKC", text).lower()

    # find name (short header before first email/phone/link)
    name = []
    contact = re.search(f"{EMAIL}|{LINK}|{PHONE}", text)
    if contact:
        name = re.findall(r"[a-z]+", text[:contact.start()])
        if len(name) > 4:
            name = []

    # remove emails, links, phone numbers
    text = re.sub(EMAIL, " ", text)
    text = re.sub(LINK, " ", text)
    text = re.sub(PHONE, " ", text)

    # remove name
    for word in name:
        text = re.sub(rf"\b{word}\b", " ", text)

    # remove symbols (keep + and # for c++, c#)
    text = re.sub(r"[^a-z0-9+#\s]", " ", text)

    # remove extra spaces
    return " ".join(text.split())


# quick test: python src/resume_reader.py
if __name__ == "__main__":
    try:
        print(read_resume(find_resume()))
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
