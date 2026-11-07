
import random
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="가위바위보",
    page_icon="✊",
    layout="centered"
)

# 디자인 설정
st.markdown("""
<style>
/* 전체 배경 */
.stApp {
    background-color: #FFFFFF;
    color: #000000;
}

/* 기본 글씨 */
h1, h2, h3, p, label, span, div {
    color: #000000;
}

/* 제목 */
.main-title {
    text-align: center;
    font-size: 45px;
    font-weight: 800;
    color: #000000;
    margin-top: 50px;
    margin-bottom: 15px;
}

/* 설명 */
.sub-title {
    text-align: center;
    font-size: 18px;
    color: #000000;
    margin-bottom: 40px;
}

/* 선택 표시 */
.choice-display {
    text-align: center;
    color: #000000;
    font-size: 22px;
    margin: 25px 0;
}

/* 결과 */
.result-text {
    text-align: center;
    color: #000000;
    font-size: 35px;
    font-weight: bold;
    margin: 30px 0;
}

/* 전적 항목 */
.history-item {
    color: #000000;
    border: 1px solid #CCCCCC;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 10px;
    background-color: #FFFFFF;
}

/* 중앙 정렬 */
.center-text {
    text-align: center;
    color: #000000;
}

/* 모든 버튼 기본 디자인 */
div.stButton > button {
    background-color: #000000 !important;
    color: #FFFFFF !important;
    border: 2px solid #000000 !important;
    border-radius: 10px !important;
    min-height: 50px;
    font-size: 17px;
    font-weight: bold;
}

/* 버튼 내부 글씨 */
div.stButton > button p,
div.stButton > button span,
div.stButton > button div {
    color: #FFFFFF !important;
}

/* 마우스를 올렸을 때 */
div.stButton > button:hover {
    background-color: #000000 !important;
    color: #FFFFFF !important;
    border: 2px solid #000000 !important;
}

/* 클릭 및 포커스 상태 */
div.stButton > button:active,
div.stButton > button:focus {
    background-color: #000000 !important;
    color: #FFFFFF !important;
    border: 2px solid #000000 !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)


# 세션 상태 초기화
if "page" not in st.session_state:
    st.session_state.page = "start"

if "history" not in st.session_state:
    st.session_state.history = []

if "current_game" not in st.session_state:
    st.session_state.current_game = None


# 가위바위보 설정
CHOICES = ["가위", "바위", "보"]

EMOJI = {
    "가위": "✌️",
    "바위": "✊",
    "보": "✋"
}


# 승패 판정
def get_result(user_choice, computer_choice):

    if user_choice == computer_choice:
        return "무승부"

    winning_pairs = {
        ("가위", "보"),
        ("바위", "가위"),
        ("보", "바위")
    }

    if (user_choice, computer_choice) in winning_pairs:
        return "승리"

    return "패배"


# 게임 실행
def play(user_choice):

    computer_choice = random.choice(CHOICES)

    result = get_result(
        user_choice,
        computer_choice
    )

    game = {
        "round": len(st.session_state.history) + 1,
        "user": user_choice,
        "computer": computer_choice,
        "result": result
    }

    st.session_state.current_game = game
    st.session_state.history.append(game)
    st.session_state.page = "result"


# ============================
# 시작 화면
# ============================

if st.session_state.page == "start":

    st.markdown(
        '<div class="main-title">가위바위보</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">가위, 바위, 보 중 하나를 선택하세요.</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✌️ 가위", use_container_width=True):
            play("가위")
            st.rerun()

    with col2:
        if st.button("✊ 바위", use_container_width=True):
            play("바위")
            st.rerun()

    with col3:
        if st.button("✋ 보", use_container_width=True):
            play("보")
            st.rerun()


# ============================
# 결과 화면
# ============================

elif st.session_state.page == "result":

    game = st.session_state.current_game

    st.markdown(
        '<div class="main-title">게임 결과</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="choice-display">
            <b>나</b><br>
            <span style="font-size:65px;">{EMOJI[game["user"]]}</span><br>
            {game["user"]}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="center-text" style="font-size:25px;">VS</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="choice-display">
            <b>컴퓨터</b><br>
            <span style="font-size:65px;">{EMOJI[game["computer"]]}</span><br>
            {game["computer"]}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="result-text">{game["result"]}!</div>',
        unsafe_allow_html=True
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("다시 하기", use_container_width=True):
            st.session_state.page = "start"
            st.rerun()

    with col2:
        if st.button("전적 보기", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()


# ============================
# 전적 화면
# ============================

elif st.session_state.page == "history":

    st.markdown(
        '<div class="main-title">게임 전적</div>',
        unsafe_allow_html=True
    )

    total = len(st.session_state.history)

    wins = sum(
        1 for game in st.session_state.history
        if game["result"] == "승리"
    )

    draws = sum(
        1 for game in st.session_state.history
        if game["result"] == "무승부"
    )

    losses = sum(
        1 for game in st.session_state.history
        if game["result"] == "패배"
    )

    st.markdown(
        f"""
        <div class="center-text"
             style="font-size:18px; margin-bottom:25px;">
            총 {total}전&nbsp;&nbsp;|&nbsp;&nbsp;
            승리 {wins}회&nbsp;&nbsp;|&nbsp;&nbsp;
            무승부 {draws}회&nbsp;&nbsp;|&nbsp;&nbsp;
            패배 {losses}회
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    if not st.session_state.history:

        st.markdown(
            '<p class="center-text">아직 게임 기록이 없습니다.</p>',
            unsafe_allow_html=True
        )

    else:

        for game in reversed(st.session_state.history):

            st.markdown(
                f"""
                <div class="history-item">
                    <b>{game["round"]}번째 게임</b><br>
                    나: {EMOJI[game["user"]]} {game["user"]}
                    &nbsp;&nbsp; VS &nbsp;&nbsp;
                    컴퓨터: {EMOJI[game["computer"]]} {game["computer"]}
                    <br>
                    <b>결과: {game["result"]}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    # 전적창 닫기 버튼
    _, center_col, _ = st.columns([1, 1.5, 1])

    with center_col:

        if st.button("전적창 닫기", use_container_width=True):
            st.session_state.page = "result"
            st.rerun()
