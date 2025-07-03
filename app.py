import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image, ImageChops, ImageDraw
import io
import base64

# Base64に変換してロゴを表示
def ImageToBase64(image: Image.Image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# ロゴ表示
logo = Image.open("logo.png")
st.markdown(
    f"<div style='text-align: center'><img src='data:image/png;base64,{ImageToBase64(logo)}' style='height:auto; width:300px;'/></div>",
    unsafe_allow_html=True
)

# ファイルアップロード
uploaded_file1 = st.file_uploader("変更前ファイルをアップロード（PDF・PNG・JPG）", type=["pdf", "png", "jpg", "jpeg"])
uploaded_file2 = st.file_uploader("変更後ファイルをアップロード（PDF・PNG・JPG）", type=["pdf", "png", "jpg", "jpeg"])

# 画像を読み込む関数
def load_image(file, page_num):
    if file.name.endswith(".pdf"):
        # ① 一度ファイルを読み込んで変数に保存
        file_bytes = file.read()
        
        # ② そのバイナリを convert_from_bytes に渡す
        images = convert_from_bytes(
        file_bytes,
        dpi=200,
        poppler_path="C:/poppler-24.08.0/Library/bin"  # ここが新しい場所
        )

        
        if page_num < len(images):
            return images[page_num]
        else:
            st.warning(f"{file.name} にはページ {page_num + 1} は存在しません。1ページ目を表示します。")
            return images[0]
    else:
        return Image.open(file).convert("RGB")


# 差分を比較する関数
def compare_images(img1, img2):
    if img1.size != img2.size:
        img2 = img2.resize(img1.size)
    diff = ImageChops.difference(img1, img2)
    bbox = diff.getbbox()
    if not bbox:
        return None
    draw = ImageDraw.Draw(diff)
    draw.rectangle(bbox, outline="red", width=3)
    return diff

# 比較処理
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
