import streamlit as st
import pandas as pd
import calendar
from datetime import datetime

# 1. 페이지 기본 설정
st.set_page_config(page_title="호네츠(Hornets) 관리자", layout="wide")

# 2. 전체 화면 스타일 (달력 CSS 추가!)
st.markdown("""
    <style>
    .main-title { font-size: 46px; font-weight: 900; letter-spacing: -0.5px; padding-bottom: 25px; line-height: 1.2; text-shadow: 2px 2px 0px #CBA052; }
    @media (max-width: 768px) { .main-title { font-size: 30px !important; padding-bottom: 15px; } }
    
    /* 배번표 스타일 */
    .num-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; margin-top: 5px; margin-bottom: 25px;}
    .num-box { border: 1px solid #ddd; border-radius: 4px; padding: 4px 1px; text-align: center; font-size: 12px; box-shadow: 1px 1px 3px rgba(0,0,0,0.05); }
    .low-grade { background-color: #CBA052; color: #000; font-weight: bold; border: 1px solid #B8860B; }
    .high-grade { background-color: #1A1A1A; color: #CBA052; font-weight: bold; border: 1px solid #000; }
    .empty { background-color: #F8F9FA; color: #ced4da; }
    .num-label { font-size: 9px; margin-bottom: 1px; color: #888; }
    
    /* 📅 달력 스타일 */
    .calendar { width: 100%; border-collapse: collapse; table-layout: fixed; margin-bottom: 30px; }
    .calendar th { background-color: #1A1A1A; color: #CBA052; border: 1px solid #444; padding: 8px; text-align: center; font-size: 14px;}
    .calendar td { border: 1px solid #ddd; height: 120px; vertical-align: top; padding: 5px; background-color: #fff; overflow-y: auto; }
    .cal-date { font-weight: bold; color: #333; margin-bottom: 5px; font-size: 14px; }
    .cal-event { font-size: 11px; padding: 4px; margin-bottom: 4px; border-radius: 4px; line-height: 1.3; word-wrap: break-word; }
    </style>
    <div class="main-title">🐝 HORNETS 관리 페이지</div>
    """, unsafe_allow_html=True)

# 3. 사이드바 메뉴 설정
menu = st.sidebar.radio("메뉴 이동", ["1. 회원 명단 및 등번호", "2. 대회 및 시합 일정 (달력)"])

# 공통 구글 시트 기본 URL
base_url = "https://docs.google.com/spreadsheets/d/1Z2QYy2bubBdkj6B-ojk_wPO717TSC2eJbXafCIsXY7U/export?format=csv&gid="

