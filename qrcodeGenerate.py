# 먼저 필요한 라이브러리를 설치합니다.
# 터미널이나 명령 프롬프트에서 아래 명령어를 실행하세요.
# > pip install streamlit qrcode pillow

import streamlit as st           # Streamlit: 간단한 파이썬 웹 앱을 쉽게 만들 수 있게 해주는 프레임워크입니다.
import qrcode                     # qrcode: QR 코드를 생성해주는 라이브러리입니다. (pip install qrcode)
from PIL import Image             # Pillow(PIL): 이미지를 열고, 편집하고, 저장할 수 있는 라이브러리입니다. (pip install pillow)
from io import BytesIO            # BytesIO: 메모리 상에서 바이트 스트림을 다룰 수 있게 해주는 모듈입니다.

# --- 페이지 설정 및 제목 ---
st.set_page_config(
    page_title="QR 코드 생성기",     # 브라우저 탭에 표시될 제목을 설정합니다.
    layout="wide"                  # 레이아웃을 화면 전체로 펼치도록 설정합니다.
)
st.title("📱 QR 코드 생성기")      # 앱 상단에 큰 제목을 출력합니다.

# 1. 데이터 유형 선택
# 사용자가 QR 코드에 담을 데이터의 유형을 선택할 수 있도록 드롭다운 박스를 생성합니다.
data_type = st.selectbox(
    "데이터 유형 선택",
    ["", "텍스트", "URL", "연락처", "Wi-Fi", "위치"]
)

# 2. 입력 폼
# 선택된 데이터 유형에 따라 입력할 폼(UI 컴포넌트)을 분기 처리합니다.
if data_type == "텍스트":
    data = st.text_area("텍스트를 입력하세요")  
    # 여러 줄 입력이 가능하도록 텍스트 에어리어를 제공합니다.
elif data_type == "URL":
    data = st.text_input("URL을 입력하세요")
    # 한 줄 입력이 가능한 텍스트 인풋 박스를 사용합니다.
elif data_type == "연락처":
    # 연락처(vCard) 형식의 데이터를 입력받습니다.
    name = st.text_input("이름")
    phone = st.text_input("전화번호")
    email = st.text_input("이메일")
    addr = st.text_input("주소")
    # 입력된 값을 vCard 포맷에 맞춰 문자열로 조합합니다.
    data = (
        "BEGIN:VCARD\n"
        "VERSION:3.0\n"
        f"N:{name}\n"
        f"TEL:{phone}\n"
        f"EMAIL:{email}\n"
        f"ADR:{addr}\n"
        "END:VCARD"
    )
elif data_type == "Wi-Fi":
    # Wi-Fi 연결 정보 형식의 데이터를 입력받습니다.
    ssid = st.text_input("SSID")
    pwd = st.text_input("암호", type="password")
    auth = st.selectbox("암호화 방식", ["WPA", "WEP", "None"])
    # Wi-Fi 연결 문자열 포맷: WIFI:T:<방식>;S:<SSID>;P:<암호>;;
    data = f"WIFI:T:{auth};S:{ssid};P:{pwd};;"
elif data_type == "위치":
    # 위치 정보를 입력받아 구글 맵 링크로 생성합니다.
    lat = st.text_input("위도 (Latitude)")
    lon = st.text_input("경도 (Longitude)")
    data = f"https://maps.google.com/?q={lat},{lon}"
else:
    data = ""  # 아무것도 선택되지 않았을 때는 빈 문자열을 기본으로 설정합니다.

# 3. 옵션 (사이드바에서 설정)
st.sidebar.header("옵션")  
# QR 코드 시각적 요소들을 조정할 수 있는 슬라이더와 컬러 피커를 제공합니다.
box_size    = st.sidebar.slider("QR 크기 (box_size)", 1, 20, 10)
border      = st.sidebar.slider("테두리 크기 (border)", 1, 10, 4)
fill_color  = st.sidebar.color_picker("전경색", "#000000")
back_color  = st.sidebar.color_picker("배경색", "#FFFFFF")
logo_file   = st.sidebar.file_uploader("로고 삽입 (선택)", type=["png", "jpg", "jpeg"])
# file_uploader: 사용자가 로고 이미지를 업로드할 수 있도록 합니다.

# 4. 생성 버튼: 누르면 QR 코드를 생성합니다.
generate = st.button("QR 코드 생성", key="generate_qr")

if generate:
    if not data:
        # 데이터가 비어있으면 경고 메시지를 표시합니다.
        st.warning("❗️ 먼저 데이터를 입력해주세요.")
    else:
        # --- QR 코드 객체 생성 및 데이터 추가 ---
        qr = qrcode.QRCode(
            version=None,                               # 자동 버전 결정
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # 높은 오류 수정 수준
            box_size=box_size,                          # 각 픽셀 박스 사이즈
            border=border                               # 테두리(모듈 1칸 기준)
        )
        qr.add_data(data)    # QR 코드에 데이터를 추가합니다.
        qr.make(fit=True)    # 필요한 최소 크기로 QR 코드를 만듭니다.

        # 이미지를 생성하고 RGB 모드로 변환합니다.
        img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")

        # --- 로고 합성 (선택 사항) ---
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA")
            # Pillow 버전에 따른 호환성 처리: 리샘플링 필터 선택
            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                resample_filter = Image.LANCZOS

            qr_w, qr_h = img.size
            factor = 5  # 로고 크기를 QR 코드 크기의 1/5로 설정
            logo_size = (qr_w // factor, qr_h // factor)
            logo = logo.resize(logo_size, resample_filter)  # 리사이즈

            # 로고를 중앙에 배치할 좌표 계산
            pos = ((qr_w - logo_size[0]) // 2, (qr_h - logo_size[1]) // 2)
            img.paste(logo, pos, mask=logo)  # 투명도 마스크를 활용해 합성

        # --- 결과 출력 ---
        st.image(img, caption="✅ 생성된 QR 코드", use_container_width=True)
        # use_container_width=True: 이미지가 컨테이너 너비에 맞게 자동 조절됩니다.

        # --- 다운로드 기능 ---
        buffer = BytesIO()                 # 메모리 버퍼 생성
        img.save(buffer, format="PNG")     # 이미지를 PNG 형식으로 버퍼에 저장
        buffer.seek(0)                     # 버퍼의 읽기 위치를 처음으로 돌립니다.
        st.download_button(
            label="📥 QR 코드 다운로드",
            data=buffer,
            file_name="qr_code.png",
            mime="image/png"
        )  # 다운로드 버튼을 생성하여 사용자가 QR 코드를 저장할 수 있게 합니다.
