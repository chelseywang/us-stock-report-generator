import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import datetime

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="美股外電報告產生器",
    page_icon="🇺🇸",
    layout="wide"
)

# --- 2. 深度 CSS 客製化 (美式經典紅藍風格) ---
st.markdown("""
    <style>
    /* 全站基礎設定 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Microsoft JhengHei', 'Noto Sans TC', sans-serif;
    }
    
    /* 這裡保持淺色背景，讓白底卡片和紅色元素更凸顯 */
    .stApp {
        background-color: #f4f6f9;
    }
    
    .block-container {
        padding-top: 0rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 100%;
    }

    /* Header - 美國國旗紅 (Old Glory Red) */
    .header-container {
        background-color: #B31942; 
        padding: 1.8rem 4rem;
        margin-left: -3rem;
        margin-right: -3rem;
        margin-bottom: 2rem;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-bottom: 4px solid #0A3161; /* 底部加一條海軍藍的線條點綴 */
    }
    
    /* 卡片樣式 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    /* 步驟標題 - 海軍藍 */
    .step-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        font-size: 1.15rem;
        font-weight: 700;
        color: #0A3161;
    }
    
    /* 步驟數字圓圈 - 美國紅 */
    .step-number {
        background-color: #B31942;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
        font-weight: 800;
        font-size: 1rem;
        flex-shrink: 0;
    }

    /* 檔案上傳區 */
    div[data-testid="stFileUploader"] section {
        border: 2px dashed #94a3b8;
        background-color: #ffffff !important;
        border-radius: 12px;
        padding: 40px 20px;
        align-items: center;
        justify-content: center;
        text-align: center;
        position: relative;
    }
    
    /* 上傳區圖示改為紅色 (#B31942) */
    div[data-testid="stFileUploader"] section::before {
        content: '';
        display: block;
        width: 64px;
        height: 64px;
        margin: 0 auto 15px auto;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%23B31942" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/></svg>');
        background-repeat: no-repeat;
        background-position: center;
    }

    div[data-testid="stFileUploader"] section:hover {
        border-color: #B31942;
        background-color: #fdf6f6;
    }
    
    div[data-testid="stFileUploader"] small {
        font-size: 0.9rem;
        color: #64748b;
    }
    
    /* 輸入框樣式 */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div { 
        background-color: #ffffff !important; 
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
        padding: 4px;
    }
    
    .stMarkdown label, .stDateInput label, .stSelectbox label, .stTextArea label, .stTextInput label {
        font-weight: 600 !important;
        color: #334155 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* 按鈕樣式 */
    div.stButton > button {
        width: 100%;
        height: 50px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.05rem;
        border: none;
        transition: all 0.2s;
    }
    
    div.stButton > button[kind="secondary"] {
        background-color: #0A3161; /* 海軍藍次要按鈕 */
        color: white;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #061e3d;
    }
    
    div.stButton > button[kind="primary"] {
        background-color: #B31942; /* 美國紅主要按鈕 */
        color: white;
        box-shadow: 0 4px 6px -1px rgba(179, 25, 66, 0.3);
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #8C1333;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px -1px rgba(179, 25, 66, 0.4);
    }
    
    /* ✨ 程式碼/文字輸出區塊 (紅框版) */
    div[data-testid="stCodeBlock"] {
        background-color: #fdf6f6 !important; /* 極淡的紅色底 */
        border: 2px solid #B31942 !important; /* 美國紅邊框 */
        border-radius: 8px !important;
        padding: 10px !important;
        margin-top: 5px !important;
    }

    div[data-testid="stCodeBlock"] pre {
        background-color: transparent !important;
    }

    div[data-testid="stCodeBlock"] code {
        color: #0f172a !important; 
        background-color: transparent !important;
        font-family: 'Microsoft JhengHei', 'Noto Sans TC', sans-serif !important;
        font-size: 16px !important;
        font-weight: 700 !important;
    }

    /* 確保複製按鈕是紅色的 */
    div[data-testid="stCodeBlock"] button {
        color: #B31942 !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
    """, unsafe_allow_html=True)

