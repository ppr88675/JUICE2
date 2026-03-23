import streamlit as st
import google.generativeai as genai
import json
from PIL import Image

# --- 1. 頁面基本設定 ---
st.set_page_config(page_title="BubbleTea AI | 台灣手搖飲達人", page_icon="🧋", layout="centered")

# --- 2. 注入自定義 CSS (美化重點) ---
st.markdown("""
    <style>
    /* 整體背景與字體 */
    .stApp {
        background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
    }
    
    /* 標題樣式 */
    h1 {
        color: #5d4037;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0px;
    }

    /* 按鈕樣式 */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        border: none;
        background-color: #8d6e63;
        color: white;
        height: 3.5em;
        transition: 0.3s;
        font-weight: bold;
        font-size: 1.1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background-color: #5d4037;
        color: #fff;
        transform: scale(1.02);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }

    /* 卡片樣式 (Expander) */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.7) !important;
        border-radius: 12px !important;
        border: 1px solid #d7ccc8 !important;
        margin-bottom: 10px;
        font-weight: 600;
    }
    
    .stExpander {
        border: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* 隱藏 Streamlit 預設選單與頁尾 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 輸入框圓角 */
    .stTextInput > div > div > input {
        border-radius: 12px;
    }
    .stSelectbox > div > div > div {
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

import os

# --- 3. API 設定邏輯 ---
def get_api_key():
    # 1. 優先嘗試從 Streamlit Secrets 讀取 (Streamlit Cloud 專用)
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except:
        pass
    
    # 2. 嘗試從系統環境變數讀取 (AI Studio 預覽或本地測試)
    return os.environ.get('GEMINI_API_KEY')

# 取得金鑰
active_api_key = get_api_key()

with st.sidebar:
    st.markdown("### 🛠️ 系統設定")
    
    if active_api_key:
        # --- 模式 A：已偵測到後台金鑰 ---
        api_key = active_api_key
        st.success("✅ 系統金鑰已就緒")
        st.caption("目前正使用管理員預設金鑰。")
        
        # 只有勾選時才顯示輸入框 (給管理員測試用)
        if st.checkbox("更換測試金鑰"):
            test_key = st.text_input("輸入測試用 API Key", type="password")
            if test_key:
                api_key = test_key
    else:
        # --- 模式 B：未偵測到金鑰 (顯示輸入框) ---
        api_key = st.text_input("輸入 Gemini API Key", type="password", placeholder="請在此貼上您的 API Key")
        if not api_key:
            st.warning("⚠️ 請輸入 API Key 以啟用功能")
            st.info("💡 管理員提示：請至 Streamlit Cloud Secrets 設定 `GEMINI_API_KEY` 以隱藏此框。")

    # 配置 Gemini
    if api_key:
        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            st.error(f"金鑰配置失敗: {e}")
    
    st.divider()
    st.caption("v2.4 - 介面精簡版")

# --- 4. 系統指令 ---
SYSTEM_PROMPT = """
你是一個精通台灣所有手搖飲品牌的專家。
請根據使用者的店名、心情，以及（如果有提供）菜單圖片，推薦 5-10 個最適合的品項。

請嚴格按照以下 JSON 格式輸出：
{
  "shop_name": "店家名稱",
  "official_links": [
    {
      "title": "連結名稱（如：官方網站、FB 粉絲專頁、線上菜單）",
      "url": "網址"
    }
  ],
  "recommendations": [
    {
      "name": "品名",
      "reason": "推薦原因（結合使用者的心情，語氣親切專業）",
      "sugar_ice": "建議的甜度冰塊（黃金比例）",
      "calories": "熱量預估（Low/Medium/High）"
    }
  ]
}

請只輸出 JSON 格式，不要有額外對話。
"""

# --- 5. 主畫面 ---
st.markdown("<h1>🧋 今天喝什麼？</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #795548; font-size: 1.1rem;'>AI 幫你從茫茫菜單中找到最頂的那一杯</p>", unsafe_allow_html=True)
st.write("")

# 輸入框佈局
col1, col2 = st.columns([2, 1])
with col1:
    shop_name = st.text_input("想喝哪間飲料店？", placeholder="例如：五桐號、得正、一沐日...")
with col2:
    mood = st.selectbox("現在心情？", ["想喝清爽", "想咬東西", "壓力大想喝濃", "想喝健康的"])

# 上傳菜單
uploaded_file = st.file_uploader("都不喜歡？上傳這家店的菜單照片，我重新挑！", type=['png', 'jpg', 'jpeg'])

st.write("") # 間距

if st.button("✨ 開始神推薦"):
    if not api_key:
        st.error("請先在側邊欄填入 API Key 喔！")
    elif not shop_name and not uploaded_file:
        st.warning("請輸入店名或上傳菜單圖片。")
    else:
        try:
            with st.spinner('🥤 正在為您調製黃金比例...'):
                # 使用最新的穩定模型
                model = genai.GenerativeModel('gemini-3-flash-preview')
                
                # 建立內容列表 (支援多模態)
                prompt_parts = [
                    SYSTEM_PROMPT,
                    f"使用者想喝的店：{shop_name}",
                    f"目前心情：{mood}",
                    "請提供推薦品項，並盡可能找到該店的官方網站或線上菜單連結。"
                ]
                
                if uploaded_file:
                    img = Image.open(uploaded_file)
                    prompt_parts.append(img)
                    prompt_parts.append("請優先分析圖片中的菜單內容。")

                response = model.generate_content(
                    prompt_parts,
                    generation_config={"response_mime_type": "application/json"}
                )
                
                # 解析 JSON
                data = json.loads(response.text)

                # 顯示推薦結果
                st.balloons()
                display_name = data.get('shop_name', shop_name)
                
                # 標題與連結佈局
                st.markdown(f"### 📍 {display_name} 必喝清單")
                
                # 新增：查看完整菜單區塊
                links = data.get('official_links', [])
                link_cols = st.columns(len(links) + 1 if links else 1)
                
                if links:
                    for i, link in enumerate(links):
                        with link_cols[i]:
                            st.link_button(f"🌐 {link['title']}", link['url'], use_container_width=True)
                
                # 永遠提供一個 Google 搜尋連結作為備案
                with link_cols[-1]:
                    search_url = f"https://www.google.com/search?q={display_name}+菜單+官網"
                    st.link_button("🔍 在 Google 搜尋菜單", search_url, use_container_width=True)
                
                st.write("---")

                recommendations = data.get('recommendations', [])
                if not recommendations:
                    st.warning("AI 暫時找不到適合的推薦，請換個店名試試！")
                else:
                    for idx, drink in enumerate(recommendations, 1):
                        # 根據熱量顯示圖示
                        cal = drink.get('calories', 'Medium')
                        cal_icon = "🟢" if cal == "Low" else "🟡" if cal == "Medium" else "🔴"
                        
                        # 使用 Expander 做出摺疊卡片感
                        with st.expander(f"🥤 {idx}. {drink['name']} | {cal_icon} 熱量：{cal}"):
                            st.markdown(f"**🌟 推薦原因：**\n{drink['reason']}")
                            st.markdown(f"**✨ 黃金比例：** `{drink['sugar_ice']}`")
                            
        except Exception as e:
            st.error(f"哎呀，出錯了！可能是 API 限制或格式問題。錯誤訊息：{e}")

# 頁尾
st.markdown("<br><br><p style='text-align: center; color: #a1887f; font-size: 0.8rem;'>Made with ❤️ by AI Beverage Specialist<br>本資料由 Gemini AI 提供，僅供參考</p>", unsafe_allow_html=True)
