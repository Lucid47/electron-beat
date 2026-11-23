import streamlit as st

from stage_board import draw_board
from stage_rules import DIFFICULTIES, SHELL_NAMES, STAGES, TIMING_GRADES, Game, clock_ms

st.set_page_config(page_title="전자껍질 리듬게임", page_icon="⚛️", layout="centered")
# A tab opened before deployment may still hold the old single-stage game.
if not isinstance(st.session_state.get("game"), Game):
    st.session_state.game = None
st.session_state.setdefault("unlocked_stage", 1)
st.session_state.setdefault("stage_number", 1)
st.session_state.setdefault("mode", "연습")
st.session_state.setdefault("stage_scores", {})


def start_game(number, mode):
    st.session_state.stage_number = number
    st.session_state.mode = mode
    st.session_state.game = Game(STAGES[number - 1], DIFFICULTIES[mode], clock_ms())


def capture():
    game = st.session_state.game
    game.capture(clock_ms())
    if game.complete:
        number = game.stage.number
        scores = st.session_state.stage_scores
        scores[number] = max(scores.get(number, 0), game.score)
        st.session_state.unlocked_stage = max(
            st.session_state.unlocked_stage, min(number + 1, len(STAGES))
        )


def return_to_lobby():
    st.session_state.game = None
    st.rerun()


def select_stage():
    st.session_state.stage_number = st.session_state.stage_choice


def stage_heading(stage):
    st.markdown(f"**스테이지 {stage.number} / {len(STAGES)} · {stage.name} ({stage.symbol})**")


def show_lobby():
    stage = STAGES[st.session_state.stage_number - 1]
    stage_heading(stage)
    st.image(draw_board(stage, clock_ms()), width="stretch")
    st.selectbox(
        "스테이지",
        range(1, st.session_state.unlocked_stage + 1),
        index=stage.number - 1,
        key="stage_choice",
        format_func=lambda number: f"{number}. {STAGES[number - 1].name} ({STAGES[number - 1].symbol})",
        on_change=select_stage,
    )
    if st.session_state.unlocked_stage < len(STAGES):
        st.caption("원자를 완성하면 다음 스테이지가 열립니다. 해금은 이번 접속에 저장됩니다.")
    mode = st.selectbox(
        "난이도",
        list(DIFFICULTIES),
        index=list(DIFFICULTIES).index(st.session_state.mode),
        format_func=lambda name: f"{name} · {DIFFICULTIES[name].bpm} BPM",
    )
    if st.button("게임 시작", type="primary", width="stretch"):
        start_game(stage.number, mode)
        st.rerun()


def game_screen():
    game = st.session_state.game
    stage = game.stage
    now = clock_ms()
    game.advance(now)
    st.image(draw_board(stage, now, game), width="stretch")

    if game.complete:
        st.success(f"{stage.name} 원자 완성! {stage.shell_summary}")
        st.write(f"**바닥상태 전자배치** {stage.configuration}")
        if stage.number == len(STAGES):
            st.success("수소부터 네온까지 모든 스테이지를 완료했습니다!")
        elif st.button(
            f"다음 스테이지 · {STAGES[stage.number].name}", type="primary", width="stretch"
        ):
            start_game(stage.number + 1, st.session_state.mode)
            st.rerun()
    else:
        st.button("전자 포획", type="primary", width="stretch", on_click=capture)
        cue = "지금 포획!" if game.in_capture_window(now) else "노란 구간에서 포획"
        st.caption(f"{SHELL_NAMES[game.target]} 껍질 · {game.difficulty.bpm} BPM · {cue}")
        if game.feedback:
            st.write(game.feedback)

    captured = len(game.captured)
    st.progress(captured / stage.number, text=f"포획 {captured} / {stage.number}")
    st.write(f"**점수 {game.score}**　·　콤보 {game.combo}　·　MISS {game.misses}")
    best_score = st.session_state.stage_scores.get(stage.number)
    if best_score:
        st.caption(f"이번 접속의 스테이지 최고 점수 · {best_score}점")
    if game.complete and st.button("다시 플레이"):
        start_game(stage.number, st.session_state.mode)
        st.rerun()
    if st.button("스테이지 선택"):
        return_to_lobby()


st.title("전자껍질 리듬게임")
st.write("노란 전자가 **노란 구간**에 들어오면 **전자 포획** 버튼을 누르세요.")

game = st.session_state.game
if game is None:
    show_lobby()
else:
    stage_heading(game.stage)
    st.fragment(game_screen, run_every=0.09)()

with st.expander("판정과 전자배치"):
    for mode, difficulty in DIFFICULTIES.items():
        grades = [
            f"{label} ±{limit}ms"
            for limit, (label, _) in zip(difficulty.windows_ms, TIMING_GRADES)
        ]
        st.write(f"**{mode}** · {' · '.join(grades)}")
    st.write("전자 포획 점수는 PERFECT 100점, GREAT 70점, GOOD 40점입니다.")
    st.write("일찍 눌렀다면 같은 전자에 다시 도전할 수 있습니다. 전자가 구간을 지나면 MISS입니다.")
    st.write("연속 포획에 성공하면 두 번째부터 10점씩 더 받습니다.")
    st.caption("화면은 껍질별 전자 수를 설명하는 교육용 보어 모형입니다.")
