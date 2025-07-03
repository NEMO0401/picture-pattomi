
import streamlit as st
from PIL import Image, ImageChops, ImageDraw
import fitz  # PyMuPDF
import io
import base64

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

# PDFページを画像として読み込む関数（PyMuPDFを使用）
def load_image(file, page_num):
    if file.name.endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        if page_num < len(doc):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=200)
            image = Image.open(io.BytesIO(pix.tobytes("png")))
            return image.convert("RGB")
        else:
            st.warning(f"{file.name} にはページ {page_num + 1} は存在しません。1ページ目を表示します。")
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=200)
            return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
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
