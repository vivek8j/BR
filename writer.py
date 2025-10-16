import csv
import logging
import os
from config import OUTPUT_CSV
from constant import NOT_AVAILABLE
import html
import re

def ensure_columns(row: dict, columns_order: list):
    return {col: row.get(col, NOT_AVAILABLE) for col in columns_order}

def save_to_csv(rows, columns_order):
    try:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns_order)
            writer.writeheader()
            for row in rows:
                for col in columns_order:
                    if col not in row:
                        row[col] = NOT_AVAILABLE
                writer.writerow(row)
        logging.info(f"✅ Done! {len(rows)} Plot entries saved to {OUTPUT_CSV}")
    except Exception as e:
        logging.error(f"Failed to write CSV: {e}", exc_info=True)

def append_to_csv(row, columns_order, filename=OUTPUT_CSV):
    try:
        file_exists = False
        try:
            with open(filename, 'r', encoding='utf-8') as _:
                file_exists = True
        except FileNotFoundError:
            pass

        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns_order)
            if not file_exists:
                writer.writeheader()

            for col in columns_order:
                if col not in row:
                    row[col] = NOT_AVAILABLE
            writer.writerow(row)
    except Exception as e:
        logging.error(f"Failed to append to CSV: {e}", exc_info=True)