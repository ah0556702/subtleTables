import pdfplumber
import csv
import re

pdf_path = 'Vegetables.pdf'
csv_file_path = 'vegetables_data_with_alternative_phone.csv'

def parse_listing(line):

    phone_pattern = r'(\d{3}-\d{3}-\d{4})|Call'
    phones = re.findall(phone_pattern, line)
    if phones:

        if len(phones) == len(line.split()) or "Call" in line:
            return None, None, " ".join(phones)
        else:
            phone = phones[0]
            before_phone = line[:line.find(phone)].strip()
            parts = before_phone.rsplit(' ', 2)  # separate name and location
            if len(parts) >= 2:
                location = parts[-1]
                name = ' '.join(parts[:-1])
            else:
                name = parts[0]
                location = "Unknown"
    else:
        name, location = line, "Unknown"
        phone = "Unknown"
    return name, location, phone

def extract_data(page_text):
    structured_data = []
    current_category = None
    previous_entry = []

    for line in page_text.split('\n'):
        if line.isupper() and not any(char.isdigit() for char in line):
            current_category = line
        else:
            name, location, phone = parse_listing(line)
            if name is None and previous_entry:  # Handle alternative phone numbers
                if len(previous_entry) < 5:
                    previous_entry.append(phone)
                else:
                    previous_entry[4] += "; " + phone
            else:
                if previous_entry and len(previous_entry) > 1:
                    structured_data.append(previous_entry)
                previous_entry = [current_category, name, location, phone]

    if previous_entry and len(previous_entry) > 1:
        structured_data.append(previous_entry)

    return structured_data

all_data = []

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:  # Ensure there's text to process
            page_data = extract_data(text)
            all_data.extend(page_data)

# Write data to CSV
with open(csv_file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Category', 'Name', 'Location', 'Phone Number', 'Alternative Phone'])
    for data_row in all_data:
        writer.writerow(data_row + [''] * (5 - len(data_row)))

print("Data extraction and writing to CSV completed.")
