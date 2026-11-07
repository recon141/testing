
import random
import time
from datetime import datetime

import streamlit as st


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------

st.set_page_config(
    page_title="모의 해킹 시뮬레이터",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .stApp {
        background: #ffffff;
        color: #111111;
    }

    [data-testid="stHeader"] {
        background: #ffffff;
    }

    h1, h2, h3, p, label, span, div {
        color: #111111;
    }

    .stButton > button {
        background: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #111111 !important;
        border-radius: 3px !important;
        min-height: 2.35rem;
        font-weight: 600;
    }

    .stButton > button:hover {
        background: #333333 !important;
        color: #ffffff !important;
    }

    .stButton > button:disabled {
        background: #777777 !important;
        color: #ffffff !important;
    }

    .panel {
        border: 1px solid #cccccc;
        padding: 12px;
        border-radius: 3px;
        background: #ffffff;
    }

    .muted {
        color: #555555;
        font-size: 0.9rem;
    }

    .danger {
        color: #c62828 !important;
        font-weight: 700;
    }

    .success {
        color: #16803c !important;
        font-weight: 700;
    }

    .blue {
        color: #1565c0 !important;
        font-weight: 700;
    }

    .logline {
        border-bottom: 1px solid #eeeeee;
        padding: 5px 0;
        font-family: monospace;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 공격 종류 및 대응 기능
# --------------------------------------------------

ATTACKS = {
    "DDoS": {
        "desc": "다수의 출발지에서 대량의 트래픽을 보내 서비스 이용을 방해하는 공격",
        "clues": [
            "비정상적으로 높은 네트워크 트래픽",
            "여러 출발지 IP에서 동시에 요청 증가",
            "RPS 급증",
        ],
        "defenses": ["CDN", "DDoS 방어 서비스", "WAF"],
        "hint": "다수의 출발지에서 요청이 동시에 증가하고 있습니다.",
        "log_type": "네트워크 트래픽",
    },
    "HTTP Flood": {
        "desc": "HTTP 요청을 과도하게 발생시켜 웹 서버나 API에 부담을 주는 공격",
        "clues": [
            "특정 API의 요청 수 급증",
            "특정 경로의 RPS 증가",
            "정상 사용자 대비 요청 빈도 이상",
        ],
        "defenses": ["API별 Rate Limit", "WAF"],
        "hint": "특정 웹 경로에 요청이 집중되고 있습니다.",
        "log_type": "네트워크 트래픽",
    },
    "Resource Exhaustion": {
        "desc": "서버의 CPU, 메모리, 연결 등의 자원을 소진시키려는 공격",
        "clues": [
            "CPU 또는 메모리 사용량 급증",
            "데이터베이스 연결 수 증가",
            "응답 지연",
        ],
        "defenses": [
            "CPU 및 메모리 사용량 제한",
            "Timeout 설정",
            "Connection Limit",
        ],
        "hint": "서버 자원 사용량이 평소보다 빠르게 증가하고 있습니다.",
        "log_type": "서버 자원",
    },
    "Slowloris": {
        "desc": "연결을 오래 유지해 서버의 동시 연결 자원을 점유하는 공격",
        "clues": [
            "연결이 장시간 종료되지 않음",
            "동시 연결 수 증가",
            "요청 완료 지연",
        ],
        "defenses": ["Connection Limit", "Timeout 설정"],
        "hint": "완료되지 않은 연결이 비정상적으로 오래 유지되고 있습니다.",
        "log_type": "네트워크 트래픽",
    },
    "Brute Force": {
        "desc": "하나의 계정에 여러 비밀번호를 반복적으로 시도하는 공격",
        "clues": [
            "특정 계정의 로그인 실패 반복",
            "특정 IP의 인증 요청 증가",
        ],
        "defenses": [
            "IP별 Rate Limit",
            "계정별 Rate Limit",
            "다중 인증(MFA)",
        ],
        "hint": "특정 계정에 대한 로그인 실패가 반복되고 있습니다.",
        "log_type": "인증 기록",
    },
    "Credential Stuffing": {
        "desc": "다른 서비스에서 유출된 계정 정보를 이용해 로그인을 시도하는 공격",
        "clues": [
            "여러 계정에서 로그인 시도",
            "비정상적인 위치나 기기에서 인증",
            "로그인 성공과 실패가 혼재",
        ],
        "defenses": ["다중 인증(MFA)"],
        "hint": "서로 다른 계정에서 평소와 다른 인증 시도가 관찰됩니다.",
        "log_type": "인증 기록",
    },
    "Password Spraying": {
        "desc": "여러 계정에 소수의 비밀번호를 분산해 시도하는 공격",
        "clues": [
            "다수 계정에서 유사한 시간대 로그인 실패",
            "전체 로그인 실패 수 증가",
        ],
        "defenses": [
            "SIEM",
            "다중 인증(MFA)",
            "IP별 Rate Limit",
            "계정별 Rate Limit",
        ],
        "hint": "여러 계정에서 비슷한 시간대에 인증 실패가 발생하고 있습니다.",
        "log_type": "인증 기록",
    },
    "Session Hijacking": {
        "desc": "유효한 사용자의 세션 정보를 탈취하거나 악용하는 공격",
        "clues": [
            "동일 세션의 비정상적인 접속 환경 변화",
            "평소와 다른 IP에서 세션 사용",
            "세션 재사용 징후",
        ],
        "defenses": ["세션 관리"],
        "hint": "이미 인증된 세션이 평소와 다른 환경에서 사용되고 있습니다.",
        "log_type": "세션 정보",
    },
    "SQL Injection": {
        "desc": "입력값을 통해 데이터베이스 질의 구조에 영향을 주려는 공격",
        "clues": [
            "입력값 검증 경고",
            "비정상적인 데이터베이스 질의 패턴",
            "예상하지 못한 DB 오류",
        ],
        "defenses": ["Prepared Statement", "WAF"],
        "hint": "일부 요청에서 데이터베이스 질의와 관련된 이상 징후가 나타납니다.",
        "log_type": "데이터베이스 접근 기록",
    },
    "Data Exfiltration": {
        "desc": "서버 내부의 데이터를 허가되지 않은 외부 위치로 반출하는 공격",
        "clues": [
            "외부 데이터 전송량 급증",
            "평소와 다른 목적지로 데이터 전송",
            "대량의 데이터 조회",
        ],
        "defenses": ["DLP", "데이터베이스 접근 권한 관리"],
        "hint": "외부 데이터 전송량과 데이터 조회량이 증가하고 있습니다.",
        "log_type": "외부 데이터 전송",
    },
    "데이터 파괴 및 랜섬웨어": {
        "desc": "데이터를 훼손하거나 사용할 수 없게 만들려는 공격",
        "clues": [
            "파일 변경 이벤트 급증",
            "중요 데이터의 비정상적인 수정",
            "보안 프로그램의 이상 경고",
        ],
        "defenses": ["EDR", "백업 및 복구 설정"],
        "hint": "중요 데이터에 대한 비정상적인 변경 이벤트가 관찰됩니다.",
        "log_type": "백업 시스템 상태",
    },
    "백업 및 복구 시스템 공격": {
        "desc": "백업 데이터나 복구 체계를 무력화하려는 공격",
        "clues": [
            "백업 설정 변경 시도",
            "백업 저장소 접근 권한 변경",
            "백업 작업 실패",
        ],
        "defenses": [
            "백업 및 복구 설정",
            "데이터베이스 접근 권한 관리",
            "다중 인증(MFA)",
        ],
        "hint": "백업 시스템의 설정 또는 접근 권한에 변화가 감지됩니다.",
        "log_type": "백업 시스템 상태",
    },
}


TOP_CONTROLS = [
    "IP별 Rate Limit",
    "계정별 Rate Limit",
    "API별 Rate Limit",
    "다중 인증(MFA)",
    "Connection Limit",
    "Timeout 설정",
    "Prepared Statement",
    "데이터베이스 접근 권한 관리",
    "세션 관리",
    "CPU 및 메모리 사용량 제한",
    "백업 및 복구 설정",
    "로그 분석",
]

BOTTOM_CONTROLS = [
    "CDN",
    "WAF",
    "DDoS 방어 서비스",
    "로드 밸런서",
    "DLP",
    "EDR",
    "IDS",
    "IPS",
    "SIEM",
]


INFO_KEYS = {
    "네트워크 트래픽": "traffic",
    "출발지 IP 주소": "src",
    "목적지 IP 주소": "dst",
    "초당 요청 수(RPS)": "rps",
    "서버 CPU 및 메모리 사용량": "resources",
    "데이터베이스 연결 수": "db",
    "로그인 성공 및 실패 기록": "auth",
    "데이터베이스 접근 기록": "database",
    "외부 데이터 전송량": "egress",
    "세션 정보": "session",
    "백업 시스템 상태": "backup",
}


# --------------------------------------------------
# 공격별 방어 판정
# --------------------------------------------------
# 각 공격의 defenses 목록 중 하나라도 활성화되면 방어 성공.
# 단, 백업 시스템 공격은 백업 설정과 MFA가 모두 필요하도록 설정.

DEFENSE_RULES = {
    "DDoS": [
        {"CDN"},
        {"DDoS 방어 서비스"},
        {"WAF"},
    ],
    "HTTP Flood": [
        {"API별 Rate Limit"},
        {"WAF"},
    ],
    "Resource Exhaustion": [
        {"CPU 및 메모리 사용량 제한"},
        {"Timeout 설정"},
        {"Connection Limit"},
    ],
    "Slowloris": [
        {"Connection Limit"},
        {"Timeout 설정"},
    ],
    "Brute Force": [
        {"IP별 Rate Limit"},
        {"계정별 Rate Limit"},
        {"다중 인증(MFA)"},
    ],
    "Credential Stuffing": [
        {"다중 인증(MFA)"},
    ],
    "Password Spraying": [
        {"SIEM"},
        {"다중 인증(MFA)"},
        {"IP별 Rate Limit"},
        {"계정별 Rate Limit"},
    ],
    "Session Hijacking": [
        {"세션 관리"},
    ],
    "SQL Injection": [
        {"Prepared Statement"},
        {"WAF"},
    ],
    "Data Exfiltration": [
        {"DLP"},
        {"데이터베이스 접근 권한 관리"},
    ],
    "데이터 파괴 및 랜섬웨어": [
        {"EDR"},
        {"백업 및 복구 설정"},
    ],
    "백업 및 복구 시스템 공격": [
        {"백업 및 복구 설정", "다중 인증(MFA)"},
        {"백업 및 복구 설정", "데이터베이스 접근 권한 관리"},
    ],
}


# --------------------------------------------------
# 세션 상태 초기화
# --------------------------------------------------

def init_state():
    defaults = {
        "page": "home",
        "active": False,
        "started_at": None,
        "last_event_at": None,
        "next_event_in": 0,
        "current_event": None,
        "event_started": None,
        "event_stage": 0,
        "enabled_controls": set(),
        "history": [],
        "event_counter": 0,
        "opened_info": None,
        "result": None,
        "logs": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


def add_log(message, level="INFO"):
    stamp = datetime.now().strftime("%H:%M:%S")
    line = f"{stamp} [{level}] {message}"

    st.session_state.logs.insert(0, line)
    st.session_state.logs = st.session_state.logs[:80]


def reset_sim():
    st.session_state.active = False
    st.session_state.started_at = None
    st.session_state.last_event_at = None
    st.session_state.next_event_in = 0
    st.session_state.current_event = None
    st.session_state.event_started = None
    st.session_state.event_stage = 0
    st.session_state.enabled_controls = set()
    st.session_state.history = []
    st.session_state.event_counter = 0
    st.session_state.opened_info = None
    st.session_state.result = None
    st.session_state.logs = []
    st.session_state.page = "home"
    st.rerun()


def start_sim():
    st.session_state.active = True
    st.session_state.page = "sim"
    st.session_state.started_at = time.time()
    st.session_state.last_event_at = time.time()
    st.session_state.next_event_in = random.randint(30, 60)

    st.session_state.current_event = None
    st.session_state.event_started = None
    st.session_state.event_stage = 0
    st.session_state.enabled_controls = set()
    st.session_state.history = []
    st.session_state.event_counter = 0
    st.session_state.opened_info = None
    st.session_state.result = None
    st.session_state.logs = []

    add_log("시뮬레이션이 시작되었습니다.")


# --------------------------------------------------
# 방어 판정 및 이벤트 처리
# --------------------------------------------------

def get_defense(attack_name):
    enabled = st.session_state.enabled_controls

    for rule in DEFENSE_RULES[attack_name]:
        if rule.issubset(enabled):
            return True, sorted(rule)

    return False, []


def record_event(attack_name, blocked, used_controls):
    st.session_state.history.append({
        "attack": attack_name,
        "blocked": blocked,
        "controls": used_controls,
        "time": datetime.now().strftime("%H:%M:%S"),
    })


def finish_success():
    st.session_state.result = "success"
    st.session_state.active = False
    st.session_state.current_event = None
    add_log("모든 공격 유형에 대한 방어 조건을 충족했습니다.", "SUCCESS")


def generate_event():
    candidates = [
        name for name in ATTACKS
        if not get_defense(name)[0]
    ]

    if not candidates:
        finish_success()
        return

    attack = random.choice(candidates)

    st.session_state.event_counter += 1
    st.session_state.current_event = attack
    st.session_state.event_started = time.time()
    st.session_state.event_stage = 0
    st.session_state.opened_info = None

    add_log("비정상적인 이벤트가 관찰되었습니다.", "WARN")

    # 이미 적용된 방어 기능으로 막을 수 있는 공격은
    # 후보에서 제외되므로 사용자가 대응할 기회를 갖게 됨.


def resolve_event():
    attack = st.session_state.current_event

    if not attack:
        return

    blocked, controls = get_defense(attack)

    if blocked:
        record_event(attack, True, controls)
        add_log(
            f"{attack} 공격 시도를 방어했습니다. 사용 기능: {', '.join(controls)}",
            "DEFENDED",
        )

        st.session_state.current_event = None
        st.session_state.event_started = None
        st.session_state.event_stage = 0
        st.session_state.last_event_at = time.time()
        st.session_state.next_event_in = random.randint(30, 60)

    else:
        record_event(attack, False, [])
        add_log(f"{attack} 공격 대응에 실패했습니다.", "CRITICAL")

        st.session_state.result = "failure"
        st.session_state.active = False


def tick():
    if not st.session_state.active:
        return

    now = time.time()

    if st.session_state.current_event is None:
        # 모든 공격을 방어할 수 있다면 성공 처리
        if all(get_defense(name)[0] for name in ATTACKS):
            finish_success()
            return

        elapsed = now - st.session_state.last_event_at

        if elapsed >= st.session_state.next_event_in:
            generate_event()

    else:
        attack = st.session_state.current_event
        elapsed = now - st.session_state.event_started

        # 방어 기능이 활성화되었는지 매초 확인
        blocked, controls = get_defense(attack)

        if blocked:
            resolve_event()
            return

        stage = (
            0 if elapsed < 15 else
            1 if elapsed < 25 else
            2 if elapsed < 30 else
            3
        )

        if stage > st.session_state.event_stage:
            st.session_state.event_stage = stage

            if stage == 1:
                add_log("시스템이 비정상적인 활동을 감지했습니다.", "WARN")

            elif stage == 2:
                add_log("이상 징후 분석 힌트가 활성화되었습니다.", "WARN")

            elif stage == 3:
                add_log(
                    f"공격 유형 추정: {attack}",
                    "WARN",
                )

        if elapsed >= 60:
            resolve_event()


# --------------------------------------------------
# 공통 화면
# --------------------------------------------------

def show_header():
    st.markdown("# 모의 해킹 시뮬레이터")
    st.markdown(
        "<div class='muted'>가상의 서버 환경에서 보안 이벤트를 탐지하고 대응하는 교육용 시뮬레이션</div>",
        unsafe_allow_html=True,
    )
    st.divider()


def go_home():
    st.session_state.page = "home"
    st.rerun()


# --------------------------------------------------
# 시작 화면
# --------------------------------------------------

def home():
    show_header()

    st.write("")
    st.write("")

    st.markdown(
        "<h2 style='text-align:center'>모의 해킹 시뮬레이션</h2>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p style='text-align:center;color:#555'>가상 서버의 이상 징후를 분석하고 적절한 방어 기능을 적용하십시오.</p>",
        unsafe_allow_html=True,
    )

    st.write("")

    _, center, _ = st.columns([1, 1.2, 1])

    with center:
        if st.button("시작하기", use_container_width=True):
            start_sim()
            st.rerun()

        if st.button("해킹 종류", use_container_width=True):
            st.session_state.page = "attacks"
            st.rerun()

        if st.button("인터페이스 설명", use_container_width=True):
            st.session_state.page = "guide"
            st.rerun()

    st.write("")

    st.caption(
        "본 앱은 실제 네트워크에 접속하거나 공격을 수행하지 않는 가상 교육용 시뮬레이터입니다."
    )


# --------------------------------------------------
# 해킹 종류 설명 화면
# --------------------------------------------------

def attacks_page():
    show_header()
    st.subheader("해킹 종류 및 대응 방법")

    for name, item in ATTACKS.items():
        with st.expander(name):
            st.write(item["desc"])

            st.markdown("**주요 탐지 징후**")

            for clue in item["clues"]:
                st.write(f"- {clue}")

            st.markdown("**주요 대응 기능**")
            st.write(", ".join(item["defenses"]))

    if st.button("닫기"):
        go_home()


# --------------------------------------------------
# 인터페이스 설명 화면
# --------------------------------------------------

def guide_page():
    show_header()
    st.subheader("인터페이스 설명")

    st.markdown("""
**상단 기능 영역 — 서버 내부 설정**

- IP·계정·API별 요청 제한, MFA, 연결 수와 Timeout 관리
- Prepared Statement, 데이터베이스 접근 권한, 세션 관리
- 서버 자원 제한, 백업 설정, 로그 분석

**중앙 정보 영역 — 서버 상태와 관찰 기록**

- 네트워크 트래픽, IP 주소, RPS, CPU·메모리, DB 연결 수
- 로그인 기록, 데이터베이스 접근 기록, 외부 전송량, 세션 및 백업 상태
- 정보 버튼을 눌러 세부 기록을 열고 닫을 수 있음

**하단 기능 영역 — 외부 보안 서비스**

- CDN, WAF, DDoS 방어 서비스, 로드 밸런서
- DLP, EDR, IDS, IPS, SIEM

**시뮬레이션 진행**

- 공격 발생 후 최초 15초 동안 별도 경고 없이 관찰 가능
- 15초 이후 감지 알림
- 25초 이후 관련 정보 버튼 강조
- 30초 이후 공격 유형 공개
- 공격 이벤트마다 60초 안에 대응해야 함
""")

    if st.button("닫기"):
        go_home()


# --------------------------------------------------
# 서버 정보 창
# --------------------------------------------------

def info_content(label, attack=None):
    is_attack = attack is not None

    if label == "네트워크 트래픽":
        return [
            f"현재 네트워크 트래픽: {random.randint(450, 1800) if is_attack else random.randint(80, 260)} Mbps",
            f"최근 1분 평균: {random.randint(90, 180)} Mbps",
            "상태: 비정상 패턴 분석 중" if is_attack else "상태: 정상 범위",
        ]

    if label == "출발지 IP 주소":
        return [
            f"관찰된 출발지: 203.0.113.{random.randint(10, 220)}",
            "추가 출발지: 198.51.100.24",
            "참고: 문서용 예약 IP 대역 사용",
        ]

    if label == "목적지 IP 주소":
        return [
            "목적지 서버: 192.0.2.10",
            "서비스 포트: HTTPS (443)",
            "참고: 가상 서버 주소",
        ]

    if label == "초당 요청 수(RPS)":
        return [
            f"현재 RPS: {random.randint(900, 3200) if is_attack else random.randint(45, 120)}",
            "기준 RPS: 80",
            "단위: requests/second",
        ]

    if label == "서버 CPU 및 메모리 사용량":
        return [
            f"CPU 사용량: {random.randint(75, 99) if is_attack else random.randint(15, 55)}%",
            f"메모리 사용량: {random.randint(70, 96) if is_attack else random.randint(30, 60)}%",
            "상태: 가상 측정값",
        ]

    if label == "데이터베이스 연결 수":
        return [
            f"활성 연결: {random.randint(80, 180) if is_attack else random.randint(8, 30)}",
            "최대 연결: 200",
            "대기 연결: 4",
        ]

    if label == "로그인 성공 및 실패 기록":
        auth_attack = attack in [
            "Brute Force",
            "Credential Stuffing",
            "Password Spraying",
        ]

        return [
            f"최근 로그인 성공: {random.randint(2, 12)}건",
            f"최근 로그인 실패: {random.randint(25, 90) if auth_attack else random.randint(0, 5)}건",
            "계정명은 가상 ID로 표시",
        ]

    if label == "데이터베이스 접근 기록":
        return [
            f"{datetime.now().strftime('%H:%M:%S')} SELECT 요청 — app_user",
            "접근 대상: customer_records (가상 테이블)",
            "상태: 질의 패턴 점검",
        ]

    if label == "외부 데이터 전송량":
        amount = (
            random.randint(500, 2200)
            if attack == "Data Exfiltration"
            else random.randint(20, 180)
        )

        return [
            f"최근 1분 전송량: {amount} MB",
            "외부 목적지: 198.51.100.24",
            "상태: 전송량 기준 분석",
        ]

    if label == "세션 정보":
        return [
            "활성 세션: 128",
            "세션 ID: SESSION-****-A31F",
            "상태: 가상 세션 정보",
        ]

    if label == "백업 시스템 상태":
        abnormal = attack in [
            "데이터 파괴 및 랜섬웨어",
            "백업 및 복구 시스템 공격",
        ]

        return [
            "최근 백업: 02:00 완료",
            "백업 무결성 점검 필요" if abnormal else "백업 무결성: 정상",
            "백업 저장소: 격리된 가상 저장소",
        ]

    return ["표시할 정보가 없습니다."]


# --------------------------------------------------
# 시뮬레이션 화면
# --------------------------------------------------

@st.fragment(run_every="1s")
def sim_page():
    tick()

    if st.session_state.result:
        result_page()
        return

    show_header()

    elapsed_total = int(time.time() - st.session_state.started_at)
    event = st.session_state.current_event

    event_elapsed = 0

    if event and st.session_state.event_started:
        event_elapsed = int(time.time() - st.session_state.event_started)

    top_left, top_right = st.columns([3, 1])

    with top_left:
        st.subheader("서버 모니터링")
        st.caption(
            "가상 서버 ID: SIM-SRV-01  |  상태: 운영 중  |  시간: "
            + datetime.now().strftime("%H:%M:%S")
        )

    with top_right:
        st.metric(
            "진행 시간",
            f"{elapsed_total // 60:02d}:{elapsed_total % 60:02d}",
        )

    # 공격 진행 상태 표시
    if event:
        if event_elapsed < 15:
            st.info(
                "관찰 단계: 별도 경고 없이 서버 정보를 확인하여 이상 징후를 탐지하십시오."
            )

        elif event_elapsed < 25:
            st.warning("시스템 감지: 비정상적인 활동이 감지되었습니다.")

        elif event_elapsed < 30:
            st.error(
                "분석 힌트가 활성화되었습니다. 관련 정보 버튼을 확인하십시오."
            )

        else:
            st.error(f"공격 유형 추정: {event}")

        remaining = max(0, 60 - event_elapsed)

        st.progress(
            remaining / 60,
            text=f"현재 이벤트 대응 시간: {remaining}초",
        )

    else:
        until = max(
            0,
            st.session_state.next_event_in
            - int(time.time() - st.session_state.last_event_at),
        )

        st.info(
            f"현재 진행 중인 공격 이벤트가 없습니다. 다음 이벤트까지 약 {until}초"
        )

    # 서버 정보 버튼
    st.markdown("**서버 정보 열기**")

    info_cols = st.columns(6)
    info_labels = list(INFO_KEYS.keys())

    for i, label in enumerate(info_labels):
        with info_cols[i % 6]:
            is_open = st.session_state.opened_info == label

            is_hint = bool(
                event
                and event_elapsed >= 25
                and label == ATTACKS[event]["log_type"]
            )

            button_label = label

            if is_open:
                button_label = "[열림] " + button_label

            if is_hint:
                button_label = "[힌트] " + button_label

            if st.button(
                button_label,
                key=f"info_{label}",
                use_container_width=True,
            ):
                st.session_state.opened_info = (
                    None if is_open else label
                )
                st.rerun()

    # 정보 창 표시
    if st.session_state.opened_info:
        label = st.session_state.opened_info

        st.markdown(
            f"<div class='panel'><b>{label}</b></div>",
            unsafe_allow_html=True,
        )

        visible_attack = (
            event
            if event and event_elapsed >= 25
            else None
        )

        for line in info_content(label, visible_attack):
            st.write(line)

    st.divider()

    # 서버 내부 기능
    st.markdown("**상단 기능 — 서버 내부 보안 설정**")

    top_cols = st.columns(4)

    for i, control in enumerate(TOP_CONTROLS):
        with top_cols[i % 4]:
            active = control in st.session_state.enabled_controls

            button_text = (
                "해제: " if active else "적용: "
            ) + control

            if st.button(
                button_text,
                key=f"top_{control}",
                use_container_width=True,
            ):
                if active:
                    st.session_state.enabled_controls.remove(control)
                    add_log(f"보안 기능 해제: {control}", "CONFIG")

                else:
                    st.session_state.enabled_controls.add(control)
                    add_log(f"보안 기능 적용: {control}", "CONFIG")

                st.rerun()

    st.caption(
        "적용된 기능: "
        + (
            ", ".join(sorted(st.session_state.enabled_controls))
            if st.session_state.enabled_controls
            else "없음"
        )
    )

    st.divider()

    # 외부 보안 서비스
    st.markdown("**하단 기능 — 외부 보안 서비스**")

    bottom_cols = st.columns(3)

    for i, control in enumerate(BOTTOM_CONTROLS):
        with bottom_cols[i % 3]:
            active = control in st.session_state.enabled_controls

            button_text = (
                "해제: " if active else "도입: "
            ) + control

            if st.button(
                button_text,
                key=f"bottom_{control}",
                use_container_width=True,
            ):
                if active:
                    st.session_state.enabled_controls.remove(control)
                    add_log(f"외부 보안 기능 해제: {control}", "CONFIG")

                else:
                    st.session_state.enabled_controls.add(control)
                    add_log(f"외부 보안 기능 도입: {control}", "CONFIG")

                st.rerun()

    st.divider()

    # 이벤트 로그 및 상태
    log_col, status_col = st.columns([2, 1])

    with log_col:
        st.markdown("**시스템 이벤트 로그**")

        if not st.session_state.logs:
            st.caption("아직 기록된 이벤트가 없습니다.")

        else:
            for line in st.session_state.logs[:10]:
                st.markdown(
                    f"<div class='logline'>{line}</div>",
                    unsafe_allow_html=True,
                )

    with status_col:
        st.markdown("**현재 보안 설정**")

        st.write(
            f"활성화된 기능: {len(st.session_state.enabled_controls)}개"
        )

        st.write(
            "방어 성공: "
            + str(
                sum(
                    1 for item in st.session_state.history
                    if item["blocked"]
                )
            )
            + "회"
        )

        st.write(
            f"공격 이벤트: {st.session_state.event_counter}회"
        )

        if st.button("시뮬레이션 종료", use_container_width=True):
            st.session_state.result = "failure"
            st.session_state.active = False
            st.rerun()


# --------------------------------------------------
# 결과 화면
# --------------------------------------------------

def result_page():
    show_header()

    success = st.session_state.result == "success"

    if success:
        st.markdown(
            "<h2 class='success'>시뮬레이션 성공</h2>",
            unsafe_allow_html=True,
        )

        st.write(
            "현재 보안 설정으로 모든 공격 유형을 방어할 수 있는 상태에 도달했습니다."
        )

    else:
        st.markdown(
            "<h2 class='danger'>시뮬레이션 실패</h2>",
            unsafe_allow_html=True,
        )

        failed = next(
            (
                item for item in reversed(st.session_state.history)
                if not item["blocked"]
            ),
            None,
        )

        if failed:
            st.write(f"대응에 실패한 공격: **{failed['attack']}**")

            st.write(
                "필요한 대응 기능: "
                + ", ".join(ATTACKS[failed["attack"]]["defenses"])
            )

        else:
            st.write("시뮬레이션이 사용자의 요청으로 종료되었습니다.")

    st.write("")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("분석 창 보기", use_container_width=True):
            st.session_state.page = "analysis"
            st.rerun()

    with c2:
        if st.button("다시하기", use_container_width=True):
            reset_sim()


# --------------------------------------------------
# 분석 화면
# --------------------------------------------------

def analysis_page():
    show_header()
    st.subheader("성과 및 대응 분석")

    records = st.session_state.history

    failed = [item for item in records if not item["blocked"]]
    succeeded = [item for item in records if item["blocked"]]

    if failed:
        st.markdown(
            "<h3 class='danger'>대응 실패 이벤트</h3>",
            unsafe_allow_html=True,
        )

        for item in failed:
            st.markdown(
                f"**{item['time']} — {item['attack']}**"
            )

            st.write(
                "필요한 대응: "
                + ", ".join(ATTACKS[item["attack"]]["defenses"])
            )

            st.write("결과: 방어 기능이 충분히 적용되지 않았습니다.")

    st.markdown(
        "<h3 class='success'>방어 성공 이벤트</h3>",
        unsafe_allow_html=True,
    )

    if succeeded:
        for item in succeeded:
            st.markdown(
                f"**{item['time']} — {item['attack']}**"
            )

            st.write(
                "방어에 사용된 기능: "
                + ", ".join(item["controls"])
            )

    else:
        st.write("방어에 성공한 이벤트가 없습니다.")

    st.markdown("**현재 활성화된 기능**")

    st.write(
        ", ".join(sorted(st.session_state.enabled_controls))
        or "없음"
    )

    if st.button("결과 창으로 돌아가기"):
        st.session_state.page = "result"
        st.rerun()


# --------------------------------------------------
# 메인 화면 이동
# --------------------------------------------------

if st.session_state.page == "home":
    home()

elif st.session_state.page == "attacks":
    attacks_page()

elif st.session_state.page == "guide":
    guide_page()

elif st.session_state.page == "sim":
    sim_page()

elif st.session_state.page == "result":
    result_page()

elif st.session_state.page == "analysis":
    analysis_page()

else:
    st.session_state.page = "home"
    st.rerun()
