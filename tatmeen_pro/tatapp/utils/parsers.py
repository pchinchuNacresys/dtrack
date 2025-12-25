import re

def parse_neolife_invoice(text, tables):
    data = {
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

    # Company name & address
    lines = text.split("\n")
    data["company_name"] = lines[0].strip()
    address_lines = []
    for line in lines[1:]:
        if line.strip().startswith("Invoice INV/"):
            break
        address_lines.append(line.strip())
    data["address"] = ", ".join(address_lines)

    # Invoice info
    match = re.search(r"Invoice\s+(INV/\d{4}/\d+)", text)
    if match:
        data["invoice_no"] = match.group(1)
    match = re.search(r"Invoice Date:\s*([\d/]+)", text)
    if match:
        data["invoice_date"] = match.group(1)
    match = re.search(r"Due Date:\s*([\d/]+)", text)
    if match:
        data["due_date"] = match.group(1)
    match = re.search(r"Source:\s*([A-Z0-9-]+)", text)
    if match:
        data["source"] = match.group(1)
    match = re.search(r"Reference:\s*([A-Z0-9-]+)", text)
    if match:
        data["reference"] = match.group(1)

    # Product details table (first table)
    if tables and len(tables) > 0:
        product_table = tables[0]
        for i, row in enumerate(product_table[1:], start=1):
            if len(row) < 8:
                continue
            desc = row[0].strip()
            mah, origin = "", ""
            if "\n" in desc:
                parts = desc.split("\n")
                desc = parts[0]
                for p in parts[1:]:
                    if p.startswith("MAH:"):
                        mah = p.replace("MAH:", "").strip()
                    elif p.startswith("Origin:"):
                        origin = p.replace("Origin:", "").strip()

            data["product_details"].append({
                "description": desc,
                "MAH": mah,
                "origin": origin,
                "dosage": row[1],
                "conditioning": row[2],
                "quantity": row[3],
                "unit_price": row[4],
                "taxes": row[5],
                "total_price": row[6]
            })

    # Product lot/expiry table (second table)
    if len(tables) > 1:
        product_data_table = tables[1]
        for row in product_data_table[1:]:
            if len(row) >= 3:
                data["product_data"].append({
                    "product": row[0],
                    "lot": row[1],
                    "expiry_date": row[2],
                    "mfg_date": ""  # Might be below or in text
                })

    # Totals
    match = re.search(r"Untaxed Amount\s*([\d\.,]+ €)", text)
    if match:
        data["untaxed_amount"] = match.group(1)
    match = re.search(r"VAT 0% on\s*([\d\.,]+ €)", text)
    if match:
        data["vat_0_percent_on"] = match.group(1)
    match = re.search(r"Total\s*([\d\.,]+ €)", text)
    if match:
        data["total"] = match.group(1)

    return data

