import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image, ImageChops, ImageDraw
import io
import base64

def ImageToBase64(image: Image.Image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# タイトル
logo = Image.open("logo.png")
st.markdown(
    f"<div style='text-align: center'><img src='data:image/png;base64,{ImageToBase64(logo)}' style='height:auto; width:300px;'/></div>",
    unsafe_allow_html=True
)

# ファイルアップロード（2ファイルまで）
uploaded_file1 = st.file_uploader("変更前ファイルをアップロード（ドラッグ＆ドロップ対応 / PDF・PNG・JPG）", type=["pdf", "png", "jpg", "jpeg"])
uploaded_file2 = st.file_uploader("変更後ファイルをアップロード（ドラッグ＆ドロップ対応 / PDF・PNG・JPG）", type=["pdf", "png", "jpg", "jpeg"])

def load_image(file, page_num):
    if file.name.endswith(".pdf"):
        images = convert_from_bytes(file.read(), dpi=200, poppler_path="C:/Users/all/Downloads/Tools/poppler-24.08.0/Library/bin")
        if page_num < len(images):
            return images[page_num]
        else:
            st.warning(f"{file.name} にはページ {page_num + 1} は存在しません。1ページ目を表示します。")
            return images[0]
    else:
        return Image.open(file).convert("RGB")

def compare_images(img1, img2):
    # サイズが違う場合はリサイズ
    if img1.size != img2.size:
        img2 = img2.resize(img1.size)
    diff = ImageChops.difference(img1, img2)
    bbox = diff.getbbox()
    if not bbox:
        return None  # 差分なし
    # 赤い枠で差分を表示
    draw = ImageDraw.Draw(diff)
    draw.rectangle(bbox, outline="red", width=3)
    return diff

if uploaded_file1 and uploaded_file2:
    page_num = st.number_input("比較したいページ番号（1ページ目は1）", min_value=1, value=1, step=1) - 1
    try:
        st.subheader("比較結果：")
        image1 = load_image(uploaded_file1, page_num)
        image2 = load_image(uploaded_file2, page_num)

        st.image([image1, image2], caption=["変更前", "変更後"], width=300)

        result = compare_images(image1, image2)

        if result:
            st.image(result, caption="差分（赤枠で表示）")
            st.success("違いが見つかりました！")
        else:
            st.info("2つの画像／PDFページは完全に一致しています。")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")