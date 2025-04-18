import streamlit as st
import qrcode               # pip install qrcode
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="QR 코드 생성기", layout="wide")
st.title("📱 QR 코드 생성기")

# 1. 데이터 유형 선택
data_type = st.selectbox("데이터 유형 선택", ["", "텍스트", "URL", "연락처", "Wi-Fi", "위치"])

# 2. 입력 폼
if data_type == "텍스트":
    data = st.text_area("텍스트를 입력하세요")
elif data_type == "URL":
    data = st.text_input("URL을 입력하세요")
elif data_type == "연락처":
    name = st.text_input("이름")
    phone = st.text_input("전화번호")
    email = st.text_input("이메일")
    addr = st.text_input("주소")
    data = f"BEGIN:VCARD\nVERSION:3.0\nN:{name}\nTEL:{phone}\nEMAIL:{email}\nADR:{addr}\nEND:VCARD"
elif data_type == "Wi-Fi":
    ssid = st.text_input("SSID")
    pwd = st.text_input("암호", type="password")
    auth = st.selectbox("암호화 방식", ["WPA", "WEP", "None"])
    data = f"WIFI:T:{auth};S:{ssid};P:{pwd};;"
elif data_type == "위치":
    lat = st.text_input("위도 (Latitude)")
    lon = st.text_input("경도 (Longitude)")
    data = f"https://maps.google.com/?q={lat},{lon}"
else:
    data = ""

# 3. 옵션
st.sidebar.header("옵션")
box_size = st.sidebar.slider("QR 크기 (box_size)", 1, 20, 10)
border = st.sidebar.slider("테두리 크기 (border)", 1, 10, 4)
fill_color = st.sidebar.color_picker("전경색", "#000000")
back_color = st.sidebar.color_picker("배경색", "#FFFFFF")
logo_file = st.sidebar.file_uploader("로고 삽입 (선택)", type=["png","jpg","jpeg"])

# 4. 생성 버튼 (key 지정)
generate = st.button("QR 코드 생성", key="generate_qr")

if generate:
    if not data:
        st.warning("❗️ 먼저 데이터를 입력해주세요.")
    else:
        # QR 객체 생성
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=border
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")
        
        # --- 로고 합성 (선택 사항) ---
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA")
            
            # 호환 가능한 리샘플링 필터 선택
            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                resample_filter = Image.LANCZOS
            
            qr_w, qr_h = img.size
            factor = 5  # 로고가 QR 코드의 1/5 크기로
            logo_size = (qr_w // factor, qr_h // factor)
            logo = logo.resize(logo_size, resample_filter)
            
            pos = ((qr_w - logo_size[0]) // 2, (qr_h - logo_size[1]) // 2)
            img.paste(logo, pos, mask=logo)
        
        # --- 결과 출력 (use_container_width) ---
        st.image(img, caption="✅ 생성된 QR 코드", use_container_width=True)
        
        # --- 다운로드 버튼 ---
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        st.download_button(
            label="📥 QR 코드 다운로드",
            data=buffer,
            file_name="qr_code.png",
            mime="image/png"
        )
