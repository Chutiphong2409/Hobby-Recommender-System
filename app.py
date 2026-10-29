import os
from collections import Counter, defaultdict
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Hobby Recommender", page_icon="🎯", layout="wide")

# Dark theme and styling close to the supplied example
st.markdown("""
<style>
.stApp {background:#0e1117;color:#f5f6fa}
[data-testid="stSidebar"] {background:#262832}
h1,h2,h3 {color:#f7f7fb}
div[data-testid="stMetric"] {background:#171a22;border:1px solid #2b303b;padding:14px;border-radius:12px}
.card {background:#171a22;border:1px solid #2b303b;padding:18px;border-radius:12px;margin-bottom:10px}
.small {color:#aeb4c0;font-size:0.92rem}
</style>
""", unsafe_allow_html=True)

USERS = [f"User{i:02d}" for i in range(1, 11)]
HOBBIES = ["Photography","Drawing","Reading","Gardening","Running","Cooking","Playing Music","Gaming"]
LIKES = {
    "User01":["Photography","Drawing","Reading"],
    "User02":["Photography","Drawing","Reading","Playing Music"],
    "User03":["Photography","Gardening","Cooking"],
    "User04":["Drawing","Reading","Gaming"],
    "User05":["Reading","Playing Music","Gaming"],
    "User06":["Gardening","Cooking","Running"],
    "User07":["Running","Cooking","Gaming"],
    "User08":["Photography","Gardening","Playing Music"],
    "User09":["Drawing","Gaming","Playing Music"],
    "User10":["Reading","Running","Cooking"],
}

def recommend(target_user, top_n=3):
    """Graph-style two-hop recommendation using the relationships in the notebook."""
    liked = set(LIKES[target_user])
    scores = Counter()
    evidence = defaultdict(set)
    for shared_hobby in liked:
        for other_user, other_likes in LIKES.items():
            if other_user == target_user or shared_hobby not in other_likes:
                continue
            for hobby in other_likes:
                if hobby not in liked:
                    scores[hobby] += 1
                    evidence[hobby].add(other_user)
    return [(h, s, sorted(evidence[h])) for h, s in scores.most_common(top_n)]

def get_data_source():
    uri = os.getenv("NEO4J_URI", "")
    user = os.getenv("NEO4J_USERNAME", os.getenv("NEO4J_USER", ""))
    password = os.getenv("NEO4J_PASSWORD", "")
    if not (uri and user and password):
        return "ข้อมูลตัวอย่างในไฟล์ Hobby (Demo)", False, None
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        with driver.session() as session:
            rows = session.run("""
                MATCH (u:User)-[:LIKES]->(h:Hobby)
                RETURN u.name AS user, h.name AS hobby
            """).data()
        driver.close()
        if rows:
            data = defaultdict(list)
            for row in rows:
                data[row["user"]].append(row["hobby"])
            return "Neo4j Aura", True, dict(data)
        return "Neo4j เชื่อมต่อได้ แต่ไม่พบข้อมูล จึงใช้ข้อมูลตัวอย่าง", False, None
    except Exception as exc:
        return f"เชื่อมต่อ Neo4j ไม่สำเร็จ จึงใช้ข้อมูลตัวอย่าง ({type(exc).__name__})", False, None

source_label, neo4j_connected, db_likes = get_data_source()
data = db_likes if db_likes and len(db_likes) else LIKES
all_users = sorted(data.keys())
all_hobbies = sorted({h for vals in data.values() for h in vals})

def recommend_from_data(target_user, top_n=3):
    liked = set(data.get(target_user, []))
    scores = Counter()
    evidence = defaultdict(set)
    for shared in liked:
        for other, hobbies in data.items():
            if other == target_user or shared not in hobbies:
                continue
            for hobby in hobbies:
                if hobby not in liked:
                    scores[hobby] += 1
                    evidence[hobby].add(other)
    return [(h, score, sorted(evidence[h])) for h, score in scores.most_common(top_n)]

with st.sidebar:
    st.title("🎯 Hobby Recommender")
    st.caption("ระบบแนะนำงานอดิเรกด้วย Graph")
    page = st.radio("เลือกหัวข้อ", [
        "หน้าแรก / ผู้พัฒนา",
        "1. ปัญหาและ Dataset",
        "2. Data Preprocessing",
        "3. ทฤษฎีโมเดล Graph",
        "4. ผลลัพธ์และการประเมิน",
        "5. Streamlit Application",
    ])
    st.divider()
    st.subheader("ตั้งค่า")
    top_n = st.slider("จำนวนงานอดิเรกที่แนะนำ", 1, 8, 3)
    st.caption("ข้อมูลผู้ใช้ 10 คน · งานอดิเรก 8 ประเภท")
    st.divider()
    st.caption("แหล่งข้อมูล")
    st.write(source_label)
    if neo4j_connected:
        st.success("เชื่อมต่อ Neo4j แล้ว")
    else:
        st.info("กำลังใช้ข้อมูลตัวอย่าง")