# ----------------------------------------------------
# [메뉴 1] 회원 명단 및 등번호 (유치/저학년 통합 vs 고학년)
# ----------------------------------------------------
if menu == "1. 회원 명단 및 등번호":
    
    # 이제 GID 1개만 사용합니다! (전체 회원 명단)
    members_url = base_url + "878707605"
    
    try:
        df_all = pd.read_csv(members_url)
        
        # 배번 '.0' 제거
        if not df_all.empty and len(df_all.columns) > 0:
            first_col = df_all.columns[0]
            df_all[first_col] = pd.to_numeric(df_all[first_col], errors='coerce').astype('Int64').astype(str)
            df_all[first_col] = df_all[first_col].replace('<NA>', '')
            
        df_all = df_all.fillna("")
        
        # 💡 자동 분류 마법! (줄(Row)에 해당 단어가 있으면 자동으로 표를 나눕니다)
        mask_kinder = df_all.apply(lambda row: row.astype(str).str.contains('유치').any(), axis=1)
        mask_low = df_all.apply(lambda row: row.astype(str).str.contains('저학').any(), axis=1)
        mask_high = df_all.apply(lambda row: row.astype(str).str.contains('고학').any(), axis=1)
        
        df_kinder = df_all[mask_kinder]
        df_low = df_all[mask_low]
        df_high = df_all[mask_high]
        
        def get_num_map_safe(df):
            if df.empty or len(df.columns) < 2: return {}
            temp = df.iloc[:, [0, 1]].copy() 
            temp.columns = ['num', 'name']
            temp['num'] = pd.to_numeric(temp['num'], errors='coerce')
            temp = temp.dropna(subset=['num', 'name'])
            return dict(zip(temp['num'].astype(int), temp['name']))

        # 유치부와 저학년을 하나의 배번 사전(Dict)으로 합치기
        map_kinder_low = {**get_num_map_safe(df_kinder), **get_num_map_safe(df_low)}
        map_high = get_num_map_safe(df_high)
        
        # ==========================================
        # 🟡 1층: 유치부 & 저학년 구역 (명단은 2개, 배번판은 1개)
        # ==========================================
        col1_left, col1_right = st.columns([4, 6])
        with col1_left:
            st.markdown("#### 🐣 유치부 명단")
            st.dataframe(df_kinder, use_container_width=True, hide_index=True)
            st.markdown("#### 🟡 저학년 명단")
            st.dataframe(df_low, use_container_width=True, hide_index=True)
            
        with col1_right:
            st.markdown("#### 🔢 유치부 + 저학년 통합 배번 현황")
            st.markdown("<small>🟡 사용 중 (Gold) | ⚪ 빈 번호</small>", unsafe_allow_html=True)
            grid_html_low = '<div class="num-grid">'
            for i in range(1, 100):
                if i in map_kinder_low:
                    grid_html_low += f'<div class="num-box low-grade"><div class="num-label" style="color:#000;">{i}</div>{map_kinder_low[i]}</div>'
                else:
                    grid_html_low += f'<div class="num-box empty"><div class="num-label">{i}</div>-</div>'
            grid_html_low += "</div>"
            st.markdown(grid_html_low, unsafe_allow_html=True)

        st.markdown("<hr style='margin: 10px 0 30px 0;'>", unsafe_allow_html=True)

        # ==========================================
        # ⚫ 2층: 고학년 구역
        # ==========================================
        col2_left, col2_right = st.columns([4, 6])
        with col2_left:
            st.markdown("#### ⚫ 고학년 (대회반) 명단")
            st.dataframe(df_high, use_container_width=True, hide_index=True)
            
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
# [메뉴 2] 대회 및 시합 일정 (12개월 달력 시스템 📅)
# ----------------------------------------------------
elif menu == "2. 대회 및 시합 일정 (달력)":
    st.subheader("📅 호네츠 시합 & 행사 달력")
    
    schedule_url = base_url + "1081511364"
    
    try:
        df_schedule = pd.read_csv(schedule_url).fillna("")
        
        # '날짜'나 '일시'라는 글자가 들어간 열(Column)을 자동으로 찾습니다.
        date_col = next((col for col in df_schedule.columns if '날짜' in col or '일시' in col or 'date' in col.lower()), None)
        
        if date_col:
            # 컴퓨터가 이해할 수 있는 날짜 포맷으로 변환
            df_schedule['parsed_date'] = pd.to_datetime(df_schedule[date_col], errors='coerce')
            valid_sched = df_schedule.dropna(subset=['parsed_date'])
            
            # 연/월 선택기 만들기
            col_y, col_m, _ = st.columns([2, 2, 6])
            with col_y:
                sel_year = st.selectbox("년도 선택", range(2024, 2030), index=2) # 기본값 2026
            with col_m:
                sel_month = st.selectbox("월 선택", range(1, 13), index=datetime.today().month-1)
                
            # 파이썬 내장 달력 그리기 준비 (일요일부터 시작)
            cal = calendar.Calendar(firstweekday=6)
            month_days = cal.monthdatescalendar(sel_year, sel_month)
            
            # HTML로 달력 테이블 만들기
            html = "<table class='calendar'><tr><th>일</th><th>월</th><th>화</th><th>수</th><th>목</th><th>금</th><th>토</th></tr>"
            
            for week in month_days:
                html += "<tr>"
                for day in week:
                    # 이번 달이 아닌 날짜는 회색 처리
                    day_style = "background-color: #f9f9f9; color: #aaa;" if day.month != sel_month else ""
                    
                    html += f"<td style='{day_style}'><div class='cal-date'>{day.day}</div>"
                    
                    # 해당 날짜에 일정이 있는지 확인
                    day_events = valid_sched[valid_sched['parsed_date'].dt.date == day]
                    for _, ev in day_events.iterrows():
                        # 일정 한 줄로 합치기
                        row_text_full = " ".join([str(ev[c]) for c in df_schedule.columns])
                        
                        # 스타일 로직
                        event_bg = "#f0f2f6"; event_color = "#333"; border = "1px solid #ddd"
                        
                        if ('호네츠' in row_text_full or '헥사' in row_text_full):
                            event_bg = "#ffd966"; event_color = "#000" # 골드
                        if '화이트' in row_text_full:
                            event_bg = "#ffffff"; event_color = "#000"; border = "1px solid #ccc"
                        elif '블랙' in row_text_full:
                            event_bg = "#1a1a1a"; event_color = "#fff"
                        elif '버건디' in row_text_full:
                            event_bg = "#800020"; event_color = "#fff"
                        elif '베이지' in row_text_full:
                            event_bg = "#F5F5DC"; event_color = "#000"
                            
                        # 달력 박스 안에 띄울 텍스트 (날짜 빼고 요약해서 보여줌)
                        display_text = ""
                        for c in df_schedule.columns:
                            if c not in [date_col, 'parsed_date', '참가멤버'] and str(ev[c]).strip() != "":
                                display_text += f"<b>{str(ev[c])}</b><br>"
                                
                        html += f"<div class='cal-event' style='background:{event_bg}; color:{event_color}; border:{border};'>{display_text}</div>"
                        
                    html += "</td>"
                html += "</tr>"
            html += "</table>"
            
            st.markdown(html, unsafe_allow_html=True)
            
            # 혹시 자세한 표로도 보고 싶을까 봐 달력 아래에 원본 데이터도 접었다 펼칠 수 있게 추가
            with st.expander("📝 전체 일정 표로 보기 (클릭하여 펼치기)"):
                st.dataframe(df_schedule.drop(columns=['parsed_date']), use_container_width=True, hide_index=True)
                
        else:
            st.error("구글 시트에 '날짜' 또는 '일시'라는 이름의 열(Column)이 필요합니다!")
            
    except Exception as e:
        st.error(f"일정 데이터를 불러올 수 없습니다. 오류: {e}")
