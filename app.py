import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(page_title="호네츠(Hornets) 관리자", layout="wide")

# 2. 전체 화면 스타일 및 폰트 크기 설정
st.markdown("""
    <style>
    /* 메인 타이틀에 호네츠 골드 그림자 포인트 추가 */
    .main-title { font-size: 46px; font-weight: 900; letter-spacing: -0.5px; padding-bottom: 25px; line-height: 1.2; text-shadow: 2px 2px 0px #CBA052; }
    @media (max-width: 768px) { .main-title { font-size: 30px !important; padding-bottom: 15px; } }
    
    /* 배번표 컴팩트 디자인 */
    .num-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; margin-top: 5px; margin-bottom: 25px;}
    .num-box { border: 1px solid #ddd; border-radius: 4px; padding: 4px 1px; text-align: center; font-size: 12px; box-shadow: 1px 1px 3px rgba(0,0,0,0.05); }
    
    /* 🐝 호네츠 테마 색상 적용 */
    .low-grade { background-color: #CBA052; color: #000; font-weight: bold; border: 1px solid #B8860B; }
    .high-grade { background-color: #1A1A1A; color: #CBA052; font-weight: bold; border: 1px solid #000; }
    .empty { background-color: #F8F9FA; color: #ced4da; }
    
    .num-label { font-size: 9px; margin-bottom: 1px; color: #888; }
    </style>
    <div class="main-title">🐝 HORNETS 관리 페이지</div>
    """, unsafe_allow_html=True)

# 3. 사이드바 메뉴 설정
menu = st.sidebar.radio("메뉴 이동", ["1. 회원 명단 및 등번호", "2. 대회 및 시합 일정"])

# 공통 구글 시트 기본 URL (GID 제외)
base_url = "https://docs.google.com/spreadsheets/d/1Z2QYy2bubBdkj6B-ojk_wPO717TSC2eJbXafCIsXY7U/export?format=csv&gid="

# ----------------------------------------------------
# [메뉴 1] 회원 명단 및 등번호
# ----------------------------------------------------
if menu == "1. 회원 명단 및 등번호":
    
    low_grade_url = base_url + "878707605"
    high_grade_url = base_url + "1898750252"
    
    try:
        df_low = pd.read_csv(low_grade_url)
        df_high = pd.read_csv(high_grade_url)
        
        # 배번 컬럼의 '.0' 소수점 제거 로직
        for df in [df_low, df_high]:
            if not df.empty and len(df.columns) > 0:
                first_col = df.columns[0]
                df[first_col] = pd.to_numeric(df[first_col], errors='coerce').astype('Int64').astype(str)
                df[first_col] = df[first_col].replace('<NA>', '')
                
        df_low = df_low.fillna("")
        df_high = df_high.fillna("")
        
        def get_num_map_safe(df):
            if df.empty or len(df.columns) < 2: return {}
            temp = df.iloc[:, [0, 1]].copy() 
            temp.columns = ['num', 'name']
            temp['num'] = pd.to_numeric(temp['num'], errors='coerce')
            temp = temp.dropna(subset=['num', 'name'])
            return dict(zip(temp['num'].astype(int), temp['name']))

        map_low = get_num_map_safe(df_low)
        map_high = get_num_map_safe(df_high)
        
        # 🟡 1층: 저학년 구역
        col1_left, col1_right = st.columns([4, 6])
        with col1_left:
            st.markdown("#### 🟡 저학년 (취미반) 명단")
            st.dataframe(df_low, use_container_width=True, hide_index=True, height=350)
        with col1_right:
            st.markdown("#### 🔢 저학년 배번 현황")
            st.markdown("<small>🟡 사용 중 (Gold) | ⚪ 빈 번호</small>", unsafe_allow_html=True)
            grid_html_low = '<div class="num-grid">'
            for i in range(1, 100):
                if i in map_low:
                    grid_html_low += f'<div class="num-box low-grade"><div class="num-label" style="color:#000;">{i}</div>{map_low[i]}</div>'
                else:
                    grid_html_low += f'<div class="num-box empty"><div class="num-label">{i}</div>-</div>'
            grid_html_low += "</div>"
            st.markdown(grid_html_low, unsafe_allow_html=True)

        st.markdown("<hr style='margin: 10px 0 30px 0;'>", unsafe_allow_html=True)

        # ⚫ 2층: 고학년 구역
        col2_left, col2_right = st.columns([4, 6])
        with col2_left:
            st.markdown("#### ⚫ 고학년 (대회반) 명단")
            st.dataframe(df_high, use_container_width=True, hide_index=True, height=350)
        with col2_right:
            st.markdown("#### 🔢 고학년 배번 현황")
            st.markdown("<small>⚫ 사용 중 (Black) | ⚪ 빈 번호</small>", unsafe_allow_html=True)
            grid_html_high = '<div class="num-grid">'
            for i in range(1, 100):
                if i in map_high:
                    grid_html_high += f'<div class="num-box high-grade"><div class="num-label" style="color:#CBA052;">{i}</div>{map_high[i]}</div>'
                else:
                    grid_html_high += f'<div class="num-box empty"><div class="num-label">{i}</div>-</div>'
            grid_html_high += "</div>"
            st.markdown(grid_html_high, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"데이터를 불러올 수 없습니다. 오류: {e}")

# ----------------------------------------------------
# [메뉴 2] 대회 및 시합 일정
# ----------------------------------------------------
elif menu == "2. 대회 및 시합 일정":
    st.subheader("🗓️ 2. 대회 및 시합 일정")
    
    schedule_url = base_url + "1081511364"
    
    try:
        df_schedule = pd.read_csv(schedule_url).fillna("")
        
        # 🎨 데이터프레임 색칠 로직 (조건부 서식)
        def highlight_schedule(x):
            df_styler = pd.DataFrame('', index=x.index, columns=x.columns)
            
            for idx, row in x.iterrows():
                for col in x.columns:
                    val = str(row[col]).strip()
                    
                    # 💡 조건 1: 호네츠, 헥사 -> 🐝 골드 바탕
                    # 단, 열 이름(col)에 '참가멤버'가 포함되어 있으면 무시!
                    if ('호네츠' in val or '헥사' in val) and ('참가멤버' not in str(col)):
                        df_styler.at[idx, col] = 'background-color: #ffd966; color: black; font-weight: bold;'
                    
                    # 조건 2: 유니폼 색상 -> 👕 단어에 맞춰 배경색/글자색 지정
                    elif '화이트' in val:
                        df_styler.at[idx, col] = 'background-color: #ffffff; color: black; border: 1px solid #ccc;'
                    elif '블랙' in val:
                        df_styler.at[idx, col] = 'background-color: #1a1a1a; color: white; font-weight: bold;'
                    elif '베이지' in val:
                        df_styler.at[idx, col] = 'background-color: #F5F5DC; color: black; font-weight: bold;'
                    elif '버건디' in val:
                        df_styler.at[idx, col] = 'background-color: #800020; color: white; font-weight: bold;'
                        
            return df_styler

        st.markdown("앞으로 예정된 시합 및 행사 일정입니다.")
        
        styled_schedule = df_schedule.style.apply(highlight_schedule, axis=None)
        st.dataframe(styled_schedule, use_container_width=True, hide_index=True, height=500)
        
    except Exception as e:
        st.error(f"일정 데이터를 불러올 수 없습니다. 오류: {e}")