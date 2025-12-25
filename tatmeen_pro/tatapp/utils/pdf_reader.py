# utils/pdf_reader.py
# import pdfplumber

# def extract_invoice_data(pdf_file):
#     """
#     Extracts text and tables from a PDF invoice file-like object.
#     Works for both Django's UploadedFile and file paths.
#     """
#     result = {
#         "text": "",
#         "tables": []
#     }

#     try:
#         with pdfplumber.open(pdf_file) as pdf:
#             for page in pdf.pages:
#                 result["text"] += page.extract_text() or ""
#                 result["tables"].extend(page.extract_tables())
#     except Exception as e:
#         raise ValueError(f"Error processing PDF: {e}")

#     return result



import pdfplumber
import re

def extract_invoice_data(pdf_file):
    """
    Extracts structured invoice data from PDF.
    """
    

    # Initialize final structure
    extracted_data = {
        "customer_name": "",
        "address": "",
        "gr_id": "",
        "rec_date": "",
        "inv_no": "",
        "invoice_date": "",
        "po_number": "",
        "po_date": "",
        "time_in": "",
        "container_no": "",
        "veh_identity": "",
        "productQuantities": []
    }

    # Extract all text & tables
    with pdfplumber.open(pdf_file) as pdf:
        all_text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        tables = []
        for page in pdf.pages:
            tables.extend(page.extract_tables())

    # Patterns for known fields
    patterns = {
        "customer_name": r"CUSTOMER NAME\s*:\s*([^\n]+?)(?=\s+PURCHASE NUMBER|$)",
        "address": r"ADDRESS\s*:\s*(.+)",
        "inv_no": r"INV NO\s*:\s*(\S+)",
        "invoice_date": r"INV DATE\s*:\s*([\d-]+)",
        "po_number": r"PURCHASE NUMBER\s*:\s*(\S+)",
        "po_date": r"PURCHASE ORDER DATE\s*:\s*([\d-]+)",
        "container_no": r"CONTAINER NO\s*:\s*(\S+)",
        "veh_identity": r"VEHICLE IDENTITY\s*:\s*(\S+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, all_text, re.IGNORECASE)
        if match:
            extracted_data[key] = match.group(1).strip()

    # Extract products from first table
    if tables:
        headers = [h.strip().lower() for h in tables[0][0]]
        for row in tables[0][1:]:
            product = {
                "pro_name": "",
                "batch": "",
                "mfg_date": "",
                "best_before": "",
                "pallet_count": 0,
                "carton_count": 0,
                "product_qty": 0
            }
            for i, header in enumerate(headers):
                val = row[i] if i < len(row) else ""
                if "product" in header:
                    product["pro_name"] = val
                elif "batch" in header:
                    product["batch"] = val
                elif "mfg" in header:
                    product["mfg_date"] = val
                elif "exp" in header or "best" in header:
                    product["best_before"] = val
                elif "pallet" in header:
                    product["pallet_count"] = int(val) if val.isdigit() else 0
                elif "carton" in header:
                    product["carton_count"] = int(val) if val.isdigit() else 0
            extracted_data["productQuantities"].append(product)

    return extracted_data



# for neo life

import re
import pdfplumber
from collections import defaultdict


def clean_text(text):
    return text.strip() if text else ""


def find_value_column(words, label_parts, y_tolerance=50, x_tolerance=120):
    """
    Finds the value directly below a multi-word label (like 'Invoice Date').
    label_parts: list of words to match in sequence (case-insensitive, colon ignored).
    """
    target_label = [p.lower().replace(":", "") for p in label_parts]
    label_positions = []

    # Search for matching sequence of words
    for i in range(len(words) - len(label_parts) + 1):
        seq = [words[i + j]["text"].strip().lower().replace(":", "") for j in range(len(label_parts))]
        if seq == target_label:
            label_positions.append(words[i])  # Take the position of the first word in the label

    for label_word in label_positions:
        label_top = label_word["top"]
        label_x0 = label_word["x0"]

        # Words directly below the label in the same column
        below_words = [
            w for w in words
            if 0 < (w["top"] - label_top) <= y_tolerance
            and abs(w["x0"] - label_x0) < x_tolerance
        ]
        if below_words:
            # Group by line (Y coordinate)
            lines_by_y = defaultdict(list)
            for bw in below_words:
                lines_by_y[int(bw["top"])].append(bw["text"])
            nearest_y = min(lines_by_y.keys())
            return " ".join(lines_by_y[nearest_y]).strip()

    return ""


def find_footer_value(words, label_parts, y_tolerance=20, x_tolerance=200):
    """
    Finds the numeric/currency value to the right of a multi-word footer label.
    Works even if the label contains numbers (like 'VAT 0% on').
    """
    target_label = [p.lower().replace(":", "") for p in label_parts]

    for i in range(len(words) - len(label_parts) + 1):
        seq = [words[i + j]["text"].strip().lower().replace(":", "") for j in range(len(label_parts))]
        if seq == target_label:
            label_top = words[i]["top"]
            label_right_edge = max(words[i + j]["x1"] for j in range(len(label_parts)))

            # Words to the right of the label
            right_words = [
                w for w in words
                if abs(w["top"] - label_top) <= y_tolerance
                and w["x0"] > label_right_edge
                and (w["x0"] - label_right_edge) < x_tolerance
            ]

            # Sort left-to-right
            right_words.sort(key=lambda w: w["x0"])
            right_text = " ".join(w["text"] for w in right_words).strip()

            # Find the first currency-like value (skip % values)
            match = re.search(r"\d[\d.,]*\s*€", right_text)
            if match:
                return match.group(0).strip()

    return ""


def extracting_invoice_data(pdf_path):
    result = {
        "company_name": "",
        "address": "",
        "invoice_no": "",
        "invoice_date": "",
        "due_date": "",
        "source": "",
        "reference": "",
        "product_details": [],
        "untaxed_amount": "",
        "vat_0_percent_on": "",
        "total": "",
        "product_data": []
    }

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        words = page.extract_words()

        # --- Company name & address ---
        lines_by_y = defaultdict(list)
        for w in words:
            lines_by_y[int(w["top"])].append(w["text"])
        sorted_lines = [" ".join(lines_by_y[y]) for y in sorted(lines_by_y)]

        result["company_name"] = sorted_lines[0].strip()
        result["address"] = " ".join(sorted_lines[1:4]).strip()

        # --- Invoice number ---
        text_block = " ".join(w["text"] for w in words)
        match_inv = re.search(r'Invoice\s+([A-Z0-9/]+)', text_block, re.IGNORECASE)
        if match_inv:
            result["invoice_no"] = match_inv.group(1).strip()

        # --- Column-based fields ---
        result["invoice_date"] = find_value_column(words, ["Invoice", "Date"])
        result["due_date"] = find_value_column(words, ["Due", "Date"])
        result["source"] = find_value_column(words, ["Source"])
        result["reference"] = find_value_column(words, ["Reference"])

        # --- Product details table ---
        table = page.extract_table()
        if table:
            for row in table[1:]:
                if not any(row):
                    continue
                desc = row[0].strip() if row[0] else ""
                mah, origin = "", ""
                if "MAH:" in desc:
                    parts = desc.split("MAH:")
                    desc = parts[0].strip()
                    mah_origin = parts[1].split("Origin:")
                    mah = mah_origin[0].strip()
                    if len(mah_origin) > 1:
                        origin = mah_origin[1].strip()

                result["product_details"].append({
                    "description": desc,
                    "MAH": mah,
                    "origin": origin,
                    "dosage": clean_text(row[1]),
                    "conditioning": clean_text(row[2]),
                    "quantity": clean_text(row[3]),
                    "unit_price": clean_text(row[4]),
                    "taxes": clean_text(row[5]),
                    "total_price": clean_text(row[6])
                })

        # --- Footer amounts ---
        result["untaxed_amount"] = find_footer_value(words, ["Untaxed", "Amount"])
        result["vat_0_percent_on"] = find_footer_value(words, ["VAT", "0%", "on"])
        result["total"] = find_footer_value(words, ["Total"])

        # --- Product data table ---
        tables = page.extract_tables()
        if len(tables) > 1:
            product_data_table = tables[1]
            for row in product_data_table[1:]:
                if not any(row):
                    continue
                # Try to extract mfg date from the row
                mfg_match = re.search(r"Mfg[\s,]*Date:?\s*(\d{2}/\d{2}/\d{4})", " ".join(row), re.IGNORECASE)
                if not mfg_match:
                    # Fallback: search whole page text
                    page_text = page.extract_text()
                    mfg_match = re.search(r"Mfg[\s,]*Date:?\s*(\d{2}/\d{2}/\d{4})", page_text, re.IGNORECASE)

                result["product_data"].append({
                    "product": clean_text(row[0]),
                    "lot": clean_text(row[1]),
                    "expiry_date": clean_text(row[2]),
                    "mfg_date": mfg_match.group(1) if mfg_match else ""
                })

    return result


# Example usage:
# data = extracting_invoice_data("InvoiceNeoSS.pdf")
# print(data)
