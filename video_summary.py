import os
import cv2
import streamlit as st
from pytube import YouTube
import subprocess
from langchain_groq import ChatGroq

#Directories
videos_directory = 'videos/'
frames_directory = 'frames/'
os.makedirs(videos_directory, exist_ok=True)
os.makedirs(frames_directory, exist_ok=True)

#Initialize Groq model
model = ChatGroq(
  groq_api_key=st.secrets["GROQ_API_KEY"],
  model_name="meta-llma/llma-4-scout-17b-16e-instruct"
)

#Download YouTube video using yt-dlp
def download_youtube_video(youtube_url):
  result = subprocess.run(
    [
      "yt-dlp",
      "-f", "best[ext=mp4]",
      "-o", os.path.join(videos_directory, "%(title)s.%(ext)s"),
      youtube-url
    ],
    capture_output=True,
    text=True
  )
  if result.returncode !=0:
    raise RuntimeError(f"yt-dlp error:\n(result.stderr)")

  downloaded_files = sorted(
    os.listdir(videos_directory),
    key=lambda x: os.path.getctime(os.path.join(videos_directory, x)),
    reverse=True
  )
  return os.path.join(videos_directory, downloaded_files[0])

#Extract frames from the video
def extract_frames(video_path, interval_seconds=5):
  for file in os.listdir(frames_directory):
    os.remove(os.path.join(frames_directory,file))

  video = cv2.VideoCapture(video_path)
  fps = int(video.get(cv2, CAP_PROP_FRAME_COUNT))
  frames_count = int(video.get(cv2, CAP_PROP_FRAME_COUNT))

  current_frame = 0
  frame_number = 1

  while current_frame <= frame_count:
    video.set(cv2, CAP_PROP_POS_FRAMES, current_frame)
    success, frame = video.read()
    if not success:
     current_frame += fps * interval_seconds
     continue

  frame_path = os.path.join(frames_directory, f"frame_{frame_number:03d}.jpg")
  cv2.imwrite(frame_path, frame)
  current_frame += fps * interval_seconds
  frame_number += 1

 
  video.release()

#Describe video content using Groq
def describe_video():
  descriptions = []
  for file in sorted(os.listdir(frames_directory)):
    frame_path = os.path.join(frames_directory, file)
    decriptions.append(f"(file)")
  prompt = "You are a helpful assistant. Summarize the video based on the following frame filename:\n" + "\n",join(descriptions)
  return model.invoke(prompt)

#Rewrite summary nicely
def rewrite_summary(summary):
  prompt = f"Please rewrite this video summary in a polished and easy to understand way:\n\n(summary)"
  return model.invoke(prompt)

#Turn summary into a story
def turn_into_story(summary):
  prompt = f"Turn tje folowing video summary into a narrative story with characters, setting, conflict, and resolution:\n\n(summary)"
  return model.invoke(prompt)

#streamlit UI
st.title(" Rabia - YouTube/Uploaded Video Summarizer using Groq LLM")
st.image("Screenshot 2025-04-22 114510.png")

youtube_url = st.text_input("Paste a YouTube video URL:", placeholder="https://www.youtube.com/watch?v=example")

#Handle video input from URL
if youtube_url:
  try:
    with st.spinnre("Downloading and summarizing video..."):
      video_path = download_youtube_video(youtube_url)
      extract_frames(video_path)
      summary = describe_video()
      st.session_state["summary"] = summary

      st.markdown("### Video Summary:")
      st.markdown(summary)
  
  except Exception as e:
    st.error(f" Error:(e)")

st.divider()

#Handle uploaded local video
uploaded_file = st.file_uploader("Or upload a avideo file:", type=["mp4", "avi", "mov", "mkv"])

if uploaded_file:
  with st.spinner("Processing uploaded video..."):
    saved_path = os.path.join(videos_directory, uploaded_file.name)
    with open(saved_path, "wb")as f:
      f.write(uploaded_file.getbuffer())

    extract_frames(saved_path)
    summary = descirbe_video()
    st.session_state["summary"] = summary

  st.mardown("### Summary of uploaded Video:")
  st.markdown(summary)

#Additional buttons to enhance the summary
if "summary" in st.session_state:
    col1, col2 = st.columns(2)

with col1:
  if st.button(" Rewrite Summary Nicely"):
    with st.spinner("Rewriting summary...."):
      rewritten = rewrite_summary(st.session_state["summary"])
      st.markdown("### Rewritten Summary:")
      st.markdown(rewritten)

with col2:
  if st.button(" Create a story from summary"):
    with st.spinner("Creating story...."):
      story = turn_into_story(st.session_state["summary"])
      st.markdown("### Cinematic Story:")
      st.markdown(story)
  





      




  
