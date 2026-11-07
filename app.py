```python
    st.session_state.db_blocked = set()
    st.session_state.result = None
    st.session_state.logs = []
    add_log("시뮬레이션이 시작되었습니다.")

def effective_controls():
    return set(st.session_state.enabled_controls)

def attack_is_blocked(attack_name):
    attack = ATTACKS[attack_name]
    enabled = effective_controls()
    if attack_name in st.session_state.db_blocked:
        return True, "사전 데이터베이스 설정"
    needed = set(attack["defenses"])
    mapped = {CONTROL_ALIASES.get(x, x) for x in needed}
    # The provided control menu represents the practical controls available in this simulator.
    if mapped and mapped.issubset(enabled):
        return True, "필요한 대응 기능이 모두 활성화됨"
    if attack_name == "DDoS" and ({"CDN", "DDoS 방어 서비스"} & enabled):
        return True, "외부 DDoS 방어 기능"
    if attack_name == "HTTP Flood" and {"API별 Rate Limit", "WAF"} & enabled:
        return True, "API 요청 제한 또는 WAF"
    if attack_name == "Brute Force" and ({"IP별 Rate Limit", "계정별 Rate Limit", "다중 인증(MFA)"} & enabled):
        return True, "인증 시도 제한 또는 MFA"
    if attack_name == "Password Spraying" and ({"SIEM", "다중 인증(MFA)", "IP별 Rate Limit", "계정별 Rate Limit"} & enabled):
        return True, "인증 패턴 분석 또는 인증 보호"
    if attack_name == "Credential Stuffing" and "다중 인증(MFA)" in enabled:
        return True, "다중 인증(MFA)"
    if attack_name == "SQL Injection" and ({"Prepared Statement", "WAF"} & enabled):
        return True, "질의 보호 또는 WAF"
    if attack_name == "Data Exfiltration" and ({"DLP", "데이터베이스 접근 권한 관리"} & enabled):
        return True, "정보 유출 방지 또는 접근 권한 관리"
    if attack_name == "Resource Exhaustion" and ({"CPU 및 메모리 사용량 제한", "Timeout 설정", "Connection Limit"} & enabled):
        return True, "서버 자원 보호"
    if attack_name == "Slowloris" and ({"Connection Limit", "Timeout 설정"} & enabled):
        return True, "연결 수 또는 대기 시간 제한"
    if attack_name == "Session Hijacking" and "세션 관리" in enabled:
        return True, "세션 관리"
    if attack_name == "데이터 파괴 및 랜섬웨어" and ({"EDR", "백업 및 복구 설정"} & enabled):
        return True, "단말 탐지·대응 또는 백업"
    if attack_name == "백업 및 복구 시스템 공격" and ({"백업 및 복구 설정", "데이터베이스 접근 권한 관리", "다중 인증(MFA)"} & enabled):
        return True, "백업 보호 또는 접근 통제"
    return False, ""

def generate_event():
    candidates = [name for name in ATTACKS if name not in st.session_state.db_blocked]
    if not candidates:
        st.session_state.result = "success"
        st.session_state.active = False
        return
    attack = random.choice(candidates)
    st.session_state.event_counter += 1
    st.session_state.current_event = attack
    st.session_state.event_started = time.time()
    st.session_state.event_stage = 0
    st.session_state.opened_info = None
    add_log("비정상적인 이벤트가 관찰되었습니다.", "WARN")

def resolve_event():
    name = st.session_state.current_event
    blocked, reason = attack_is_blocked(name)
    st.session_state.history.append({
        "attack": name, "blocked": blocked, "reason": reason if blocked else "대응 기능이 충분히 적용되지 않음",
        "time": datetime.now().strftime("%H:%M:%S"),
        "controls": sorted(st.session_state.enabled_controls),
    })
    if blocked:
        add_log(f"{name} 공격 시도를 방어했습니다. ({reason})", "DEFENDED")
        st.session_state.current_event = None
        st.session_state.event_started = None
        st.session_state.event_stage = 0
        st.session_state.last_event_at = time.time()
        st.session_state.next_event_in = random.randint(30, 60)
    else:
        add_log(f"{name} 공격 대응에 실패했습니다.", "CRITICAL")
        st.session_state.result = "failure"
        st.session_state.active = False

def tick():
    if not st.session_state.active:
        return
    now = time.time()
    if st.session_state.current_event is None:
        if now - st.session_state.last_event_at >= st.session_state.next_event_in:
            generate_event()
    else:
        elapsed = now - st.session_state.event_started
        stage = 0 if elapsed < 15 else 1 if elapsed < 25 else 2 if elapsed < 30 else 3
        if stage > st.session_state.event_stage:
            st.session_state.event_stage = stage
            if stage == 1:
                add_log("시스템이 비정상적인 활동을 감지했습니다.", "WARN")
            elif stage == 2:
                add_log("이상 징후 분석 힌트가 활성화되었습니다.", "WARN")
            elif stage == 3:
                add_log(f"공격 유형 추정: {st.session_state.current_event}", "WARN")
        if elapsed >= 60:
            resolve_event()
    # Success when all possible attack categories have been neutralized by the user's current configuration.
    if st.session_state.active and all(
        name in st.session_state.db_blocked or attack_is_blocked(name)[0] for name in ATTACKS
    ):
        st.session_state.result = "success"
        st.session_state.active = False
        add_log("현재 보안 설정으로 모든 공격 유형을 방어할 수 있습니다.", "SUCCESS")

def show_header():
    st.markdown("# 모의 해킹 시뮬레이터")
    st.markdown("<div class='muted'>가상의 서버 환경에서 보안 이벤트를 탐지하고 대응하는 교육용 시뮬레이션</div>", unsafe_allow_html=True)
    st.divider()

def home():
    show_header()
    st.write("")
    st.write("")
    st.markdown("<h2 style='text-align:center'>모의 해킹 시뮬레이션</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#555'>가상 서버의 이상 징후를 분석하고 적절한 방어 기능을 적용하십시오.</p>", unsafe_allow_html=True)
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
    st.caption("본 앱은 실제 네트워크에 접속하거나 공격을 수행하지 않는 가상 교육용 시뮬레이터입니다.")

def attacks_page():
    show_header()
    st.subheader("해킹 종류 및 대응 방법")
    for name, item in ATTACKS.items():
        with st.expander(name):
            st.write(item["desc"])
            st.markdown("**주요 탐지 징후**")
            for clue in item["clues"]:
                st.write(f"- {clue}")
            st.markdown("**대응 기능**")
            st.write(", ".join(item["defenses"]))
    if st.button("닫기"):
        st.session_state.page = "home"
        st.rerun()

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
- 공격 이벤트가 발생하면 최초 15초 동안 별도 경고 없이 관찰 가능
- 15초 이후 감지 알림, 25초 이후 관련 정보 버튼 강조, 30초 이후 공격 유형 공개
- 공격 이벤트마다 60초 안에 대응해야 함
""")
    if st.button("닫기"):
        st.session_state.page = "home"
        st.rerun()


def info_content(label, attack=None):
    elapsed = 0
    if attack and st.session_state.event_started:
        elapsed = time.time() - st.session_state.event_started
    attack_data = ATTACKS.get(attack) if attack else None
    if label == "네트워크 트래픽":
        return [
            f"현재 네트워크 트래픽: {random.randint(80, 260) if not attack else random.randint(450, 1800)} Mbps",
            f"최근 1분 평균: {random.randint(90, 180)} Mbps",
            "상태: 비정상 패턴 분석 중" if attack else "상태: 정상 범위",
        ]
    if label == "출발지 IP 주소":
        return [f"관찰된 출발지: 203.0.113.{random.randint(10,220)}", "추가 출발지: 198.51.100.24", "참고: 문서용 예약 IP 대역 사용"]
    if label == "목적지 IP 주소":
        return ["목적지 서버: 192.0.2.10", "서비스 포트: HTTPS (443)", "참고: 가상 서버 주소"]
    if label == "초당 요청 수(RPS)":
        return [f"현재 RPS: {random.randint(900,3200) if attack else random.randint(45,120)}", f"기준 RPS: 80", "단위: requests/second"]
    if label == "서버 CPU 및 메모리 사용량":
        return [f"CPU 사용량: {random.randint(75,99) if attack and attack in ['Resource Exhaustion','DDoS','HTTP Flood'] else random.randint(15,55)}%",
                f"메모리 사용량: {random.randint(70,96) if attack else random.randint(30,60)}%", "상태: 가상 측정값"]
    if label == "데이터베이스 연결 수":
        return [f"활성 연결: {random.randint(80,180) if attack else random.randint(8,30)}", "최대 연결: 200", "대기 연결: 4"]
    if label == "로그인 성공 및 실패 기록":
        return [f"최근 로그인 성공: {random.randint(2,12)}건", f"최근 로그인 실패: {random.randint(25,90) if attack in ['Brute Force','Credential Stuffing','Password Spraying'] else random.randint(0,5)}건", "계정명은 개인정보 보호를 위해 가상 ID로 표시"]
    if label == "데이터베이스 접근 기록":
        return [f"{datetime.now().strftime('%H:%M:%S')} SELECT 요청 — app_user", "접근 대상: customer_records (가상 테이블)", "상태: 질의 패턴 점검"]
    if label == "외부 데이터 전송량":
        return [f"최근 1분 전송량: {random.randint(500,2200) if attack == 'Data Exfiltration' else random.randint(20,180)} MB", "외부 목적지: 198.51.100.24", "상태: 전송량 기준 분석"]
    if label == "세션 정보":
        return ["활성 세션: 128", "세션 ID: SESSION-****-A31F", "상태: 가상 세션 정보"]
    if label == "백업 시스템 상태":
        return ["최근 백업: 02:00 완료", "백업 무결성: 정상" if attack not in ["데이터 파괴 및 랜섬웨어","백업 및 복구 시스템 공격"] else "백업 무결성 점검 필요",
                "백업 저장소: 격리된 가상 저장소"]
    return ["표시할 정보가 없습니다."]

@st.fragment(run_every="1s")
def sim_page():
    tick()
    if st.session_state.result:
        result_page()
        return

    show_header()
    elapsed_total = int(time.time() - st.session_state.started_at) if st.session_state.started_at else 0
    event = st.session_state.current_event
    event_elapsed = int(time.time() - st.session_state.event_started) if event and st.session_state.event_started else 0

    top_left, top_right = st.columns([3, 1])
    with top_left:
        st.subheader("서버 모니터링")
        st.caption("가상 서버 ID: SIM-SRV-01  |  상태: 운영 중  |  시간: " + datetime.now().strftime("%H:%M:%S"))
    with top_right:
        st.metric("진행 시간", f"{elapsed_total // 60:02d}:{elapsed_total % 60:02d}")

    if event:
        if event_elapsed < 15:
            st.info("관찰 단계: 별도 경고 없이 서버 정보를 확인하여 이상 징후를 탐지하십시오.")
        elif event_elapsed < 25:
            st.warning("시스템 감지: 비정상적인 활동이 감지되었습니다.")
        elif event_elapsed < 30:
            st.error("분석 힌트가 활성화되었습니다. 관련 정보 버튼이 빨간색으로 표시됩니다.")
        else:
            st.error(f"공격 유형 추정: {event}")
        remaining = max(0, 60 - event_elapsed)
        st.progress(remaining / 60, text=f"현재 이벤트 대응 시간: {remaining}초")
    else:
        until = max(0, st.session_state.next_event_in - int(time.time() - st.session_state.last_event_at))
        st.info(f"현재 진행 중인 공격 이벤트가 없습니다. 다음 이벤트까지 약 {until}초")

    st.markdown("**서버 정보 열기**")
    info_cols = st.columns(6)
    info_labels = list(INFO_KEYS.keys())
    for i, label in enumerate(info_labels):
        with info_cols[i % 6]:
            is_open = st.session_state.opened_info == label
            is_hint = bool(event and event_elapsed >= 25 and label == ATTACKS[event]["log_type"])
            button_label = ("● " if is_open else "") + label
            if st.button(button_label, key=f"info_{label}", use_container_width=True):
                st.session_state.opened_info = None if is_open else label
                st.rerun()
            if is_hint:
                st.markdown("<span class='danger'>분석 힌트 관련 정보</span>", unsafe_allow_html=True)

    if st.session_state.opened_info:
        label = st.session_state.opened_info
        st.markdown(f"<div class='panel'><b>{label}</b></div>", unsafe_allow_html=True)
        lines = info_content(label, event if event and event_elapsed >= 25 else None)
        for line in lines:
            st.write(line)

    st.divider()
    st.markdown("**상단 기능 — 서버 내부 보안 설정**")
    top_cols = st.columns(4)
    for i, control in enumerate(TOP_CONTROLS):
        with top_cols[i % 4]:
            active = control in st.session_state.enabled_controls
            if st.button(("해제: " if active else "적용: ") + control, key=f"top_{control}", use_container_width=True):
                if active:
                    st.session_state.enabled_controls.remove(control)
                    add_log(f"보안 기능 해제: {control}", "CONFIG")
                else:
                    st.session_state.enabled_controls.add(control)
                    add_log(f"보안 기능 적용: {control}", "CONFIG")
                st.rerun()
    st.caption("적용된 기능: " + (", ".join(sorted(st.session_state.enabled_controls)) if st.session_state.enabled_controls else "없음"))

    st.divider()
    st.markdown("**하단 기능 — 외부 보안 서비스**")
    bottom_cols = st.columns(3)
    for i, control in enumerate(BOTTOM_CONTROLS):
        with bottom_cols[i % 3]:
            active = control in st.session_state.enabled_controls
            if st.button(("해제: " if active else "도입: ") + control, key=f"bottom_{control}", use_container_width=True):
                if active:
                    st.session_state.enabled_controls.remove(control)
                    add_log(f"외부 보안 기능 해제: {control}", "CONFIG")
                else:
                    st.session_state.enabled_controls.add(control)
                    add_log(f"외부 보안 기능 도입: {control}", "CONFIG")
                st.rerun()

    st.divider()
    log_col, status_col = st.columns([2, 1])
    with log_col:
        st.markdown("**시스템 이벤트 로그**")
        if not st.session_state.logs:
            st.caption("아직 기록된 이벤트가 없습니다.")
        else:
            for line in st.session_state.logs[:10]:
                st.markdown(f"<div class='logline'>{line}</div>", unsafe_allow_html=True)
    with status_col:
        st.markdown("**현재 보안 설정**")
        st.write(f"활성화된 기능: {len(st.session_state.enabled_controls)}개")
        st.write(f"방어 성공: {sum(1 for x in st.session_state.history if x['blocked'])}회")
        st.write(f"공격 이벤트: {st.session_state.event_counter}회")
        if st.button("시뮬레이션 종료", use_container_width=True):
            st.session_state.result = "failure"
            st.session_state.active = False
            st.rerun()


def result_page():
    show_header()
    success = st.session_state.result == "success"
    if success:
        st.markdown("<h2 class='success'>시뮬레이션 성공</h2>", unsafe_allow_html=True)
        st.write("현재 보안 설정으로 모든 공격 유형을 방어할 수 있는 상태에 도달했습니다.")
    else:
        st.markdown("<h2 class='danger'>시뮬레이션 실패</h2>", unsafe_allow_html=True)
        failed = next((x for x in reversed(st.session_state.history) if not x["blocked"]), None)
        if failed:
            st.write(f"대응에 실패한 공격: **{failed['attack']}**")
            st.write("필요한 대응 기능: " + ", ".join(ATTACKS[failed["attack"]]["defenses"]))
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

def analysis_page():
    show_header()
    st.subheader("성과 및 대응 분석")
    records = st.session_state.history
    failed = [x for x in records if not x["blocked"]]
    succeeded = [x for x in records if x["blocked"]]
    if failed:
        st.markdown("<h3 class='danger'>대응 실패 이벤트</h3>", unsafe_allow_html=True)
        for item in failed:
            st.markdown(f"**{item['time']} — {item['attack']}**")
            st.write("필요한 대응: " + ", ".join(ATTACKS[item["attack"]]["defenses"]))
            st.write("결과: " + item["reason"])
    st.markdown("<h3 class='success'>방어 성공 이벤트</h3>", unsafe_allow_html=True)
    if succeeded:
        for item in succeeded:
            st.markdown(f"**{item['time']} — {item['attack']}**")
            st.write("방어 판정: " + item["reason"])
            st.write("당시 활성화된 기능: " + (", ".join(item["controls"]) if item["controls"] else "없음"))
    else:
        st.write("방어에 성공한 이벤트가 없습니다.")
    st.markdown("**현재 활성화된 기능**")
    st.write(", ".join(sorted(st.session_state.enabled_controls)) or "없음")
    if st.button("결과 창으로 돌아가기"):
        st.session_state.page = "result"
        st.rerun()

# Main router
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
