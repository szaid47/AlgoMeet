import streamlit as st
import cv2
import time
import os
import tempfile
import zipfile
import urllib.request
from eye_movement import process_eye_movement
from head_pose import process_head_pose

# Directory to save screenshots
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)

def set_dark_theme():
    st.markdown("""
    <style>
    body {
        background-color: #0f0f0f;
        color: #e5e5e5;
    }
    .stApp {
        background-color: #0f0f0f;
        color: #e5e5e5;
    }
    .stProgress > div > div > div > div {
        background-color: #a855f7 !important;
    }
    .css-1cpxqw2, .st-af, .st-ag {
        background-color: #7c3aed !important;
        color: white !important;
    }
    .stButton>button {
        background-color: #9333ea;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #6b21a8;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stSidebar {
        background-color: #1e1e1e;
        color: #e5e5e5;
    }
    .css-1v0mbdj, .css-1y4p8pa {
        background-color: #1e1e1e;
    }
    </style>
    """, unsafe_allow_html=True)

def process_video_from_path(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    calibrated_angles = (0, 0, 0)
    head_direction = "Looking at Screen"
    screenshots = []
    frame_idx = 0
    misaligned_frame_count = 0
    start_time = time.time()

    progress_bar = st.progress(0, text="⏳ Processing video...")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1
        if frame_idx % 5 != 0:
            continue

        elapsed_time = frame_idx / fps
        frame, _ = process_eye_movement(frame)

        if elapsed_time <= 5:
            _, temp_angles = process_head_pose(frame, None)
            if isinstance(temp_angles, tuple) and len(temp_angles) == 3:
                calibrated_angles = temp_angles
        else:
            frame, head_direction = process_head_pose(frame, calibrated_angles)

        if head_direction in ["Looking Left", "Looking Right"]:
            misaligned_frame_count += 1
            if misaligned_frame_count >= 6:
                filename = os.path.join(log_dir, f"head_{head_direction}_{int(elapsed_time)}.png")
                cv2.imwrite(filename, frame)
                screenshots.append(filename)
                misaligned_frame_count = 0
        else:
            misaligned_frame_count = 0

        progress_percent = int((frame_idx / total_frames) * 100)
        progress_bar.progress(min(progress_percent / 100, 1.0), text=f"⏳ Frame {frame_idx}/{total_frames}")

    cap.release()
    progress_bar.empty()
    return screenshots, round(time.time() - start_time, 2)

def zip_screenshots(screenshots):
    zip_path = os.path.join(log_dir, "misalignment_screenshots.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in screenshots:
            zipf.write(file, arcname=os.path.basename(file))
    return zip_path

def main():
    st.set_page_config(page_title="Cheating Surveillance", page_icon="🕵️", layout="centered")
    set_dark_theme()

    with st.sidebar:
        st.markdown("### 📢 Important Notice:")
        st.markdown("""
        The system detects **head or gaze misalignment lasting over 3 seconds** and captures screenshots. 
        However, these results are based on the system's analysis, and **errors might occur**. 
        Please **cross-check** the screenshots to ensure accuracy, as false positives can happen due to lighting conditions, angle, or partial visibility of the face.
        """)

    st.title("🕵️‍♂️ Cheating Surveillance System")
    st.subheader("🔍 Detect Head/Gaze Misalignment (~1 sec)")

    uploaded_video = st.file_uploader("📂 Upload Video File", type=["mp4", "avi"])
    video_link = st.text_input("🔗 Or paste a direct MP4 video URL")

    video_path = None
    if uploaded_video:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(uploaded_video.read())
            video_path = tmp.name
        st.video(uploaded_video)
    elif video_link:
        try:
            tmp_path = os.path.join(tempfile.gettempdir(), "downloaded_video.mp4")
            urllib.request.urlretrieve(video_link, tmp_path)
            video_path = tmp_path
            st.video(video_link)
        except Exception as e:
            st.error(f"❌ Error downloading video: {e}")
            return

    if video_path and st.button("▶️ Start Analysis"):
        with st.spinner("Analyzing video..."):
            screenshots, processing_time = process_video_from_path(video_path)

        st.success(f"✅ Analysis completed in {processing_time} seconds!")

        if screenshots:
            st.subheader("📸 Detected Misalignment Screenshots")
            for img in screenshots:
                st.image(img, caption=os.path.basename(img), use_container_width=True)

            zip_path = zip_screenshots(screenshots)
            with open(zip_path, "rb") as f:
                st.download_button("📦 Download All Screenshots", f, file_name="misalignment_screenshots.zip")
        else:
            st.info("🎉 No misalignment detected lasting over ~1 second.")

if __name__ == "__main__":
    main()
