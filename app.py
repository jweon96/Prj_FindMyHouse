# -*- encoding:utf-8 -*-

import streamlit as st
import math
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu

SEOUL_PUBLIC_API = st.secrets["api_credentials"]["SEOUL_PUBLIC_API"]
MAIL_KEY = st.secrets["api_credentials"]["MAIL_KEY"]

@st.cache_data
def load_data():
    df = pd.read_csv('./data/data.csv')
    data = df.loc[:, ['SGG_NM',  # 자치구명
    'BJDONG_NM',  # 법정동명
    'CNTRCT_DE',  # 계약일
    'RENT_GBN',  # 전월세 구분
    'RENT_AREA',  # 임대면적
    'RENT_GTN',  # 보증금(만원)
    'RENT_FEE',  # 임대료(만원)
    'BLDG_NM',  # 건물명
    'BUILD_YEAR',  # 건축년도
    'HOUSE_GBN_NM',  # 건물용도
    'BEFORE_GRNTY_AMOUNT',  # 종전보증금
    'BEFORE_MT_RENT_CHRGE']]  # 종전임대료
    data['평수'] = data['RENT_AREA'] * 0.3025
    data['BLDG_NM'] = data['BLDG_NM'].fillna(data['HOUSE_GBN_NM'])
    return data

# 임대료 보증금 평균 그래프
def plot_graph(data, x, y1, y2=None, secondary_y=False, title=''):
    fig = make_subplots(specs=[[{"secondary_y": secondary_y}]])    
    # y1에 대한 막대 차트 추가
    fig.add_trace(go.Bar(x=data[x], y=data[y1],
                         name='보증금 평균', marker=dict(color=data[y1], colorscale='Blues')), secondary_y=False)    
    # y2가 제공되면 y2에 대한 선 차트 추가
    if y2:    
        fig.add_trace(go.Scatter(x=data[x], y=data[y2], name='임대료 평균', line=dict(color='white')), secondary_y=True)
    # 레이아웃 및 축 제목 업데이트
    fig.update_layout(title=title)
    fig.update_yaxes(title_text='보증금(만 원)', secondary_y=False, tickformat=',.0f')
    if y2:
        fig.update_yaxes(title_text='임대료(만 원)', secondary_y=True, tickformat=',.0f')
    # Streamlit에서 Plotly 차트 표시
    st.plotly_chart(fig, use_container_width=True)

# 표를 생성하는 함수
def show_dataframe(dataframe):
    # 사용자가 체크박스를 선택하면 표를 보여줌
    if st.checkbox('표 보이기'):
        # 표를 출력함
        st.dataframe(dataframe, hide_index=True, use_container_width=True)

# 메인 페이지
def main_page():
    st.title("🏠 내 집을 찾아서(FindMyHouse)")
    st.subheader("서울 집 값, 어디까지 알아보고 오셨어요?")
    st.markdown("* 본 프로젝트는 서울 부동산 시장에서 적절한 주택을 찾는 과정을 지원하는 것을 목표로 합니다.")
    st.markdown("* 사용자가 원하는 조건을 입력하면 서울에서 필요한 조건에 따른 부동산 시세를 그래프 및 도표 형태로 보여줍니다.")
    st.markdown("* 이를 통해 사용자 입장에서 필요한 전·월세 실거래 정보를 한눈에 확인하고, 위치별 시세를 비교하여 집을 구하는 시간을 단축할 수 있습니다.\n\n")
    st.markdown("\n")
    st.markdown("\n")

    st.subheader("프로젝트 개요")
    st.markdown("멀티캠퍼스 멀티잇 데이터 분석 & 엔지니어 34회차")
    st.markdown("Team 1 Mini-Project : '내 집을 찾아서'  [GitHub](https://github.com/JinaaK/apiproject2402)")

