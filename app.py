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

# --- 3. 側邊欄設定 ---
with st.sidebar:
    st.markdown("### 🛠️ API 設定")
    # 優先從環境變數讀取，若無則要求使用者輸入
    env_api_key = os.environ.get('GEMINI_API_KEY')
    user_api_key = st.text_input("輸入 Gemini API Key", type="password", placeholder="若環境變數已設定則可留空")
    
    # 決定最終使用的 API Key
    api_key = user_api_key if user_api_key else env_api_key
    
    if api_key:
        genai.configure(api_key=api_key)
    else:
        st.warning("⚠️ 尚未偵測到 API Key，請在下方輸入或設定環境變數。")
    
    st.info("💡 提示：您可以到 [Google AI Studio](https://aistudio.google.com/app/apikey) 免費申請 API Key。")
    st.divider()
    st.caption("v2.0 - 視覺升級版")

# --- 4. 系統指令 ---
SYSTEM_PROMPT = """
你是一個精通台灣所有手搖飲品牌的專家。
請根據使用者的店名、心情，以及（如果有提供）菜單圖片，推薦 5-10 個最適合的品項。

請嚴格按照以下 JSON 格式輸出：
{
  "shop_name": "店家名稱",
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
                    "請根據以上資訊提供推薦。"
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
                st.markdown(f"### 📍 {display_name} 必喝清單")
                
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
