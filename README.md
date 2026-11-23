# 전자껍질 리듬게임

Streamlit에서 리튬 원자를 완성하는 Python 리듬게임입니다. 노란 전자가 포획 구간 안에 있을 때 PC에서 클릭하거나 모바일에서 터치하세요. K 껍질에 2개, L 껍질에 1개를 채우면 완성입니다. 포획 구간은 판정선 기준 연습 모드 ±550ms, 보통 모드 ±350ms입니다.

- [Streamlit에서 게임 플레이](https://electron-beat-lrft2vmtylcozopf2bjezx.streamlit.app/)
- [전체 개발계획서와 GitHub 포크·배포 안내](DEVELOPMENT_PLAN.md)

## 실행

Python 3.12 환경에서 아래 명령을 실행합니다.

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit Community Cloud에서 배포하려면 이 저장소와 `main` 브랜치, `app.py`를 선택합니다.

## 구현

- `capture_rules.py`는 전자배치 리스트, 반복문, 조건문과 함수를 사용해 목표 껍질, 박자, 타이밍 판정, 점수와 콤보를 처리합니다.
- `orbit_view.py`는 Pillow로 원자 그림을 그리고 경과 시간에 따라 전자를 이동시킵니다.
- `app.py`는 Streamlit의 기본 버튼과 부분 갱신을 사용합니다. 최고 점수는 현재 접속 세션에 저장합니다.
- 박자는 화면으로 전달합니다. 입력 시각은 Streamlit 서버에서 측정하므로 네트워크 지연이 판정에 영향을 줄 수 있습니다.