if page == "หน้าแรก / ผู้พัฒนา":
    st.title("Hobby Recommender System")
    st.header("ระบบแนะนำงานอดิเรกด้วย Graph")
    st.write("ค้นหางานอดิเรกใหม่จากความสนใจของผู้ใช้ที่มีความชอบคล้ายกัน โดยใช้แนวคิด Graph-based Recommendation")
    a,b,c = st.columns(3)
    a.metric("ผู้ใช้", len(data))
    b.metric("ประเภทงานอดิเรก", len(all_hobbies))
    c.metric("ความสัมพันธ์ LIKES", sum(len(v) for v in data.values()))
    st.subheader("หลักการทำงาน")
    st.markdown("""
    <div class="card">
    <b>ผู้ใช้ปัจจุบัน</b> → งานอดิเรกที่ชอบ → ผู้ใช้ที่มีความชอบร่วมกัน → งานอดิเรกอื่นของผู้ใช้เหล่านั้น → <b>รายการแนะนำ</b>
    </div>""", unsafe_allow_html=True)
    st.subheader("ข้อมูลผู้พัฒนา")
    st.info("แก้ไขชื่อ รหัสนักศึกษา และหมู่เรียนในส่วนนี้ก่อนส่งงาน")
    st.table(pd.DataFrame({"รายการ":["ชื่อ-นามสกุล","รหัสนักศึกษา","หมู่เรียน"],"ข้อมูล":["[กรอกชื่อผู้พัฒนา]","[กรอกรหัสนักศึกษา]","[กรอกหมู่เรียน]"]}))
    st.subheader("หัวข้อในเว็บไซต์")
    st.dataframe(pd.DataFrame([
        ["1","ปัญหาและ Dataset","ที่มาและรูปแบบข้อมูลผู้ใช้กับงานอดิเรก"],
        ["2","Data Preprocessing","ตรวจสอบข้อมูลและจัดรูปแบบความสัมพันธ์"],
        ["3","ทฤษฎีโมเดล Graph","โครงสร้าง Node, Relationship และอัลกอริทึม"],
        ["4","ผลลัพธ์และการประเมิน","ตัวอย่างผลแนะนำและการวิเคราะห์"],
        ["5","Streamlit Application","ทดลองระบบแนะนำงานอดิเรก"],
    ],columns=["ลำดับ","หัวข้อ","เนื้อหา"]), use_container_width=True, hide_index=True)

elif page == "1. ปัญหาและ Dataset":
    st.title("1. ปัญหาและ Dataset")
    st.subheader("ปัญหาที่ต้องการแก้ไข")
    st.write("ผู้ใช้อาจไม่ทราบว่างานอดิเรกใหม่ใดเหมาะกับตน ระบบจึงใช้ความสนใจที่มีร่วมกับผู้ใช้อื่นเพื่อแนะนำตัวเลือกที่ยังไม่เคยเลือก")
    st.subheader("Dataset")
    rows = [{"User":u,"Hobbies":", ".join(data[u]),"จำนวนความสนใจ":len(data[u])} for u in data]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.subheader("รายการงานอดิเรก")
    st.write(", ".join(all_hobbies))
    counts = Counter(h for values in data.values() for h in values)
    fig = px.bar(pd.DataFrame({"Hobby":list(counts.keys()),"จำนวนผู้ใช้":list(counts.values())}),
                 x="Hobby",y="จำนวนผู้ใช้", title="จำนวนผู้ใช้ที่สนใจงานอดิเรกแต่ละประเภท")
    fig.update_layout(template="plotly_dark",paper_bgcolor="#0e1117",plot_bgcolor="#0e1117")
    st.plotly_chart(fig,use_container_width=True)

elif page == "2. Data Preprocessing":
    st.title("2. Data Preprocessing")
    st.write("ข้อมูลต้นฉบับอยู่ในรูปแบบผู้ใช้แต่ละคนเชื่อมโยงกับรายการงานอดิเรก แปลงเป็นตารางความสัมพันธ์แบบหนึ่งแถวต่อหนึ่งคู่ User–Hobby")
    edges = [{"User":u,"Hobby":h,"Relationship":"LIKES"} for u,hs in data.items() for h in hs]
    df = pd.DataFrame(edges).drop_duplicates()
    c1,c2,c3 = st.columns(3)
    c1.metric("จำนวนผู้ใช้",df.User.nunique())
    c2.metric("จำนวนงานอดิเรก",df.Hobby.nunique())
    c3.metric("จำนวนความสัมพันธ์",len(df))
    st.subheader("ตารางหลังจัดรูปแบบ")
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button("ดาวน์โหลดข้อมูล CSV",df.to_csv(index=False).encode("utf-8-sig"),"hobby_relationships.csv","text/csv")
    st.subheader("ขั้นตอนที่ใช้")
    st.markdown("- ตรวจสอบชื่อผู้ใช้และงานอดิเรก\n- แยกความชอบให้อยู่ในรูปแบบคู่ข้อมูล\n- ตัดคู่ความสัมพันธ์ที่ซ้ำกัน\n- เตรียมข้อมูลเพื่อสร้าง Graph")

