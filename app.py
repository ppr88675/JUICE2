import streamlit as st
import google.generativeai as genai
import json

# --- 1. 設定區 ---
# 在這裡填入你的 Google AI Studio API Key
GOOGLE_API_KEY = "AIzaSyDw7Jbku74XLldpC0ERI6QlZyew4Mlu6JY"

genai.configure(api_key=GOOGLE_API_KEY)

# 設定頁面資訊
st.set_page_config(page_title="手搖飲達人推薦器", page_icon="🧋", layout="wide")

# 定義系統指令 (就是剛才幫你寫好的關鍵字)
SYSTEM_PROMPT = """
你是一個精通台灣所有手搖飲品牌的專家。
當使用者輸入店名，請提供 10 個熱門推薦品項，分類為：[經典必喝]、[奶茶/鮮奶系]、[清爽原茶/果茶]、[咀嚼控最愛]。
每個品項需包含：品名(name)、推薦原因(description)、黃金比例(best_ratio)、熱量預估(calories: Low/Medium/High)、價格區間(price_range: $/$$/$$$)。
請只輸出 JSON 格式，不要有額外對話。
"""

model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_PROMPT)

# --- 2. 網頁介面 ---
st.title("🧋 台灣手搖飲達人")
st.subheader("不知道喝什麼？輸入店名，我幫你挑 10 個！")

shop_name = st.text_input("請輸入飲料店名稱（例如：五十嵐、一沐日、可不可）", placeholder="請輸入店名...")

if shop_name:
    with st.spinner(f"正在從 {shop_name} 的菜單中尋找最強飲品..."):
        try:
            # 呼叫 Gemini
            response = model.generate_content(f"請推薦 {shop_name} 的 10 個品項")
            # 處理 JSON 格式 (移除 Markdown 的 ```json 標籤)
            raw_json = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(raw_json)
            
            # 顯示店家標語
            st.info(f"✨ {data['shop_info']['name']}：{data['shop_info']['slogan']}")

            # 分類顯示 (使用 Tabs)
            categories = [c['category'] for c in data['recommendations']]
            tabs = st.tabs(categories)

            for i, cat_data in enumerate(data['recommendations']):
                with tabs[i]:
                    # 每行顯示兩個卡片
                    cols = st.columns(2)
                    for idx, item in enumerate(cat_data['items']):
                        with cols[idx % 2]:
                            with st.container(border=True):
                                st.markdown(f"### {item['name']}")
                                st.caption(f"💡 {item['description']}")
                                
                                # 標籤顯示
                                c1, c2, c3 = st.columns(3)
                                c1.metric("黃金比例", item['best_ratio'])
                                
                                cal_icon = "🟢" if item['calories'] == "Low" else "🟡" if item['calories'] == "Medium" else "🔴"
                                c2.markdown(f"**熱量**\n\n{cal_icon} {item['calories']}")
                                
                                c3.markdown(f"**價格**\n\n{item['price_range']}")

        except Exception as e:
            st.error(f"哎呀！出錯了，可能是 API Key 沒設好或是店名太冷門。錯誤訊息：{e}")

# 頁尾資訊
st.divider()
st.caption("本資料由 Google Gemini AI 提供，僅供參考，實際菜單以門市為準。")
