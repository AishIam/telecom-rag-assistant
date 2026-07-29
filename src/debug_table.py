# debug_table.py — run once to see what the extractor produces
from pathlib import Path
import sys
sys.path.append("src")
from ingest import extract_tables_from_docx
import config

for path in config.RAW_DATA_DIR.iterdir():
    if "s06" in path.name.lower():  # the file with the power table
        tables = extract_tables_from_docx(path)
        for t in tables:
            if "26" in t.page_content and "power class" in t.page_content.lower():
                print(t.page_content[:800])
                print("=" * 60)