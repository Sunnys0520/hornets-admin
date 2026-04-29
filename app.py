import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="호네츠(Hornets) 관리자", layout="wide")

# 2. 전체 화면 스타일
st.markdown("""
    <style>
    .main-title { font-size: 46px; font-weight: 900; letter-spacing: -0.5px; padding-bottom: 25px; line-height: 1.2; text-shadow: 2px 2px 0px #CBA052; margin-top: 10px;}
    @media (max-width: 768px) { .main-title { font-size: 30px !important; padding-bottom: 15px; } }
    
    .num-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; margin-top: 5px; margin-bottom: 25px;}
    .num-box { border: 1px solid #ddd; border-radius: 4px; padding: 4px 1px; text-align: center; font-size: 12px; box-shadow: 1px 1px 3px rgba(0,0,0,0.05); }
    .low-grade { background-color: #CBA052; color: #000; font-weight: bold; border: 1px solid #B8860B; }
    .high-grade { background-color: #1A1A1A; color: #CBA052; font-weight: bold; border: 1px solid #000; }
    .empty { background-color: #F8F9FA; color: #ced4da; }
    .num-label { font-size: 9px; margin-bottom: 1px; color: #888; }
    
    .calendar { width: 100%; border-collapse: collapse; table-layout: fixed; margin-bottom: 30px; }
    .calendar th { background-color: #1A1A1A; color: #CBA052; border: 1px solid #444; padding: 8px; text-align: center; font-size: 14px;}
    .calendar td { border: 1px solid #ddd; height: 120px; vertical-align: top; padding: 5px; background-color: #fff; overflow-y: auto; }
    .cal-date { font-weight: bold; color: #333; margin-bottom: 5px; font-size: 14px; }
    .cal-event { font-size: 11px; padding: 4px; margin-bottom: 4px; border-radius: 4px; line-height: 1.3; word-wrap: break-word; }
    </style>
    """, unsafe_allow_html=True)

# 🐝 로고와 타이틀을 나란히 배치
col_logo, col_title = st.columns([1, 9])
with col_logo:
    # 깃허브에 logo.jpg 파일이 있으면 보여주고, 없으면 기본 🐝 이모지 출력
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    else:
        st.markdown("<div style='font-size: 50px; text-align: center;'>🐝</div>", unsafe_allow_html=True)

with col_title:
    st.markdown('<div class="main-title">HORNETS 관리 페이지</div>', unsafe_allow_html=True)

# 3. 사이드바 메뉴 설정
menu = st.sidebar.radio("메뉴 이동", ["1. 회원 명단 및 등번호", "2. 대회 및 시합 일정 (달력)"])

base_url = "https://docs.google.com/spreadsheets/d/1Z2QYy2bubBdkj6B-ojk_wPO717TSC2eJbXafCIsXY7U/export?format=csv&gid="

# ----------------------------------------------------
# [메뉴 1] 회원 명단 및 등번호
# ----------------------------------------------------
if menu == "1. 회원 명단 및 등번호":
    members_url = base_url + "878707605"
    
    try:
        df_all = pd.read_csv(members_url)
        
        # 💡 [버그 수정] 무작정 첫 번째 열을 지우지 않고, 이름이 '등번호'인 열만 찾아서 소수점 제거!
        if '등번호' in df_all.columns:
            df_all['등번호'] = pd.to_numeric(df_all['등번호'], errors='coerce').astype('Int64').astype(str)
            df_all['등번호'] = df_all['등번호'].replace('<NA>', '')
            
        df_all = df_all.fillna("")
        
        # 구분 열(또는 전체)에서 해당 단어 찾기
        mask_kinder = df_all.apply(lambda row: row.astype(str).str.contains('유치').any(), axis=1)
        mask_low = df_all.apply(lambda row: row.astype(str).str.contains('저학').any(), axis=1)
        mask_high = df_all.apply(lambda row: row.astype(str).str.contains('고학').any(), axis=1)
        
        df_kinder = df_all[mask_kinder]
        df_low = df_all[mask_low]
        df_high = df_all[mask_high]
        
        # 💡 [버그 수정] 배번판을 그릴 때 정확히 '등번호'와 '성명' 열을 찾아오도록 수정
        def get_num_map_safe(df):
            if df.empty: return {}
            # 시트에 '등번호', '성명' 열이 있다고 가정
            if '등번호' in df.columns and '성명' in df.columns:
                temp = df[['등번호', '성명']].copy()
            elif len(df.columns) >= 3:
                # 만약 이름을 다르게 썼다면, 2번째(인덱스1)와 3번째(인덱스2) 열을 강제로 가져옴
                temp = df.iloc[:, [1, 2]].copy() 
            else:
                return {}
                
            temp.columns = ['num', 'name']
            temp['num'] = pd.to_numeric(temp['num'], errors='coerce')
            temp = temp.dropna(subset=['num', 'name'])
            return dict(zip(temp['num'].astype(int), temp['name']))

        # 유치+저학년 합치기
        map_kinder_low = {**get_num_map_safe(df_kinder), **get_num_map_safe(df_low)}
        map_high = get_num_map_safe(df_high)
        
        # ==========================================
        # 🟡 1층: 유치부 & 저학년 구역
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
        st.error(f"데이터를 불러올 수 없습니다. 시트의 열 이름('등번호', '성명' 등)을 확인해 주세요. 상세 오류: {e}")

