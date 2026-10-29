# Hobby Recommender System — Streamlit

เว็บแอปแนะนำงานอดิเรกจาก Graph ตามข้อมูลในไฟล์ Hobby Recommender System (ผู้ใช้ 10 คน, งานอดิเรก 8 ประเภท)

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. อัปโหลด `app.py` และ `requirements.txt` ไปยัง GitHub repository
2. เปิด https://share.streamlit.io/ แล้วเลือก repository และไฟล์ `app.py`
3. กด Deploy

## Optional: Neo4j Aura
ถ้ามีฐานข้อมูล Neo4j Aura ให้ตั้งค่า environment variables:
- `NEO4J_URI`
- `NEO4J_USERNAME`
- `NEO4J_PASSWORD`

บน Streamlit Community Cloud สามารถตั้งค่าได้ที่ App → Settings → Secrets:
```toml
NEO4J_URI = "neo4j+s://your-instance.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "your-password"
```
แอปจะอ่านข้อมูลจาก `(:User)-[:LIKES]->(:Hobby)` หากเชื่อมต่อไม่ได้จะใช้ข้อมูลตัวอย่างในโปรเจกต์แทน

## Notes
- คะแนนแนะนำเป็นจำนวนเส้นทางที่สนับสนุนคำแนะนำ ไม่ใช่คะแนนความแม่นยำ ML
- แก้ไขชื่อ/รหัส/หมู่เรียนในหน้าแรกก่อนนำเสนอ
