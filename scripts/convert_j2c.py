import json
import csv
import os

json_path = os.path.join(os.path.dirname(__file__), "../db/store_data.json")

csv_path = os.path.join(os.path.dirname(__file__), "../db/store_dataa.csv")

with open(json_path, "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

# CSV 파일에 저장할 필드명
fields = ["id", "name", "thumbnail", "menu", "ctg1", "ctg2", "diet", "cheap", "latitude", "longitude", "kakao_link"]

with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fields)
    writer.writeheader()
    for record in data:
        # 메뉴와 카테고리는 JSON 문자열로 변환하여 저장
        record["menu"] = json.dumps(record.get("menu", []), ensure_ascii=False)
        record["ctg1"] = json.dumps(record.get("ctg1", []), ensure_ascii=False)
        record["ctg2"] = json.dumps(record.get("ctg2", []), ensure_ascii=False)
        writer.writerow(record)

print(f"CSV 파일이 생성되었습니다: {csv_path}")