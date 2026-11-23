import streamlit as st

from capture_rules import DIFFICULTIES, SHELLS, TARGETS, TIMING_GRADES, Game, clock_ms
from orbit_view import draw_board

st.set_page_config(page_title="전자껍질 리듬게임", page_icon="⚛️", layout="centered")
# An open tab may still hold a game object from before a deployment.
if not isinstance(st.session_state.get("game"), Game):
    st.session_state.game = None
st.session_state.setdefault("best_score", 0)


def start_game():
    difficulty = DIFFICULTIES[st.session_state.difficulty]
    st.session_state.game = Game(difficulty, clock_ms())


def capture():
    game = st.session_state.game
    game.capture(clock_ms())
    if game.complete:
        st.session_state.best_score = max(st.session_state.best_score, game.score)


def reset_game():
    st.session_state.game = None
    st.rerun()


def game_screen():
    game = st.session_state.game
    now = clock_ms()
    if game:
        game.advance(now)

    st.image(draw_board(game, now), width="stretch")
    if game is None:
        st.selectbox("난이도", list(DIFFICULTIES), key="difficulty",
                     format_func=lambda mode: f"{mode} · {DIFFICULTIES[mode].bpm} BPM")
        if st.button("게임 시작", type="primary", width="stretch"):
            start_game()
            st.rerun()
        return

    if game.complete:
        st.success("리튬 원자 완성!  K 껍질 2개 · L 껍질 1개")
        if st.button("다시 플레이", type="primary", width="stretch"):
            reset_game()
    else:
        st.button("전자 포획", type="primary", width="stretch", on_click=capture)
        cue = "지금 포획!" if game.in_capture_window(now) else "노란 구간에서 포획"
        st.caption(f"{SHELLS[game.target][0]} 껍질 · {game.difficulty.bpm} BPM · {cue}")
        if game.feedback:
            st.write(game.feedback)

    st.progress(len(game.captured) / len(TARGETS),
                text=f"포획 {len(game.captured)} / {len(TARGETS)}")
    st.write(f"**점수 {game.score}**　·　콤보 {game.combo}　·　MISS {game.misses}")
    if st.session_state.best_score:
        st.caption(f"이번 접속 최고 점수 · {st.session_state.best_score}점")
    if not game.complete and st.button("처음으로"):
        reset_game()


st.title("전자껍질 리듬게임")
st.markdown("**리튬 (Li) · 원자번호 3**")
st.write("노란 전자가 **노란 구간**에 들어오면 **전자 포획** 버튼을 누르세요.")

game = st.session_state.game
refresh = None if game is None else 0.09
st.fragment(game_screen, run_every=refresh)()

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
    st.caption("리튬의 바닥상태 전자배치는 1s² 2s¹입니다. 화면은 교육용 보어 모형입니다.")
