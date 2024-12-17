import streamlit as st
import folium
from streamlit_folium import st_folium
from langchain_core.output_parsers import StrOutputParser  # AI의 출력 결과를 문자열로 파싱
from langchain_core.messages import ChatMessage            # 사용자와 AI 간의 메시지를 관리
from langchain_core.prompts import PromptTemplate          # AI가 사용할 프롬프트(명령어)를 템플릿으로 정의
from langchain_openai import ChatOpenAI                    # OpenAI 모델을 사용해 AI 대화를 수행
import googlemaps                                          # Google Maps API 사용
import time
from time import sleep
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

# Streamlit 페이지의 제목과 아이콘을 설정
st.set_page_config(page_title="국내 여행지 추천", page_icon="🚄", layout="centered")

# CSS 스타일 적용
st.markdown("""
    <style>
    /* 사용자 말풍선 스타일 */
    .user-bubble {
        background-color: #CF66B2;  /* 파란색 말풍선 */
        color: white;
        padding: 10px;
        border-radius: 20px;
        margin: 10px;
        width: fit-content; /* 텍스트 크기에 맞게 말풍선 너비 조정 */
        margin-left: auto;  /* 오른쪽 정렬 */
        text-align: right;
    }
    /* AI 말풍선 스타일 */
    .ai-bubble {
        background-color: #EFEFEF;  /* 회색 말풍선 */
        color: black;
        padding: 10px;
        border-radius: 20px;
        margin: 10px;
        width: fit-content; /* 텍스트 크기에 맞게 말풍선 너비 조정 */
        margin-right: auto;  /* 왼쪽 정렬 */
    }
    /* 입력 박스 스타일 */
    .input-box {
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: #FFFFFF;
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px;
    }

    /* 전체 페이지 배경 색상 */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF;
    }

    /* 메인 내용 컨테이너 배경 색상 */
    [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: #FFFFFF;
    }

    /* 하단 여백 및 고정 요소 배경 색상 */
    footer {
        background-color: #FFFFFF;
        position: fixed;
        bottom: 0;
        width: 100%;
        height: 50px;
    }

    /* 하단 푸터의 텍스트 숨김 (필요시) */
    footer:after {
        content: '';
        display: block;
        position: fixed;
        bottom: 0;
        width: 100%;
        height: 30px;
        background-color: #FFFFFF;
    }

}
    
""", unsafe_allow_html=True)


st.markdown("<h1 style='text-align: center;'>국내 여행지 추천 🚄</h1>", unsafe_allow_html=True)

# Google Maps API 설정
gmaps = googlemaps.Client(key="my key")  # 여기에 Google Maps API 키를 입력하세요

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []  # 사용자와 AI 간의 대화 내용을 저장하는 리스트

# 메시지 출력 및 추가 함수
def print_history():
    for msg in st.session_state["messages"]:
       st.chat_message(msg.role).write(msg.content)


def add_history(role, content):
    st.session_state["messages"].append(ChatMessage(role=role, content=content))

# 체인 생성
def create_chain(prompt, model):
    chain = prompt | ChatOpenAI(model_name=model, api_key="my_key") | StrOutputParser()
    return chain

# 지오코딩 함수: Google Maps Geocoding API를 사용해 관광지 이름을 좌표로 변환
def geocode_location(place_name):
    try:
        geo_location = gmaps.geocode(place_name)[0].get('geometry')
        lat = geo_location['location']['lat']
        lng =  geo_location['location']['lng']
        return [lat, lng]
    except:
        return (None, None)

# 사이드바 설정
with st.sidebar:
    st.markdown("<h2 style='color: #1e272e;'>Settings</h2>", unsafe_allow_html=True)
    clear_btn = st.button("대화내용 초기화")
    
    # 프롬프트 설정 UI
    prompt = """당신은 국내 여행지 추천 AI 어시스턴트 입니다. 사용자의 질문에 자세하게 답변해 주세요."""
    user_text_prompt = st.text_area("프롬프트", value=prompt)
    user_text_apply_btn = st.button("프롬프트 적용", key="apply1")
    
    # 프롬프트 적용 로직
    if user_text_apply_btn:
        st.markdown("<div style='color: green;'>✅ 프롬프트가 적용되었습니다</div>", unsafe_allow_html=True)
        prompt_template = user_text_prompt + "\n\n#Question:\n{question}\n\n#Answer:"
        prompt = PromptTemplate.from_template(prompt_template)
        st.session_state["chain"] = create_chain(prompt, "gpt-3.5-turbo")  # 수정된 프롬프트로 새로운 체인 생성

# 대화 내용 초기화
if clear_btn:
    st.session_state["messages"].clear()

# 대화 내역 출력
print_history()

# 초기 체인 영역 
if "chain" not in st.session_state:
    # 초기 프롬프트 템플릿 설정
    prompt_template = """당신은 국내 여행지 추천 AI 어시스턴트 입니다. 사용자의 질문에 자세하게 답변해 주세요.\n\n#Question:\n{question}\n\n#Answer:"""
    prompt = PromptTemplate.from_template(prompt_template)
    st.session_state["chain"] = create_chain(prompt, "gpt-3.5-turbo")

# 사용자 입력 처리 및 AI 응답 처리
if user_input := st.chat_input():
    add_history("user", user_input)  # 사용자의 입력을 메시지에 추가
    st.markdown(f"<div class='user-bubble'>{user_input}</div>", unsafe_allow_html=True)  # 사용자 메시지 출력
    
    # AI 응답 처리
    with st.chat_message("assistant"):
        chat_container = st.empty()

        # AI 응답을 실시간으로 스트리밍
        stream_response = st.session_state["chain"].stream({"question": user_input})
        ai_answer = ""

        # 스트리밍된 AI 응답을 차례로 화면에 출력
        for chunk in stream_response:
            ai_answer += chunk  # 스트리밍된 답변을 하나의 문자열로 결합
            chat_container.markdown(f"<div class='ai-bubble'>{ai_answer}</div>", unsafe_allow_html=True)  # 실시간으로 화면에 표시

        # AI 응답을 기록
        add_history("ai", ai_answer)

        # 관광지 이름을 쉼표로 구분해 추출
        spots = [spot.strip() for spot in ai_answer.split("-")]

        # 좌표 리스트를 담을 배열
        locations = []
        for spot in spots:
            lat, lon = geocode_location(spot)  # 지오코딩으로 좌표 가져오기
            if lat and lon:
                locations.append((lat, lon))
                sleep(1)  # API 호출 제한을 피하기 위해 잠시 대기
                
        # 관광지의 중심 좌표 계산 (평균) - 지도 생성 초기값을 위해 
        if locations:
            center_lat = sum(lat for lat, lon in locations) / len(locations)
            center_lon = sum(lon for lat, lon in locations) / len(locations)
        else:
            # 기본 서울 중심 좌표로 설정
            center_lat, center_lon = 37.5665, 126.9780

        # 지도 생성
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
        marker_cluster = MarkerCluster().add_to(m)

       # 각 추천 관광지에 대한 마커 추가
        for place, (lat, lon) in zip(spots, locations):
            folium.Marker(
                location=[lat, lon],
            ).add_to(marker_cluster)

        # Folium 지도를 Streamlit에 표시
        if spots:
            # 지도 크기를 조정하여 더 잘 보이게 만들 수 있음 (width, height 조정)
            folium_static(m, width=700, height=500)
        else:
            chat_container.markdown("추천된 관광지를 지도에 표시할 수 없습니다.")