# 자치구별 시세 페이지
def sgg_page(recent_data):
    st.title("자치구별 시세")

    # 최대 평수 구해서 정수로 나타내기(반올림)
    max_area_value = math.ceil(recent_data['평수'].max())

    # 필터 설정
    rent_filter = st.selectbox('전·월세', recent_data['RENT_GBN'].unique())
    house_filter = st.multiselect('건물용도', recent_data['HOUSE_GBN_NM'].unique())
    area_filter = st.slider('평수', min_value=0, max_value=max_area_value, value=(0, max_area_value))

    # 필터 적용
    filtered_recent_data = recent_data[(recent_data['RENT_GBN'] == rent_filter) &
                    (recent_data['HOUSE_GBN_NM'].isin(house_filter)) &
                    (recent_data['평수'] >= area_filter[0]) &
                    (recent_data['평수'] <= area_filter[1])]

    # 자치구별 평균 계산
    average_data = filtered_recent_data.groupby('SGG_NM').agg({'RENT_FEE': 'mean', 'RENT_GTN': 'mean', '평수': 'mean'}).reset_index()

    # 그래프 및 표 생성
    if rent_filter == '월세' and not average_data.empty:
        plot_graph(average_data, x='SGG_NM', y1='RENT_GTN', y2='RENT_FEE', secondary_y=True, title='자치구별 시세')
        show_dataframe(average_data[['SGG_NM', 'RENT_GTN', 'RENT_FEE', '평수']].rename(columns={'SGG_NM': '자치구', 'RENT_GTN': '보증금 평균', 'RENT_FEE': '임대료 평균', '평수': '평수 평균'}))
    elif rent_filter == '전세' and not average_data.empty:
        plot_graph(average_data, x='SGG_NM', y1='RENT_GTN', title='자치구별 시세')
        show_dataframe(average_data[['SGG_NM', 'RENT_GTN', '평수']].rename(columns={'SGG_NM': '자치구', 'RENT_GTN': '보증금 평균', 'RENT_FEE': '임대료 평균', '평수': '평수 평균'}))
    else:
        st.write("최근 1개월 내 계약 내역이 없습니다. 다른 옵션을 선택하세요.")

# 법정동별 시세 페이지
def bjdong_page(recent_data):
    st.title("법정동별 시세")

    # 최대 평수 구해서 정수로 나타내기(반올림)
    max_area_value = math.ceil(recent_data['평수'].max())

    # 필터 설정
    rent_filter = st.selectbox('전·월세', recent_data['RENT_GBN'].unique())
    sgg_filter = st.selectbox('자치구', recent_data['SGG_NM'].unique())
    house_filter = st.multiselect('건물용도', recent_data['HOUSE_GBN_NM'].unique())
    area_filter = st.slider('평수', min_value=0, max_value=max_area_value, value=(0, max_area_value))

    # 필터 적용
    filtered_recent_data = recent_data[(recent_data['SGG_NM'] == sgg_filter) &
                    (recent_data['RENT_GBN'] == rent_filter) &
                    (recent_data['HOUSE_GBN_NM'].isin(house_filter)) &
                    (recent_data['평수'] >= area_filter[0]) &
                    (recent_data['평수'] <= area_filter[1])]

    # 법정동별 평균 계산
    average_data = filtered_recent_data.groupby('BJDONG_NM').agg({'RENT_FEE': 'mean', 'RENT_GTN': 'mean', '평수': 'mean'}).reset_index()

    # 그래프 및 표 생성
    if rent_filter == '월세' and not average_data.empty:
        plot_graph(average_data, x='BJDONG_NM', y1='RENT_GTN', y2='RENT_FEE', secondary_y=True, title='법정동별 시세')
        show_dataframe(average_data[['BJDONG_NM', 'RENT_GTN', 'RENT_FEE', '평수']].rename(columns={'BJDONG_NM': '법정동', 'RENT_GTN': '보증금 평균', 'RENT_FEE': '임대료 평균', '평수': '평수 평균'}))
    elif rent_filter == '전세' and not average_data.empty:
        plot_graph(average_data, x='BJDONG_NM', y1='RENT_GTN', title='법정동별 시세')
        show_dataframe(average_data[['BJDONG_NM', 'RENT_GTN', '평수']].rename(columns={'BJDONG_NM': '법정동', 'RENT_GTN': '보증금 평균', '평수': '평수 평균'}))
    else:
        st.write("최근 1개월 내 계약 내역이 없습니다. 다른 옵션을 선택하세요.")

