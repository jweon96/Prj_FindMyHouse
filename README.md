# 프로젝트 배경 🏚️
본 프로젝트는 서울 부동산 시장에서 적절한 주택을 찾는 과정을 지원하는 것을 목표로 합니다. 
사용자가 원하는 조건을 입력하면 자치구, 법정동, 또는 건물에 따른 부동산 시세를 그래프 및 도표 형태로 제공합니다. 
이를 통해 사용자는 쉽게 전·월세 실거래 정보를 확인하고, 위치별 시세를 비교하여 집을 구하는 시간을 단축할 수 있습니다.

 ## 팀원 소개 🧑‍🤝‍🧑
- 박지건  : [https://github.com/JG-Park](https://github.com/JG-Park)
- 정주영  : [https://github.com/Ju0s](https://github.com/Ju0s)
- 김진아  : [https://github.com/JinaaK](https://github.com/JinaaK) 
- 원주성  : [https://github.com/jweon96](https://github.com/jweon96)
- 곽정근  : [https://github.com/alpha8108](https://github.com/alpha8108) 
  
## 본 프로젝트에서 사용한 주요 개발환경
  - OS : Windows 10 & Mac (Linux에서는 테스트 하지 않았습니다.)
  - Programming Languages : Python(ver. 3.12.1)
  - Web Framework : Streamlit (ver. 1.31.0)

## 주요 라이브러리 버전
  + [requirements.txt](requirements.txt) 파일 참조

# 데모페이지
- Streamlit에서 구현한 Demo는 다음과 같습니다.
  + [https://apiproject2402.streamlit.app/](https://apiproject2402.streamlit.app/)
 

 # 주요 기능
 - 본 프로젝트에서 자체 개발 및 활용한 주요 메서드는 다음과 같습니다. 

| Functions | Location | Description |
|---|---|---|
| plot_graph | app.py | for creating graphs |
| show_dataframe | app.py | for creating a table display option |
| send_email | app.py | for sending email |

#### plot_graph(data, x, y1, y2=None, secondary_y=False, title='')
-  plot_graph(data, x, y1, y2=None, secondary_y=False, title='') 함수는 임대료와 보증금의 평균 그래프를 생성하는 함수입니다. 보증금 평균은 막대 그래프로 나타내고, 임대료 평균값이 존재하면 선 그래프를 추가로 나타냅니다.
```python
def plot_graph(data, x, y1, y2=None, secondary_y=False, title=''):
    fig = make_subplots(specs=[[{"secondary_y": secondary_y}]])    
    # y1에 대한 막대 그래프 추가
    fig.add_trace(go.Bar(x=data[x], y=data[y1],
                         name='보증금 평균', marker=dict(color=data[y1], colorscale='Blues')), secondary_y=False)    
    # y2가 제공되면 y2에 대한 선 그래 추가
    if y2:    
        fig.add_trace(go.Scatter(x=data[x], y=data[y2], name='임대료 평균', line=dict(color='white')), secondary_y=True)
    # 레이아웃 및 축 제목 업데이트
    fig.update_layout(title=title)
    fig.update_yaxes(title_text='보증금(만 원)', secondary_y=False, tickformat=',.0f')
    if y2:
        fig.update_yaxes(title_text='임대료(만 원)', secondary_y=True, tickformat=',.0f')
    # Streamlit에서 Plotly 차트 표시
    st.plotly_chart(fig, use_container_width=True)
```

#### show_dataframe(dataframe)
- show_dataframe(dataframe) 함수는 표를 보여주는 옵션을 생성하고, 표를 출력하는 함수입니다.
```python
def show_dataframe(dataframe):
    # 사용자가 체크박스를 선택하면 표를 보여줌
    if st.checkbox('표 보이기'):
        # 표를 출력함
        st.dataframe(dataframe, hide_index=True, use_container_width=True)
```

#### send_email(name, email, inquiry_type, inquiry_details)
- send_email(name, email, inquiry_type, inquiry_details) 함수는 Gmail을 이용하여 사용자가 지원 및 문의 내용의 메일을 전송할 수 있도록 하는 함수입니다.
```python
def send_email(name, email, inquiry_type, inquiry_details):
    # 보내는 사람, 받는 사람 이메일 설정
    sender_email = "sender_eamil@gmail.com"  # 보내는 사람 이메일 주소
    receiver_emails = ["receiver_email1@gmail.com", "receiver_email2.com", "receiver_email3@gmail.com"]  # 받는 사람 이메일 주소
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
        server.login(sender_email, "google app password")  # 이메일 계정 로그인
        server.sendmail(sender_email, receiver_emails, message.as_string())  # 이메일 보내기
        st.success("이메일이 성공적으로 전송되었습니다!")
    except Exception as e:
        st.error(f"이메일을 보내는 중 오류가 발생했습니다: {e}")
    finally:
        server.quit()  # SMTP 서버 연결 종료
```

# 발표자료 PDF
- 발표자료 PDF는 아래와 같습니다.
  + [내 집을 찾아서.pdf](portfolio.pdf)

# License
`This project is licensed under the terms of the MIT license.`
- [MIT Licence](LICENSE) 