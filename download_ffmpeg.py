import urllib.request
import zipfile
import os
import shutil

print("下载 ffmpeg...")
url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
zip_path = "ffmpeg-essentials.zip"

urllib.request.urlretrieve(url, zip_path)
print("下载完成，解压中...")

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall("temp_ffmpeg")

# 找到 ffmpeg.exe 并移动到 ffmpeg 目录
for root, dirs, files in os.walk("temp_ffmpeg"):
    if "ffmpeg.exe" in files:
        src = os.path.join(root, "ffmpeg.exe")
        if not os.path.exists("ffmpeg"):
            os.makedirs("ffmpeg")
        shutil.copy(src, "ffmpeg/ffmpeg.exe")
        print(f"ffmpeg.exe 已复制到 ffmpeg 目录")
        break

# 清理临时文件
shutil.rmtree("temp_ffmpeg")
os.remove(zip_path)
print("完成！")