# 건물별 시세 페이지
def bldg_page(recent_data):
    st.title("건물별 시세")

    # 최대 평수 구해서 정수로 나타내기(반올림)
    max_area_value = math.ceil(recent_data['평수'].max())

    # 필터 설정
    rent_filter = st.selectbox('전·월세', recent_data['RENT_GBN'].unique())
    sgg_filter = st.selectbox('자치구', recent_data['SGG_NM'].unique())
    bjdong_options = recent_data[recent_data['SGG_NM'] == sgg_filter]['BJDONG_NM'].unique()
    bjdong_filter = st.selectbox('법정동', bjdong_options)
    house_filter = st.multiselect('건물용도', recent_data['HOUSE_GBN_NM'].unique())
    area_filter = st.slider('평수', min_value=0, max_value=max_area_value, value=(0, max_area_value))

    # 필터 적용
    filtered_recent_data = recent_data[(recent_data['BJDONG_NM'] == bjdong_filter) &
                    (recent_data['RENT_GBN'] == rent_filter) &
                    (recent_data['HOUSE_GBN_NM'].isin(house_filter)) &
                    (recent_data['평수'] >= area_filter[0]) &
                    (recent_data['평수'] <= area_filter[1])]

    # 건물별 평균 계산
    average_data = filtered_recent_data.groupby('BLDG_NM').agg({'RENT_FEE': 'mean', 'RENT_GTN': 'mean', '평수': 'mean'}).reset_index()

    # 그래프 및 표 생성
    if rent_filter == '월세' and not average_data.empty:
        plot_graph(average_data, x='BLDG_NM', y1='RENT_GTN', y2='RENT_FEE', secondary_y=True, title='건물별 시세')
        show_dataframe(average_data[['BLDG_NM', 'RENT_GTN', 'RENT_FEE', '평수']].rename(columns={'BLDG_NM': '건물명', 'RENT_GTN': '보증금 평균', 'RENT_FEE': '임대료 평균', '평수': '평수 평균'}))
    elif rent_filter == '전세' and not average_data.empty:
        plot_graph(average_data, x='BLDG_NM', y1='RENT_GTN', title='법정동별 시세')
        show_dataframe(average_data[['BLDG_NM', 'RENT_GTN', '평수']].rename(columns={'BLDG_NM': '건물명', 'RENT_GTN': '보증금 평균', '평수': '평수 평균'}))
    else:
        st.write("최근 1개월 내 계약 내역이 없습니다. 다른 옵션을 선택하세요.")

