import subprocess
import os
import re
from pathlib import Path

''' 这个脚本可以使用ffmpeg批量分离视频中的音频'''

def process_video(file_name):
    print(f"Processing video: {file_name}")
    # 使用 ffmpeg 提取音频
    audio_output_path = str(file_name)[0:-4]+"_"+"audio.wav"
    command = f"ffmpeg -i "+str(file_name)+" -vn -acodec pcm_s16le -ar 44100 -ac 2 "+f"{audio_output_path}"
    print(command)
    subprocess.run(command, shell=True)

folder_path="D:\ziyan\\video\80066455"
# 正则表达式，匹配常见的视频文件扩展名
video_pattern = re.compile(r".*\.(mp4|avi|mkv|mov|flv)$", re.IGNORECASE)

# 切换到指定的目录
os.chdir(folder_path)
# 使用pathlib遍历文件夹中的所有文件

for file in Path('.').iterdir():
    # 检查文件是否匹配正则表达式
    if file.is_file() and video_pattern.match(file.name):
        process_video(file)