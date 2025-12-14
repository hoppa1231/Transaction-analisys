import re
from pathlib import Path
import PyPDF2
import pandas as pd
from utils import BASE_DIR


def _empty_store():
    return {'operation': [], 'datetime': [], 'price': []}


DATE_RE = re.compile(r"(\d{2}\.\d{2}\.\d{4})")
TIME_RE = re.compile(r"в\s*(\d{2}:\d{2})")
AMOUNT_RE = re.compile(r"([+−–-]?\s?[\d\s\xa0]+,\d{2})\s?₽")


def parse_page(text, store):
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    for idx in range(len(lines) - 1):
        line = lines[idx]
        next_line = lines[idx + 1]

        if "₽" not in next_line or "в" not in next_line:
            continue

        date_match_line = DATE_RE.search(line)
        date_match_next = DATE_RE.search(next_line)
        time_match = TIME_RE.search(next_line)
        amount_matches = AMOUNT_RE.findall(next_line)

        if not (date_match_line or date_match_next) or not time_match or not amount_matches:
            continue

        # prefer date from the first line if present, else fallback to next line
        date_str = (date_match_line or date_match_next).group(1)
        time_str = time_match.group(1)
        amount_raw = amount_matches[-1]

        # strip date from description if it sticks to the end
        desc = re.sub(r"\d{2}\.\d{2}\.\d{4}.*", "", line).strip()
        if not desc:
            desc = line.strip()

        # normalize amount (replace non-breaking spaces and comma)
        price = amount_raw.replace("\xa0", "").replace(" ", "")
        price = price.replace("−", "-").replace("–", "-").replace(",", ".")
        if price.startswith("+"):
            price = price[1:]

        try:
            price_val = float(price)
        except ValueError:
            continue

        datetime_str = f"{date_str} {time_str}"

        store['operation'].append(desc)
        store['datetime'].append(datetime_str)
        store['price'].append(price_val)


def pdf_to_csv(filename='input.pdf', input_path=None, output_path=None):
    """Convert PDF statement to CSV stored in data/base/output.csv."""
    store = _empty_store()
    pdf_source = Path(input_path) if input_path else Path(BASE_DIR) / 'data' / 'pdf' / filename

    with open(pdf_source, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        # operations start from page 3 in provided sample
        for page_idx in range(len(reader.pages)):
            text = reader.pages[page_idx].extract_text()
            if not text:
                continue
            parse_page(text, store)

    df = pd.DataFrame(store)
    csv_path = Path(output_path) if output_path else Path(BASE_DIR) / 'data' / 'base' / 'output.csv'
    df.to_csv(csv_path, index=False)
    return str(csv_path)