# 최근 1개월 계약 현황 페이지
def onemonth_page(recent_data):
    st.title("건물별 시세")

    # 최대 평수 구해서 정수로 나타내기(반올림)
    max_area_value = math.ceil(recent_data['평수'].max())

    # 계약일 날짜만 나타내기
    recent_data['CNTRCT_DE'] = recent_data['CNTRCT_DE'].dt.date
    
    # 필터 설정
    rent_filter = st.selectbox('전·월세', recent_data['RENT_GBN'].unique())
    sgg_filter = st.selectbox('자치구', recent_data['SGG_NM'].unique())
    bjdong_options = recent_data[recent_data['SGG_NM'] == sgg_filter]['BJDONG_NM'].unique()
    bjdong_filter = st.selectbox('법정동', bjdong_options)
    house_filter = st.multiselect('건물용도', recent_data['HOUSE_GBN_NM'].unique())
    bldg_options = recent_data[(recent_data['RENT_GBN'] == rent_filter) & (recent_data['BJDONG_NM'] == bjdong_filter) & (recent_data['HOUSE_GBN_NM'].isin(house_filter))]['BLDG_NM'].unique()
    bldg_filter = st.multiselect('건물명', bldg_options)
    area_filter = st.slider('평수', min_value=0, max_value=max_area_value, value=(0, max_area_value))

    # 필터 적용
    filtered_recent_data = recent_data[(recent_data['BLDG_NM'].isin(bldg_filter)) &
                    (recent_data['RENT_GBN'] == rent_filter) &
                    (recent_data['HOUSE_GBN_NM'].isin(house_filter)) &
                    (recent_data['평수'] >= area_filter[0]) &
                    (recent_data['평수'] <= area_filter[1])]

    # 표 생성
    if rent_filter == '월세' and not filtered_recent_data.empty:
        st.dataframe(filtered_recent_data[['CNTRCT_DE', 'BLDG_NM', 'RENT_GTN', 'RENT_FEE', '평수']].rename(columns={'CNTRCT_DE': '계약일', 'BLDG_NM': '건물명', 'RENT_GTN': '보증금', 'RENT_FEE': '임대료'}), hide_index=True, use_container_width=True)
    elif rent_filter == '전세' and not filtered_recent_data.empty:
        st.dataframe(filtered_recent_data[['CNTRCT_DE', 'BLDG_NM', 'RENT_GTN', '평수']].rename(columns={'CNTRCT_DE': '계약일', 'BLDG_NM': '건물명', 'RENT_GTN': '보증금'}), hide_index=True, use_container_width=True)
    else:
        st.write("최근 1개월 내 계약 내역이 없습니다. 다른 옵션을 선택하세요.")


