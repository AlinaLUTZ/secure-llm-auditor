#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ИБ АУДИТ ИИ-СИСТЕМ v3.2
Запуск строго из файла: py audit.py sample_input.txt
"""

import re
import sys
import os
from datetime import datetime
from pathlib import Path

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    pass # Если нет colorama, просто печатаем текст

try:
    import pdfkit
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

def cprint(text, color=""):
    print(text)

def detect_pd(text):
    patterns = {
        "ФИО": r"\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?\b",
        "Паспорт": r"\b\d{4}\s*\d{6}\b",
        "СНИЛС": r"\b\d{3}-\d{3}-\d{3}\s\d{2}\b",
        "ИНН": r"\b\d{12}\b",
        "Биометрия": r"(голос|отпечаток|лицо|ДНК|биометри|фото\s*лица)",
    }
    found = []
    for name, pat in patterns.items():
        if re.search(pat, text, re.IGNORECASE | re.MULTILINE):
            found.append(name)
    return found

def anonymize_text(text):
    text = re.sub(r"\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?\b", "[ФИО УДАЛЕНО]", text)
    text = re.sub(r"\b\d{4}\s*\d{6}\b", "[ПАСПОРТ УДАЛЕН]", text)
    text = re.sub(r"\b\d{3}-\d{3}-\d{3}\s\d{2}\b", "[СНИЛС УДАЛЕН]", text)
    text = re.sub(r"\b\d{12}\b", "[ИНН УДАЛЕН]", text)
    text = re.sub(r"(голос|отпечаток|лицо|ДНК|биометри|фото\s*лица)", "[БИОМЕТРИЯ УДАЛЕНА]", text, flags=re.IGNORECASE)
    return text

def main():
    print("="*60)
    print("🛡️  ИБ АУДИТ ИИ-СИСТЕМ v3.2")
    print("="*60)

    if len(sys.argv) < 2:
        print("❌ Ошибка: Укажите имя файла.")
        print("Пример: py audit.py sample_input.txt")
        return

    filename = sys.argv[1]
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()
        print(f"✅ Файл '{filename}' загружен.")
    except FileNotFoundError:
        print(f"❌ Файл '{filename}' не найден.")
        return
    except Exception as e:
        print(f"❌ Ошибка чтения: {e}")
        return

    # Анализ
    pd_list = detect_pd(text)
    
    # Классификация
    if "Биометрия" in pd_list:
        level = "Уровень 1 (Высокий)"
        category = "Специальная + Биометрия"
    elif any(x in pd_list for x in ["Паспорт", "СНИЛС", "ИНН"]):
        level = "Уровень 1 (Высокий)"
        category = "Специальная категория"
    elif pd_list:
        level = "Уровень 2 (Повышенный)"
        category = "Общая категория"
    else:
        level = "Не применимо"
        category = "ПДн не обнаружены"

    # Анонимизация
    anon_text = anonymize_text(text)
    
    # Проверка ИИ
    if detect_pd(anon_text):
        ai_status = "❌ ЗАПРЕЩЕНО (остались ПДн)"
    else:
        ai_status = "✅ РАЗРЕШЕНО (personalization=false)"

    # Генерация отчета
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_path = REPORTS_DIR / f"{timestamp}_report.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 🛡️ Отчет ИБ Аудита\n\n")
        f.write(f"**Дата:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
        
        if pd_list:
            f.write("## 🔍 Найденные ПДн:\n")
            for item in pd_list:
                f.write(f"- {item}\n")
            
            f.write(f"\n## 📊 Категория: {category}\n")
            f.write(f"##  Уровень: {level}\n\n")
            
            f.write("## 🔐 Требования ГОСТ Р 57580.2:\n")
            f.write("- Шифрование: ГОСТ 28147-89\n")
            f.write("- ЦП: ГОСТ Р 34.10-2012\n\n")
            
            f.write("## 📜 Соответствие №19/2024:\n")
            f.write(f"- Статус вызова ИИ: {ai_status}\n")
        else:
            f.write("## ✅ ПДн не обнаружены.\n")

    print(f"\n📄 Обнаружено ПДн: {len(pd_list)}")
    print(f"📂 Отчёт сохранён: {report_path}")
    
    # Попытка создать PDF
    if HAS_PDF:
        try:
            pdfkit.from_file(str(report_path), str(report_path.with_suffix(".pdf")))
            print(f"📄 PDF также создан: {report_path.with_suffix('.pdf')}")
        except:
            pass

if __name__ == "__main__":
    main()