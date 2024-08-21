import os
import sys
import ffmpeg
from ffmpeg.nodes import filter_operator, output_operator

def download_ffmpeg():
    import subprocess
    import urllib.request
    import zipfile

    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = "ffmpeg.zip"
    extract_path = "ffmpeg"

    print("Downloading FFmpeg...")
    urllib.request.urlretrieve(ffmpeg_url, zip_path)

    print("Extracting FFmpeg...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    ffmpeg_path = os.path.join(extract_path, "ffmpeg-master-latest-win64-gpl", "bin")
    os.environ["PATH"] += os.pathsep + ffmpeg_path
    print(f"FFmpeg downloaded and added to PATH: {ffmpeg_path}")

    os.remove(zip_path)

def split_mp3(file_path, max_size_mb=2, output_folder="output"):
    # Check if the input file exists
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        # Get the duration of the input file
        probe = ffmpeg.probe(file_path)
        duration = float(probe['streams'][0]['duration'])

        # Calculate the duration of each chunk (in seconds)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
        chunk_duration = (max_size_mb / file_size) * duration

        # Split the audio file
        for i, start in enumerate(range(0, int(duration), int(chunk_duration))):
            chunk_name = f"{output_folder}/chunk_{i}.mp3"
            end = min(start + chunk_duration, duration)
            
            stream = ffmpeg.input(file_path, ss=start, t=end-start)
            stream = ffmpeg.output(stream, chunk_name)
            ffmpeg.run(stream, overwrite_output=True)
            
            print(f"Exported {chunk_name}")

        print(f"Split complete. {i+1} chunks created.")
    except ffmpeg.Error as e:
        print(f"An error occurred: {e.stderr.decode()}")

# Usage
if __name__ == "__main__":
    try:
        ffmpeg.probe("dummy")
    except:
        download_ffmpeg()

    input_file = "videns.mp3"
    split_mp3(input_file)