# 최근 1년 평균 시세 조회
def yearly_page(recent_data):
    def calculate_monthly_averages(data):
        # 'CNTRCT_DE' 열을 datetime 형식으로 변환
        data['CNTRCT_DE'] = pd.to_datetime(data['CNTRCT_DE'])

        # 월별로 데이터를 나누고 각 월별 보증금과 임대료의 평균을 계산하여 리스트로 반환
        monthly_averages = []
        for month in range(1, 13):
            # 해당 월의 데이터 추출
            monthly_data = data[data['CNTRCT_DE'].dt.month == month]
            # 해당 월의 보증금과 임대료의 평균 계산
            avg_rent_gtn = monthly_data['RENT_GTN'].mean()
            avg_rent_fee = monthly_data['RENT_FEE'].mean()
            avg_rent_area = monthly_data['RENT_AREA'].mean()
            # 결과를 튜플로 추가
            monthly_averages.append((avg_rent_gtn, avg_rent_fee, avg_rent_area))

        return monthly_averages


    st.title("2023년 월별 평균 보증금, 임대료 조회")

    # 데이터 불러오기
    data = load_data()

    # 정수로 된 날짜 열을 날짜로 변환
    data['CNTRCT_DE'] = pd.to_datetime(data['CNTRCT_DE'], format='%Y%m%d')
    # 데이터 중에서 2023년 데이터만 선택
    recent_data = data[(data['CNTRCT_DE'] >= pd.to_datetime('20230101', format='%Y%m%d')) & (data['CNTRCT_DE'] < pd.to_datetime('20240101', format='%Y%m%d'))]

    # 최대 평수 구해서 정수로 나타내기(반올림)
    max_area_value = math.ceil(recent_data['평수'].max())

    # 계약일 날짜만 나타내기
    recent_data['CNTRCT_DE'] = recent_data['CNTRCT_DE'].dt.date
    
    # 필터 설정
    rent_filter = st.selectbox('전·월세', recent_data['RENT_GBN'].unique())
    sgg_filter = st.selectbox('자치구', recent_data['SGG_NM'].unique())
    bjdong_options = recent_data[recent_data['SGG_NM'] == sgg_filter]['BJDONG_NM'].unique()
    bjdong_filter = st.selectbox('법정동', bjdong_options)
    house_filter = st.multiselect('건물용도', recent_data['HOUSE_GBN_NM'].unique())
    bldg_options = recent_data[(recent_data['RENT_GBN'] == rent_filter) & (recent_data['BJDONG_NM'] == bjdong_filter) & (recent_data['HOUSE_GBN_NM'].isin(house_filter))]['BLDG_NM'].unique()
    bldg_filter = st.selectbox('건물명', bldg_options)
    area_filter = st.slider('평수', min_value=0, max_value=max_area_value, value=(0, max_area_value))


    if len(bldg_options) == 0:
        st.write("해당 조건에 맞는 건물이 없습니다.")
        st.stop()

    # 필터 적용
    filtered_recent_data = recent_data[(recent_data['BLDG_NM'] == bldg_filter) &
                    (recent_data['RENT_GBN'] == rent_filter) &
                    (recent_data['HOUSE_GBN_NM'].isin(house_filter)) &
                    (recent_data['평수'] >= area_filter[0]) &
                    (recent_data['평수'] <= area_filter[1])]

    # 월별 평균 계산
    monthly_averages = calculate_monthly_averages(filtered_recent_data)

    # 월별 보증금과 임대료 데이터 프레임 생성
    months = [f"{month}월" for month in range(1, 13)]
    avg_rent_gtn = [avg[0] for avg in monthly_averages]
    avg_rent_fee = [avg[1] for avg in monthly_averages]
    avg_rent_area = [avg[2] for avg in monthly_averages]
    monthly_data = pd.DataFrame({'Month': months, 'Avg_Rent_GTN': avg_rent_gtn, 'Avg_Rent_Fee': avg_rent_fee, 'Avg_Rent_Area': avg_rent_area})

    # 그래프, 표 생성
    if rent_filter == '월세' and not filtered_recent_data.empty:
        # 보증금과 임대료 평균 그래프 시각화
        plot_graph(monthly_data, x='Month', y1='Avg_Rent_GTN', y2='Avg_Rent_Fee', secondary_y=True, title='월별 보증금 및 월 임대료 평균(2023)')
        show_dataframe(monthly_data[['Month', 'Avg_Rent_GTN', 'Avg_Rent_Fee', 'Avg_Rent_Area']].rename(columns={'Month': '월', 'Avg_Rent_GTN': '보증금 평균', 'Avg_Rent_Fee': '월 임대료 평균', 'Avg_Rent_Area': '면적 평균'}))
    elif rent_filter == '전세' and not filtered_recent_data.empty:
        # 보증금과 임대료 평균 그래프 시각화
        plot_graph(monthly_data, x='Month', y1='Avg_Rent_GTN', secondary_y=False, title='월별 전세 보증금 평균(2023)')
        show_dataframe(monthly_data[['Month', 'Avg_Rent_GTN', 'Avg_Rent_Area']].rename(columns={'Month': '월', 'Avg_Rent_GTN': '보증금 평균', 'Avg_Rent_Area': '면적 평균'}))
    else:
        st.write("거래내역이 없습니다. 다른 옵션을 선택하세요.")




# 지원 및 문의 페이지
def support_page():
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    def send_email(name, email, inquiry_type, inquiry_details):
        # 보내는 사람, 받는 사람 이메일 설정
        sender_email = "jgp3620@gmail.com"  # 보내는 사람 이메일 주소
        receiver_emails = ["juyoungeeya@gmail.com", "jgp3620@gmail.com", "wls9416@gmail.com", "rhkrcjswo@gmail.com", "jweon96@gmail.com"]  # 받는 사람 이메일 주소

        # 이메일 제목과 내용 설정
        subject = f"새로운 문의: {inquiry_type} - {name}"
        body = f"""
        이름: {name}
        이메일: {email}
        문의 유형: {inquiry_type}
        문의 내용:
        {inquiry_details}
        """

        # 이메일 메시지 설정
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = ", ".join(receiver_emails)  # 여러 이메일 주소를 쉼표로 구분하여 문자열로 변환
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # SMTP 서버에 연결하여 이메일 보내기
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)  # SMTP 서버 주소와 포트
            server.starttls()  # TLS 암호화 시작
            server.login(sender_email, MAIL_KEY)  # 이메일 계정 로그인
            server.sendmail(sender_email, receiver_emails, message.as_string())  # 이메일 보내기
            st.success("이메일이 성공적으로 전송되었습니다!")
        except Exception as e:
            st.error(f"이메일을 보내는 중 오류가 발생했습니다: {e}")
        finally:
            server.quit()  # SMTP 서버 연결 종료

    st.title("지원 및 문의")

    # 사용자 정보 입력
    name = st.text_input("이름")
    email = st.text_input("이메일 주소")
    inquiry_type = st.selectbox("문의 유형", ["기술 지원", "문의 사항", "기타"])
    inquiry_details = st.text_area("문의 내용", height=200)

    # 문의 제출 버튼
    if st.button("문의 제출"):
        send_email(name, email, inquiry_type, inquiry_details)