# ----------------------------------------------------
# [메뉴 2] 대회 및 시합 일정 (달력)
# ----------------------------------------------------
elif menu == "2. 대회 및 시합 일정 (달력)":
    st.subheader("📅 호네츠 시합 & 행사 달력")
    
    schedule_url = base_url + "1081511364"
    
    try:
        df_schedule = pd.read_csv(schedule_url).fillna("")
        
        date_col = next((col for col in df_schedule.columns if '날짜' in col or '일시' in col or 'date' in col.lower()), None)
        
        if date_col:
            df_schedule['parsed_date'] = pd.to_datetime(df_schedule[date_col], errors='coerce')
            valid_sched = df_schedule.dropna(subset=['parsed_date'])
            
            col_y, col_m, _ = st.columns([2, 2, 6])
            with col_y:
                sel_year = st.selectbox("년도 선택", range(2024, 2030), index=2)
            with col_m:
                sel_month = st.selectbox("월 선택", range(1, 13), index=datetime.today().month-1)
                
            cal = calendar.Calendar(firstweekday=6)
            month_days = cal.monthdatescalendar(sel_year, sel_month)
            
            html = "<table class='calendar'><tr><th>일</th><th>월</th><th>화</th><th>수</th><th>목</th><th>금</th><th>토</th></tr>"
            
            for week in month_days:
                html += "<tr>"
                for day in week:
                    day_style = "background-color: #f9f9f9; color: #aaa;" if day.month != sel_month else ""
                    html += f"<td style='{day_style}'><div class='cal-date'>{day.day}</div>"
                    
                    day_events = valid_sched[valid_sched['parsed_date'].dt.date == day]
                    for _, ev in day_events.iterrows():
                        row_text_full = " ".join([str(ev[c]) for c in df_schedule.columns])
                        
                        event_bg = "#f0f2f6"; event_color = "#333"; border = "1px solid #ddd"
                        
                        if ('호네츠' in row_text_full or '헥사' in row_text_full):
                            event_bg = "#ffd966"; event_color = "#000"
                        if '화이트' in row_text_full:
                            event_bg = "#ffffff"; event_color = "#000"; border = "1px solid #ccc"
                        elif '블랙' in row_text_full:
                            event_bg = "#1a1a1a"; event_color = "#fff"
                        elif '버건디' in row_text_full:
                            event_bg = "#800020"; event_color = "#fff"
                        elif '베이지' in row_text_full:
                            event_bg = "#F5F5DC"; event_color = "#000"
                            
                        display_text = ""
                        for c in df_schedule.columns:
                            if c not in [date_col, 'parsed_date', '참가멤버'] and str(ev[c]).strip() != "":
                                display_text += f"<b>{str(ev[c])}</b><br>"
                                
                        html += f"<div class='cal-event' style='background:{event_bg}; color:{event_color}; border:{border};'>{display_text}</div>"
                        
                    html += "</td>"
                html += "</tr>"
            html += "</table>"
            
            st.markdown(html, unsafe_allow_html=True)
            
            with st.expander("📝 전체 일정 표로 보기 (클릭하여 펼치기)"):
                st.dataframe(df_schedule.drop(columns=['parsed_date']), use_container_width=True, hide_index=True)
                
        else:
            st.error("구글 시트에 '날짜' 또는 '일시'라는 이름의 열(Column)이 필요합니다!")
            
    except Exception as e:
        st.error(f"일정 데이터를 불러올 수 없습니다. 오류: {e}")
