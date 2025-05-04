import re
import json
import sqlite3
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from pathlib import Path
from ....database.queries import get_connection

# Ініціалізація моделі для генерації короткого опису
tokenizer = AutoTokenizer.from_pretrained("d0p3/O3ap-sm")
model = AutoModelForSeq2SeqLM.from_pretrained("d0p3/O3ap-sm")

JSON_FILE = "news_backup.json"
DB_NAME = "alumni.db"

def generate_short_title(full_desc: str, max_length: int = 25) -> str:
    input_ids = tokenizer(full_desc, return_tensors="pt", truncation=True, max_length=512).input_ids
    output_ids = model.generate(input_ids, max_length=max_length, num_beams=4, early_stopping=True)
    return tokenizer.decode(output_ids[0], skip_special_tokens=True)

def is_valid_url(url: str) -> bool:
    return re.match(r"^https?://\S+\.\S+", url) is not None

def save_news_to_db(short_desc: str, full_desc: str, date: str, link: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO news (short_description, full_description, date, link)
        VALUES (?, ?, ?, ?)
    ''', (short_desc, full_desc, date, link))
    conn.commit()
    conn.close()

def save_news_to_json(short_desc: str, full_desc: str, date: str, link: str):
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            news_list = json.load(f)
    except FileNotFoundError:
        news_list = []

    news_list.append({
        "short_description": short_desc,
        "full_description": full_desc,
        "date": date,
        "link": link
    })

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)
