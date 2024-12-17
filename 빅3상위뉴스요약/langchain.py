import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import ChatMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# 페이지 기본 설정
st.set_page_config(page_title="빅 3 상위뉴스 요약", page_icon="🤖", layout="centered")

# CSS 스타일 적용
st.markdown("""
    <style>
    /* 사용자 말풍선 스타일 */
    .user-bubble {
        background-color: #071C6D;  /* 파란색 말풍선 */
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
        background-color: #FFFFFF;  /* 회색 말풍선 */
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
        background-color: #CFE1EB;
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px;
    }

    /* 전체 페이지 배경 색상 */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #CFE1EB;
    }

    /* 메인 내용 컨테이너 배경 색상 */
    [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: #CFE1EB;
    }

    /* 하단 여백 및 고정 요소 배경 색상 */
    footer {
        background-color: #CFE1EB;
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
        background-color: #CFE1EB;
    }

    </style>
""", unsafe_allow_html=True)



st.markdown("<h1 style='text-align: center;'>📰 빅 3 상위뉴스 요약</h1>", unsafe_allow_html=True)

# 세션 상태에서 대화 내용이 없을 경우 빈 리스트로 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 세션 상태에 저장된 대화 내역을 출력하는 함수
def print_history():
    for msg in st.session_state["messages"]:
        if msg.role == "user":
            st.markdown(f"<div class='user-bubble'>{msg.content}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ai-bubble'>{msg.content}</div>", unsafe_allow_html=True)

# 대화 내역을 세션 상태에 추가하는 함수
def add_history(role, content):
    st.session_state["messages"].append(ChatMessage(role=role, content=content))  # 'user' 또는 'ai' 메시지 구분

# 체인을 생성하는 함수 (프롬프트, 모델 연결)
def create_chain(prompt, model):
    chain = prompt | ChatOpenAI(model_name=model, api_key="my_key") | StrOutputParser()  # OpenAI API와 파싱 체인 생성
    return chain

# 사이드바에 대화 초기화 버튼과 프롬프트 설정 인터페이스를 추가
with st.sidebar:
    st.markdown("<h2 style='color: #1e272e;'>Settings</h2>", unsafe_allow_html=True)
    clear_btn = st.button("대화내용 초기화")

    # 프롬프트 설정 UI
    prompt = """당신은 친절한 AI 어시스턴트 입니다. 사용자의 질문에 간결하게 답변해 주세요."""
    user_text_prompt = st.text_area("프롬프트", value=prompt)
    user_text_apply_btn = st.button("프롬프트 적용", key="apply1")

    # 프롬프트 적용 로직
    if user_text_apply_btn:
        st.markdown("<div style='color: green;'>✅ 프롬프트가 적용되었습니다</div>", unsafe_allow_html=True)
        prompt_template = user_text_prompt + "\n\n#Question:\n{question}\n\n#Answer:"
        prompt = PromptTemplate.from_template(prompt_template)
        st.session_state["chain"] = create_chain(prompt, "gpt-3.5-turbo")  # 수정된 프롬프트는 PromptTemplate을 통해 템플릿화되고, AI 모델과의 체인이 새로 생성

# 대화내용 초기화 버튼이 눌리면 세션 상태의 대화 내용 초기화
if clear_btn:
    st.session_state["messages"].clear()

# 이전 대화 내역 출력
print_history()

# 세션 상태에 체인이 없다면 기본 체인을 생성
if "chain" not in st.session_state:
    prompt_template = user_text_prompt + "\n\n#Question:\n{question}\n\n#Answer:"  # 기본 프롬프트 템플릿
    prompt = PromptTemplate.from_template(prompt_template)  # 템플릿 생성
    st.session_state["chain"] = create_chain(prompt, "gpt-3.5-turbo")  # 체인 생성 후 세션에 저장

# 사용자가 입력창에 질문을 입력했을 때
if user_input := st.chat_input("Type your question here..."):
    add_history("user", user_input)  # 입력된 질문을 세션 상태에 저장
    st.markdown(f"<div class='user-bubble'>{user_input}</div>", unsafe_allow_html=True)  # 사용자 메시지 출력

    # AI의 답변 처리
    with st.chat_message("assistant"):
        chat_container = st.empty()  # 응답을 실시간으로 표시할 공간 생성

        # AI 모델의 스트리밍 응답 처리
        stream_response = st.session_state["chain"].stream({"question": user_input})  # 질문에 대한 답변 스트리밍
        ai_answer = ""

        # 스트리밍된 AI 응답을 차례로 화면에 출력
        for chunk in stream_response:
            ai_answer += chunk  # 스트리밍된 답변을 하나의 문자열로 결합
            chat_container.markdown(f"<div class='ai-bubble'>{ai_answer}</div>", unsafe_allow_html=True)  # 실시간으로 화면에 표시

        # AI 응답을 세션 상태에 저장
        add_history("ai", ai_answer)