def main():
    st.set_page_config(
        page_title="내 집을 찾아서",
        page_icon="🏠",
        # layout="wide",
        # initial_sidebar_state="expanded",
        # menu_items={
        #     'Get Help': 'https://www.extremelycoolapp.com/help',
        #     'Report a bug': "https://www.extremelycoolapp.com/bug",
        #     'About': "# This is a header. This is an *extremely* cool app!"
        # }
    )

    # 데이터 불러오기
    data = load_data()

    # 최근 한 달 데이터만 가져오기
    # 정수로 된 날짜 열을 날짜로 변환
    data['CNTRCT_DE'] = pd.to_datetime(data['CNTRCT_DE'], format='%Y%m%d')
    # 데이터 중에서 가장 최근의 날짜 찾기
    latest_date = data['CNTRCT_DE'].max()
    # 최근 한 달 데이터 선택
    recent_data = data[data['CNTRCT_DE'] >= (latest_date - pd.DateOffset(days=30))]

    # 사이드바 메뉴
    with st.sidebar:
        selected_menu = option_menu("기능 선택", ["메인 페이지", "내가 살 곳 찾기", "집 값 파악하기", "지원 및 문의"],
                            icons=['bi bi-house-fill','bi bi-geo-alt-fill', 'bi bi-currency-dollar', 'bi bi-info-circle'], menu_icon='bi bi-check',
                            styles={"container": {"background-color": "#3081D0", "padding": "0px"},
                                    "nav-link-selected": {"background-color": "#EEEEEE", "color": "#262730"}})

        if selected_menu == "메인 페이지":
            choice = "메인 페이지"
            
        elif selected_menu == "내가 살 곳 찾기":
            choice = option_menu("내가 살 곳 찾기", ["자치구 정하기", "동네 정하기", "건물 정하기"],
                                 icons=['bi bi-1-circle','bi bi-2-circle', 'bi bi-3-circle'], menu_icon='bi bi-house-fill',
                                 styles={"container": {"background-color": "#FC6736"}, "nav-link-selected": {"background-color": "#EEEEEE", "color": "#262730"}})

        elif selected_menu == "집 값 파악하기":
            choice = option_menu("집 값 파악하기", ["최근 1개월 계약 현황", "2023년 실거래가 추이"],
                                 icons=['bi bi-pen-fill','bi-graph-up-arrow'], menu_icon='bi bi-currency-dollar',
                                 styles={"container": {"background-color": "#FC6736"}, "nav-link-selected": {"background-color": "#EEEEEE", "color": "#262730"}})
        
        elif selected_menu == "지원 및 문의":
            choice = "지원 및 문의"

    # 페이지 보이기
    if choice == "메인 페이지":
        main_page()

    elif choice == "자치구 정하기":
        sgg_page(recent_data)
    
    elif choice == "동네 정하기":
        bjdong_page(recent_data)
    
    elif choice == "건물 정하기":
        bldg_page(recent_data)
    
    elif choice == "최근 1개월 계약 현황":
        onemonth_page(recent_data)

    elif choice == "2023년 실거래가 추이":
         yearly_page(recent_data)

    elif choice == "지원 및 문의":
        support_page()
    
if __name__ == '__main__':
    main()