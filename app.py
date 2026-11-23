import streamlit as st

from game_logic import Game, MISS_WINDOW, SHELLS, TARGETS, TEMPOS, TIMING, clock_ms
from game_view import draw_board

st.set_page_config(page_title="전자껍질 리듬게임", page_icon="⚛️", layout="centered")
st.session_state.setdefault("game", None)
st.session_state.setdefault("best_score", 0)


def start_game():
    bpm, travel_ms = TEMPOS[st.session_state.difficulty]
    st.session_state.game = Game(bpm, travel_ms, clock_ms())


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
        st.selectbox("난이도", list(TEMPOS), key="difficulty",
                     format_func=lambda mode: f"{mode} · {TEMPOS[mode][0]} BPM")
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
        cue = "지금 포획!" if abs(now - game.hit_at) <= MISS_WINDOW else "전자 대기"
        st.caption(f"{SHELLS[game.target][0]} 껍질 · {game.bpm} BPM · {cue}")
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
st.write("노란 전자가 판정선(HIT)에 닿을 때 **전자 포획** 버튼을 누르세요.")

game = st.session_state.game
refresh = None if game is None else 0.09
st.fragment(game_screen, run_every=refresh)()

with st.expander("판정과 전자배치"):
    for limit, label, points in TIMING:
        st.write(f"**{label}** · ±{limit}ms 이내 · +{points}점")
    st.write("**MISS** · ±200ms 초과 · 0점")
    st.write("연속 포획에 성공하면 두 번째부터 10점씩 더 받습니다.")
    st.caption("리튬의 바닥상태 전자배치는 1s² 2s¹입니다. 화면은 교육용 보어 모형입니다.")
