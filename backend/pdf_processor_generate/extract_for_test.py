import fitz  # pymupdf
import os
import re


def extract_toc_sections(pdf_path):
    """讀取目錄並儲存各章節名稱，並過濾掉頁碼與點點線"""
    doc = fitz.open(pdf_path)
    toc_sections = set()

    for page in doc:
        page_text = page.get_text("text")
        lines = page_text.split("\n")
        for line in lines:
            clean_line = re.sub(r"[.\s]+\d+$", "", line).strip()
            match = re.match(r"^([1-5](?:\.[0-9]+)+)\s+(.*)$", clean_line)
            match_ch = re.match(r"^(第[一二三四五六七八九十百零〇]{1,7}節)\s*(.*)$",
                                clean_line)
            if match:
                section_number, section_name = match.groups()
                toc_sections.add(
                    (section_number.strip(), section_name.strip()))
            elif match_ch:
                section_number, section_name = match_ch.groups()
                toc_sections.add(
                    (section_number.strip(), section_name.strip()))

    return toc_sections


def extract_sections(pdf_path, text_counter, toc_sections, all_texts):
    """從內文中抓取對應章節名稱的完整段落，不包含目錄內容與標題，支援跨頁處理。"""
    doc = fitz.open(pdf_path)
    extracting = False
    first_paragraph = ""
    found_content = False  # 用來確保我們跳過目錄
    pdf_name = os.path.basename(pdf_path)
    # start_counter = file_counter

    all_text = []
    for page in doc:
        page_text = page.get_text("text")
        lines = page_text.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 跳過頁碼（純數字行）
            if line.isdigit():
                continue

            # 跳過封底內容（包含 "國立XX大學" 的行）
            if "國立" in line:
                continue

            all_text.append(line)

    for i, line in enumerate(all_text):
        if "....." in line:
            continue  # 直接跳過含有點點線的內容

        # 偵測參考文獻，若遇到則停止擷取
        if re.match(r"^(參考文獻|References)$", line.strip()):
            extracting = False
            break

        match = re.match(r"^([1-5](?:\.[0-9]+)+)\s+(.*)$", line)
        match_ch = re.match(r"^(第[一二三四五六七八九十百零〇]{1,7}節)\s*(.*)$", line)
        if match:
            section_number, section_name = match.groups()

            if (section_number.strip(), section_name.strip()) in toc_sections:
                if not found_content:
                    found_content = True  # 跳過目錄部分
                    continue

                if extracting:
                    paragraph_length = len(first_paragraph.strip())
                    if 200 <= paragraph_length <= 2000:
                        all_texts.append(first_paragraph)

                        # txt_filename = f"{file_counter}.txt"
                        # txt_path = os.path.join(output_dir, txt_filename)
                        # with open(txt_path, "w", encoding="utf-8") as txt_file:
                        #     txt_file.write(first_paragraph.strip() + "\n")
                        # print(f"Section saved to {txt_path}")
                        text_counter += 1
                    # else:
                    #     print(f"Skipped section due to length ({paragraph_length} chars)")

                first_paragraph = ""  # 重置段落，但不儲存標題
                extracting = True
                continue
        elif match_ch:
            section_number, section_name = match_ch.groups()

            if (section_number.strip(), section_name.strip()) in toc_sections:
                if not found_content:
                    found_content = True  # 跳過目錄部分
                    continue

                if extracting:
                    paragraph_length = len(first_paragraph.strip())
                    if 200 <= paragraph_length <= 2000:
                        all_texts.append(first_paragraph)

                        # txt_filename = f"{file_counter}.txt"
                        # txt_path = os.path.join(output_dir, txt_filename)
                        # with open(txt_path, "w", encoding="utf-8") as txt_file:
                        #     txt_file.write(first_paragraph.strip() + "\n")
                        # print(f"Section saved to {txt_path}")
                        text_counter += 1
                    # else:
                    #     print(f"Skipped section due to length ({paragraph_length} chars)")

                first_paragraph = ""  # 重置段落，但不儲存標題
                extracting = True
                continue

        if extracting and found_content:
            first_paragraph += line.strip() + " "

            # 判斷段落結束條件（下一行為空，或遇到新的章節）
            if i + 1 < len(all_text) and not all_text[i + 1].strip():
                extracting = False

    if extracting:
        paragraph_length = len(first_paragraph.strip())
        if 200 <= paragraph_length <= 2000:
            all_texts.append(first_paragraph)

            # txt_filename = f"{file_counter}.txt"
            # txt_path = os.path.join(output_dir, txt_filename)
            # with open(txt_path, "w", encoding="utf-8") as txt_file:
            #     txt_file.write(first_paragraph.strip() + "\n")
            # print(f"Section saved to {txt_path}")
            text_counter += 1
        # else:
        #     print(f"Skipped section due to length ({paragraph_length} chars)")

    # end_counter = file_counter - 1
    # if start_counter <= end_counter:
    #     index_records.append(f"{pdf_name}: {start_counter}.txt - {end_counter}.txt")

    return text_counter


def merge(t_counter, all_texts):
    result = []
    content = ""
    end_counter = t_counter - 1
    cut1 = end_counter // 3
    cut2 = cut1 * 2

    for i in range(cut1):
        content = content + all_texts[i].strip() + "\n\n"
    result.append(content)
    content = ""

    for i in range(cut1, cut2):
        content = content + all_texts[i].strip() + "\n\n"
    result.append(content)
    content = ""

    for i in range(cut2, end_counter):
        content = content + all_texts[i].strip() + "\n\n"
    result.append(content)
    content = ""

    # txt_filename = f"{f_counter}.txt"
    # txt_path = os.path.join(output_dir, txt_filename)
    # with open(txt_path, "w", encoding="utf-8") as txt_file:
    #     for i in range(cut1):
    #         txt_file.write(all_texts[i].strip() + "\n\n")
    # print(f"Section saved to {txt_path}")
    # f_counter += 1

    # txt_filename = f"{f_counter}.txt"
    # txt_path = os.path.join(output_dir, txt_filename)
    # with open(txt_path, "w", encoding="utf-8") as txt_file:
    #     for i in range(cut1, cut2):
    #         txt_file.write(all_texts[i].strip() + "\n\n")
    # print(f"Section saved to {txt_path}")
    # f_counter += 1

    # txt_filename = f"{f_counter}.txt"
    # txt_path = os.path.join(output_dir, txt_filename)
    # with open(txt_path, "w", encoding="utf-8") as txt_file:
    #     for i in range(cut2, end_counter):
    #         txt_file.write(all_texts[i].strip() + "\n\n")
    # print(f"Section saved to {txt_path}")
    # f_counter += 1

    return result


def extract(pdf_path):

    text_counter = 1
    all_texts = []

    toc_sections = extract_toc_sections(pdf_path)  # 先讀取目錄
    text_counter = extract_sections(pdf_path, text_counter, toc_sections,
                                    all_texts)

    return merge(text_counter, all_texts)