elif page == "3. ทฤษฎีโมเดล Graph":
    st.title("3. ทฤษฎีโมเดล Graph")
    st.write("กราฟประกอบด้วย Node สองชนิด คือ User และ Hobby และเชื่อมกันด้วย Relationship `LIKES`")
    st.code("(User)-[:LIKES]->(Hobby)",language="cypher")
    st.subheader("ตัวอย่างความสัมพันธ์")
    sample = pd.DataFrame([{"User":u,"Relationship":"LIKES","Hobby":h} for u,hs in data.items() for h in hs][:15])
    st.dataframe(sample,use_container_width=True,hide_index=True)
    st.subheader("อัลกอริทึมแนะนำ")
    st.markdown("""
    1. อ่านงานอดิเรกที่ผู้ใช้เป้าหมายชอบอยู่แล้ว
    2. ค้นหาผู้ใช้อื่นที่ชอบงานอดิเรกเดียวกัน
    3. รวบรวมงานอดิเรกอื่นของผู้ใช้เหล่านั้น
    4. ตัดงานอดิเรกที่ผู้ใช้เป้าหมายมีอยู่แล้ว
    5. นับคะแนนจากจำนวนเส้นทางความสนใจที่สนับสนุน แล้วเรียงคะแนนจากมากไปน้อย
    """)
    st.caption("คะแนนเป็นจำนวนครั้งที่พบเส้นทางแนะนำ ไม่ใช่ความน่าจะเป็นหรือความแม่นยำของ Machine Learning")

elif page == "4. ผลลัพธ์และการประเมิน":
    st.title("4. ผลลัพธ์และการประเมิน")
    chosen = st.selectbox("เลือกผู้ใช้เพื่อดูผลตัวอย่าง", all_users, index=all_users.index("User01") if "User01" in all_users else 0)
    liked = data.get(chosen, [])
    st.subheader(f"งานอดิเรกที่ {chosen} ชอบ")
    st.write(" · ".join(liked) if liked else "ไม่พบรายการความสนใจ")
    result = recommend_from_data(chosen, top_n)
    st.subheader("รายการแนะนำ")
    if result:
        result_df = pd.DataFrame([{"อันดับ":i+1,"งานอดิเรก":h,"คะแนน":score,"ผู้ใช้ที่เป็นหลักฐาน":", ".join(users)} for i,(h,score,users) in enumerate(result)])
        st.dataframe(result_df,use_container_width=True,hide_index=True)
        fig = px.bar(result_df,x="งานอดิเรก",y="คะแนน",text="คะแนน",title=f"คะแนนแนะนำสำหรับ {chosen}")
        fig.update_layout(template="plotly_dark",paper_bgcolor="#0e1117",plot_bgcolor="#0e1117")
        st.plotly_chart(fig,use_container_width=True)
    else:
        st.warning("ไม่มีคำแนะนำจากข้อมูลที่มี")
    st.subheader("ข้อจำกัด")
    st.write("ข้อมูลเป็นชุดตัวอย่างขนาดเล็ก คะแนนใช้การนับเส้นทางในกราฟ และยังไม่มีข้อมูล feedback เพื่อวัด Precision@K หรือ Recall@K อย่างเป็นทางการ")

else:
    st.title("5. Streamlit Application")
    st.write("เลือกผู้ใช้เพื่อรับคำแนะนำงานอดิเรกจากความสัมพันธ์ใน Graph")
    chosen = st.selectbox("ผู้ใช้",all_users,index=all_users.index("User01") if "User01" in all_users else 0)
    st.markdown("#### งานอดิเรกที่ผู้ใช้เลือกไว้")
    liked = data.get(chosen, [])
    cols = st.columns(4)
    for i,h in enumerate(liked):
        cols[i%4].markdown(f"<div class='card'>❤️ {h}</div>",unsafe_allow_html=True)
    if st.button("✨ แนะนำงานอดิเรก",type="primary",use_container_width=True):
        results = recommend_from_data(chosen,top_n)
        if not results:
            st.warning("ไม่พบงานอดิเรกใหม่ที่จะแนะนำ")
        else:
            st.subheader("งานอดิเรกที่เหมาะสำหรับลองทำ")
            cols = st.columns(min(3,len(results)))
            for i,(h,score,users) in enumerate(results):
                with cols[i%len(cols)]:
                    st.markdown(f"<div class='card'><h3>#{i+1} {h}</h3><p>คะแนน: <b>{score}</b></p><p class='small'>พบจากผู้ใช้: {', '.join(users)}</p></div>",unsafe_allow_html=True)
            with st.expander("ดูวิธีคิดคะแนน"):
                st.write("คะแนนนับจำนวนครั้งที่ผู้ใช้คนอื่นซึ่งมีงานอดิเรกร่วมกัน แนะนำให้กับผู้ใช้เป้าหมาย")
    st.caption("หากต้องการเชื่อมต่อ Neo4j Aura ให้ตั้งค่า NEO4J_URI, NEO4J_USERNAME และ NEO4J_PASSWORD ใน Secrets หรือ Environment Variables")
