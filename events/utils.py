import csv

def parse_usernames_from_csv(file, expected_column='帳號'):
    """
    從 CSV 檔案中解析帳號欄位，回傳 username list。
    自動處理 BOM、欄位名變異、空白與換行。
    """
    result = []
    try:
        content = file.read().decode('utf-8-sig').splitlines()
        reader = csv.DictReader(content)
        fieldnames = [fn.strip() for fn in (reader.fieldnames or [])]

        match_col = None
        for fn in fieldnames:
            if expected_column in fn:
                match_col = fn
                break

        if not match_col:
            return [], ['❌ 找不到欄位：帳號']

        errors = []
        for row in reader:
            raw = row.get(match_col, '').strip()
            if raw:
                result.append(raw)
            else:
                errors.append('❌ 找不到帳號欄位或有空值')

        return result, errors

    except Exception as e:
        return [], [f'❌ 匯入失敗：{str(e)}']