# --- 3. 頂部紅色 Header ---
st.markdown("""
    <div class="header-container">
        <div style="display:flex; align-items:center;">
            <div style="background-color:rgba(255,255,255,0.2); padding:10px; border-radius:10px; margin-right:15px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
            </div>
            <div>
                <h1 style="margin:0; font-size:1.6rem; font-weight:700; letter-spacing:0.5px;">美股外電報告產生器</h1>
                <p style="margin:4px 0 0 0; color:#e2e8f0; font-size:0.9rem;">元大證券國際金融部專用格式</p>
            </div>
        </div>
        <div style="background-color:rgba(255,255,255,0.15); padding:6px 16px; border-radius:20px; font-size:0.85rem; font-weight:500;">
            V 8.1 (美式紅藍配色)
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 4. 邏輯處理 ---
api_key = None
available_models = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro"]

if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    try:
        genai.configure(api_key=api_key)
        fetched_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                name = m.name.replace("models/", "")
                fetched_models.append(name)
        
        if fetched_models:
            fetched_models.sort(reverse=True)
            available_models = fetched_models
            if "gemini-2.0-flash-exp" not in available_models:
                available_models.insert(0, "gemini-2.0-flash-exp")
    except Exception as e:
        pass 

# --- 預設 Prompt 模板 ---
DEFAULT_PROMPT_TEMPLATE = """請你扮演「元大證券國際金融部研究員」，根據我上傳的 PDF 券商報告（內容附在最後），整理成「美股外電格式」。
若報告涉及 ETF，請優先抓取「AUM (資產管理規模)」數據，而非 Market Cap。
請完整依照以下規範輸出，排版格式與空行必須嚴格遵守：

1️⃣ 開頭固定：
早安！{date}
美股外電整理 元大證券國金部

(⚠️注意：此處空兩行)

2️⃣ 個股格式（每檔公司兩段，請嚴格遵守空格行數）

🇺🇸[公司代號 公司名稱]
第一段（150–170字）：(⚠️注意：此處緊接公司名稱，不可空行)。
內容整理美系／歐系券商分析摘要，說明產業趨勢、公司展望、次季動能、成長關鍵。不得提及目標價與評級。

(⚠️注意：第一段與第二段之間必須「空一行」)

第二段（80–100字）：
第一句必須依照以下邏輯撰寫：

目標價有變動時： 「券商將目標價從 XXXX 美元（上調／下調）至 OOOO 美元，評級（維持／調升為／調降為）[具體評級內容，如：買進/中立]。」

目標價/評級維持時： 「券商將目標價維持在 OOOO 美元，評級維持 [具體評級內容，如：買進/持有]。」
後續補充： 券商調整原因、市場關注風險與主軸。

(⚠️注意：不同公司之間請務必「空兩行」區隔)

3️⃣ 範例參考（請完全複製此排版間距與文字邏輯）：

🇺🇸AAPL Apple Inc.
美系券商指出，Apple 在即將到來的秋季發表會中，有望透過新一代 AI 晶片大幅提升終端設備的運算能力... (緊接上一行，無空行)
...預期服務收入將成為下一季度的主要增長引擎，並帶動整體毛利率擴張。

券商將目標價從 185 美元上調至 210 美元，評級維持買進。該調整主因是看好其 AI 策略將加速消費者換機潮，風險則需留意大中華區市場的競爭壓力及供應鏈地緣政治風險。

🇺🇸NVDA NVIDIA Corp.
歐系券商參加 NVIDIA 的開發者大會後指出，新一代架構產品的需求遠超預期... (緊接上一行，無空行)
...並計畫擴大與雲端服務供應商(CSP)的合作，以鞏固其在資料中心市場的絕對領先地位。

券商將目標價維持在 950 美元，評級維持買進。儘管短期內面臨產能瓶頸，但考量其強大的軟硬體生態系護城河，長期成長動能依然無虞，需關注競爭對手自研晶片的進展。

(⚠️注意：最後這句免責聲明前也要空兩行)

以上資料為元大證券依上手提供研究報告摘譯，僅供內部教育訓練使用。"""

# --- 5. 介面佈局 ---
col_left, col_right = st.columns([0.45, 0.55], gap="large")

with col_left:
    # === 卡片 1: 上傳 ===
    with st.container(border=True):
        st.markdown("""
            <div class="step-header">
                <div class="step-number">1</div>
                <div>上傳券商 PDF 報告</div>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "將 PDF 拖曳至此框框中，或點擊選取檔案 (支援多檔)", 
            type=["pdf"], 
            accept_multiple_files=True,
        )
        
        if uploaded_files:
            st.success(f"✅ 已成功讀取 {len(uploaded_files)} 份檔案")

    # === 卡片 2: 設定 ===
    with st.container(border=True):
        st.markdown("""
            <div class="step-header">
                <div class="step-number">2</div>
                <div>設定與模型選擇</div>
            </div>
        """, unsafe_allow_html=True)
        
        report_date = st.date_input("報告日期", datetime.date.today())
        
        st.write("")
        st.markdown("**👇 信件標題 (點擊右上角圖示即可複製)**")
        
        # 格式化日期：YYYY/MM/DD
        formatted_date = report_date.strftime("%Y/%m/%d")
        title_text = f"早安！{formatted_date} 美股外電整理 元大證券國金部"
        
        st.code(title_text, language="text")
        
        st.write("") 
        
        selected_model_name = st.selectbox(
            "Google Gemini 模型 (自動偵測可用清單)",
            available_models,
            index=0, 
            help="系統已自動連結 API 並列出所有可用模型，若遇額度問題請切換其他版本。"
        )
        
        if api_key:
            st.caption(f"✓ API 連線正常，共偵測到 {len(available_models)} 個模型")
        else:
            st.error("⚠️ 未偵測到 Secrets API Key，請檢查 GitHub Secrets 設定。")

    # === 卡片 3 ===
    with st.container(border=True):
        with st.expander("✏️ 自定義 Prompt 指令 (進階設定)", expanded=False):
            st.caption("您可以在此修改 AI 的指令模板。`{date}` 會自動替換為上方選擇的日期。")
            user_custom_prompt = st.text_area(
                "Prompt 內容編輯",
                value=DEFAULT_PROMPT_TEMPLATE,
                height=300,
                label_visibility="collapsed"
            )

    # === 按鈕區 ===
    c1, c2 = st.columns(2)
    with c1:
        show_prompt_btn = st.button("📋 複製完整指令", type="secondary")
    with c2:
        generate_btn = st.button("✨ AI 直接生成", type="primary", disabled=not (uploaded_files and api_key))

