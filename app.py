import streamlit as st
import cv2
import numpy as np

st.set_page_config(page_title="CV & Data App", layout="wide")

st.title("Real-Time Video Stream with OpenCV")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Video Stream", "Other Features (Placeholder)"])

if 'stop_camera' not in st.session_state:
    st.session_state.stop_camera = False
if 'snapshot' not in st.session_state:
    st.session_state.snapshot = None
if 'latest_raw_frame' not in st.session_state: # To store the raw frame for snapshot
    st.session_state.latest_raw_frame = None

def video_stream_page():
    st.header("Webcam Live Feed")


    # --- Controls ---
    run_camera = st.toggle("Start Camera", value=not st.session_state.stop_camera)

    st.sidebar.subheader("Video Filter Options")
    filter_option = st.sidebar.selectbox(
        "Apply Filter",
        ("None", "Grayscale", "Canny Edge Detection", "Blur")
    )

    # --- Filter Specific Controls ---
    canny_threshold1 = 50
    canny_threshold2 = 150
    blur_ksize = 5

    if filter_option == "Canny Edge Detection":
        # st.sidebar.subheader("Canny Edge Detection Controls") # Subheader already exists or can be more general
        canny_threshold1 = st.sidebar.slider("Threshold 1", 0, 200, 50)
        canny_threshold2 = st.sidebar.slider("Threshold 2", 0, 400, 150)
    elif filter_option == "Blur":
        # st.sidebar.subheader("Blur Control") # Subheader already exists or can be more general
        blur_ksize = st.sidebar.slider("Kernel Size (Odd Number)", 1, 31, 5, step=2)

    image_placeholder = st.empty() # Create a placeholder for the image

    if run_camera:
        st.session_state.stop_camera = False

        cap = cv2.VideoCapture(0)  # Open the default camera
        if not cap.isOpened():
            st.error("Failed to open the webcam. Please check your camera settings.")
            st.session_state.stop_camera = True
        else:
            ret, frame = cap.read()
            if not ret:
                st.warning("Failed to capture frame from webcam.")
                st.session_state.stop_camera = True
            else:
                # Store the raw frame for snapshot
                st.session_state.latest_raw_frame = frame.copy()

                # Process the frame for display
                processed_frame = frame.copy()
                # Apply the selected filter
                if filter_option == "Grayscale":
                    processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
                elif filter_option == "Canny Edge Detection":
                    gray_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
                    processed_frame = cv2.Canny(gray_frame, canny_threshold1, canny_threshold2)
                elif filter_option == "Blur":
                    # Ensure blur_ksize is odd
                    if blur_ksize % 2 == 0: blur_ksize +=1
                    processed_frame = cv2.GaussianBlur(processed_frame, (blur_ksize, blur_ksize), 0)

                # Display the frame
                if len(processed_frame.shape) == 2: # Grayscale or Canny
                    image_placeholder.image(processed_frame, caption="Webcam Feed")
                else: # Color or Blur
                    image_placeholder.image(processed_frame, channels="BGR", caption="Webcam Feed")

            cap.release()  # Release the camera after capturing one frame

        # Snapshot button - active only if camera is running and a frame was captured
        if st.session_state.latest_raw_frame is not None:
            if st.button("Take Snapshot (Original Frame)"):
                st.session_state.snapshot = st.session_state.latest_raw_frame.copy()
                st.success("Snapshot of the original camera frame taken!")
    else:
        st.session_state.stop_camera = True
        image_placeholder.empty() # Clear the image placeholder
        st.info("Camera is off. Toggle 'Start Camera' to begin streaming.")

# --- Display Snapshot ---
if 'snapshot' in st.session_state and st.session_state.snapshot is not None:
    st.subheader("Last Snapshot")
    st.image(st.session_state.snapshot, channels="BGR", caption="Snapshot (Original Frame)")

if page == "Video Stream":
    video_stream_page()
elif page == "Other Features (Placeholder)":
    st.write("Other features will be implemented here.")