import re
import fitz      # pip install pymupdf
import json
import sys
import os

def parse_transcript_into_json(pdf_path):
    # 1) pull all text and collapse newlines→spaces
    doc = fitz.open(pdf_path)
    raw = "".join(page.get_text() for page in doc)
    clean = re.sub(r'\s+', ' ', raw)

    # 2) skip the pre‑undergrad stuff
    marker = "Beginning of Undergraduate Record"
    if marker in clean:
        clean = clean.split(marker, 1)[1]

    # 3) match “CODE” … “GRADE” that’s immediately followed by “ space + credits ”
    pattern = re.compile(
        r'([A-Z]{2,4} \d{4})'         # e.g. "CS 2100"
        r'.*?'                         # anything (now on one line)
        r'([A-F](?:\+|-)?|CR)'         # A, A-, B+, or CR
        r'(?=\s+\d+\.\d)'              # lookahead for the credit hours
    )

    return {m.group(1): m.group(2) for m in pattern.finditer(clean)}

def main():
    # accept path on CLI or prompt otherwise
    path = sys.argv[1] if len(sys.argv) > 1 else input("Transcript PDF path: ").strip()
    if not os.path.isfile(path):
        print(f"❌ File not found: {path}")
        sys.exit(1)

    data = parse_transcript_into_json(path)
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()