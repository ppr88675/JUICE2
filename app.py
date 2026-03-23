import streamlit as st
import google.generativeai as genai
import json

# --- 1. 設定區 ---
# 在這裡填入你的 Google AI Studio API Key
GOOGLE_API_KEY = "AIzaSyDw7Jbku74XLldpC0ERI6QlZyew4Mlu6JY"

genai.configure(api_key=GOOGLE_API_KEY)

# 設定頁面資訊
st.set_page_config(page_title="手搖飲達人推薦器", page_icon="🧋", layout="wide")

# 定義系統指令
SYSTEM_PROMPT = """
你是一個精通台灣所有手搖飲品牌的專家。
當使用者輸入店名，請提供 10 個熱門推薦品項，分類為：[經典必喝]、[奶茶/鮮奶系]、[清爽原茶/果茶]、[咀嚼控最愛]。

請嚴格按照以下 JSON 格式輸出：
{
  "shop_info": {
    "name": "店家名稱",
    "slogan": "店家標語"
  },
  "recommendations": [
    {
      "category": "分類名稱",
      "items": [
        {
          "name": "品名",
          "description": "推薦原因",
          "best_ratio": "黃金比例",
          "calories": "Low/Medium/High",
          "price_range": "$/$$/$$$"
        }
      ]
    }
  ]
}

請只輸出 JSON 格式，不要有額外對話。
"""

model = genai.GenerativeModel('gemini-3-flash-preview', system_instruction=SYSTEM_PROMPT)

# --- 2. 網頁介面與樣式 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .main {
        background-color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        padding: 12px 16px;
    }
    .drink-card {
        background: white;
        padding: 24px;
        border-radius: 20px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
        transition: transform 0.2s ease;
    }
    .drink-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .drink-name {
        font-size: 1.25rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 8px;
    }
    .drink-desc {
        color: #64748b;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 16px;
    }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 8px;
    }
    .badge-emerald { background: #ecfdf5; color: #059669; }
    .badge-slate { background: #f1f5f9; color: #475569; }
    .badge-amber { background: #fffbeb; color: #d97706; }
    
    .shop-banner {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 40px;
        border-radius: 24px;
        color: white;
        margin-bottom: 40px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧋 台灣手搖飲達人")
st.markdown("<p style='color: #64748b; font-size: 1.1rem;'>輸入店名，為您探索隱藏版最強飲品</p>", unsafe_allow_html=True)

shop_name = st.text_input("", placeholder="例如：五十嵐、一沐日、可不可...")

if shop_name:
    with st.spinner(f"正在調製 {shop_name} 的專屬菜單..."):
        try:
            response = model.generate_content(
                f"請推薦 {shop_name} 的 10 個品項",
                generation_config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            
            # 店家橫幅
            shop_info = data.get('shop_info', {})
            if shop_info:
                st.markdown(f"""
                    <div class="shop-banner">
                        <h1 style="margin:0; font-weight:800;">{shop_info.get('name', shop_name)}</h1>
                        <p style="opacity:0.9; font-size:1.1rem; margin-top:8px;">{shop_info.get('slogan', '')}</p>
                    </div>
                """, unsafe_allow_html=True)

            # 分類顯示
            recommendations = data.get('recommendations', [])
            if recommendations:
                categories = [c.get('category', '推薦') for c in recommendations]
                tabs = st.tabs(categories)

                for i, cat_data in enumerate(recommendations):
                    with tabs[i]:
                        items = cat_data.get('items', [])
                        cols = st.columns(2)
                        for idx, item in enumerate(items):
                            with cols[idx % 2]:
                                # 使用 HTML 渲染精美的卡片
                                calories = item.get('calories', 'Medium')
                                cal_color = "#10b981" if calories == "Low" else "#f59e0b" if calories == "Medium" else "#ef4444"
                                
                                st.markdown(f"""
                                    <div class="drink-card">
                                        <div class="drink-name">{item.get('name', '未知品項')}</div>
                                        <div class="drink-desc">{item.get('description', '探索這款飲品的獨特風味。')}</div>
                                        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                                            <span class="badge badge-emerald">✨ {item.get('best_ratio', '黃金比例')}</span>
                                            <span class="badge badge-slate">💰 {item.get('price_range', '$')}</span>
                                            <span class="badge badge-amber" style="color: {cal_color};">🔥 {calories} Cal</span>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"哎呀！出錯了，可能是 API Key 沒設好或是店名太冷門。錯誤訊息：{e}")

# 頁尾資訊
st.divider()
st.caption("本資料由 Google Gemini AI 提供，僅供參考，實際菜單以門市為準。")