# --- 6. 核心生成邏輯 ---
final_prompt = ""
extracted_text = ""

if uploaded_files:
    for pdf_file in uploaded_files:
        try:
            reader = PdfReader(pdf_file)
            file_text = ""
            for page in reader.pages:
                file_text += page.extract_text() + "\n"
            extracted_text += f"\n\n=== 檔案: {pdf_file.name} ===\n{file_text}"
        except Exception as e:
            st.error(f"檔案 {pdf_file.name} 解析失敗: {e}")

    date_str = report_date.strftime("%Y/%m/%d")
    instruction_part = user_custom_prompt.replace("{date}", date_str)
    
    final_prompt = f"""{instruction_part}

【以下是 PDF 內容】：
{extracted_text}
"""

# --- 7. 右側輸出區 ---
with col_right:
    with st.container(border=True):
        st.markdown('<div class="step-header">輸出結果 (請注意目標價、日期、券商標記是否符合原文)</div>', unsafe_allow_html=True)
        
        if show_prompt_btn and final_prompt:
            st.info("指令已生成，請點擊右上角複製：")
            st.code(final_prompt, language="text")

        if generate_btn:
            status_box = st.empty()
            with status_box.container():
                st.image("https://i.gifer.com/ZKZg.gif", width=100)
                st.info(f"🤖 AI 正在努力奔跑分析中... ({selected_model_name})，請稍候片刻！")
            
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(selected_model_name)
                response = model.generate_content(final_prompt)
                result_text = response.text
                
                status_box.empty()
                st.success("✅ 報告生成完成！請點擊下方紅框框右上角的 📄 圖示進行複製")
                
                st.code(result_text, language="text")
                
            except Exception as e:
                status_box.error(f"生成失敗: {str(e)}")
                st.error("請確認 API Key 是否有效，或嘗試更換其他模型。")
        
        elif not show_prompt_btn:
             st.markdown("""
            <div style="height:550px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#94a3b8; background-color:white;">
                <p style="font-size:1.2rem; font-weight:500; color:#cbd5e1;">等待 PDF 解析與生成...</p>
                <p style="font-size:0.9rem; color:#94a3b8; margin-top:10px;">請在左側上傳檔案並按下「AI 直接生成」</p>
            </div>
            """, unsafe_allow_html=True)
