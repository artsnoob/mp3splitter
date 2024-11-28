import os
import subprocess
import math
import sys
import webbrowser
import urllib.request
import zipfile
import shutil
from pathlib import Path

# FFmpeg will be installed in the user's home directory
FFMPEG_BASE_PATH = os.path.join(str(Path.home()), "ffmpeg")
FFMPEG_PATH = os.path.join(FFMPEG_BASE_PATH, "bin", "ffmpeg.exe")
FFPROBE_PATH = os.path.join(FFMPEG_BASE_PATH, "bin", "ffprobe.exe")

def download_and_install_ffmpeg():
    """Download and install FFmpeg automatically"""
    print("\nDownloading FFmpeg... This may take a few minutes.")
    
    # Create temporary directory for download
    temp_dir = os.path.join(os.getenv('TEMP'), 'ffmpeg_download')
    os.makedirs(temp_dir, exist_ok=True)
    zip_path = os.path.join(temp_dir, 'ffmpeg.zip')
    
    # Download FFmpeg
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    try:
        urllib.request.urlretrieve(url, zip_path)
    except Exception as e:
        print(f"Error downloading FFmpeg: {e}")
        return False
    
    print("Download complete. Installing FFmpeg...")
    
    try:
        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the extracted ffmpeg directory
        ffmpeg_extracted = None
        for item in os.listdir(temp_dir):
            if item.startswith('ffmpeg-master'):
                ffmpeg_extracted = os.path.join(temp_dir, item)
                break
        
        if ffmpeg_extracted:
            # Remove existing installation if any
            if os.path.exists(FFMPEG_BASE_PATH):
                shutil.rmtree(FFMPEG_BASE_PATH)
            
            # Move to final location
            shutil.move(ffmpeg_extracted, FFMPEG_BASE_PATH)
            
            # Clean up
            shutil.rmtree(temp_dir)
            print(f"FFmpeg has been installed successfully to: {FFMPEG_BASE_PATH}")
            return True
    except Exception as e:
        print(f"Error installing FFmpeg: {e}")
        return False
    
    return False

def check_ffmpeg_installation():
    """Check if FFmpeg is properly configured and install if missing"""
    if not os.path.exists(FFMPEG_PATH) or not os.path.exists(FFPROBE_PATH):
        print("\nFFmpeg is not found. Starting automatic installation...")
        if download_and_install_ffmpeg():
            print("\nFFmpeg installation completed successfully!")
            return True
        else:
            print("\nAutomatic installation failed. Please install FFmpeg manually:")
            print("\n1. Download FFmpeg:")
            print("   - Go to: https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip")
            
            response = input("\nWould you like to open the download page now? (y/n): ")
            if response.lower() == 'y':
                webbrowser.open('https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip')
            
            print("\n2. After downloading:")
            print("   - Extract the ZIP file to a folder on your computer")
            print(f"   - Move the extracted contents to: {FFMPEG_BASE_PATH}")
            sys.exit(1)
    return True

def get_duration(input_file):
    """Get the duration of the audio file using ffprobe"""
    cmd = [FFPROBE_PATH, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return float(output)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error getting duration: {e.output.decode()}")

def split_audio_file(input_file, max_size_mb=19):
    """Split an audio file into chunks of maximum specified size in MB"""
    # First check if FFmpeg is properly configured
    if not check_ffmpeg_installation():
        return
    
    if not os.path.exists(input_file):
        print(f"\nError: The file '{input_file}' does not exist.")
        print("Please make sure the audio file is in the same directory as this script.")
        return
    
    # Get file size and calculate number of parts needed
    file_size = os.path.getsize(input_file)
    num_parts = math.ceil(file_size / (max_size_mb * 1024 * 1024))
    
    if num_parts == 1:
        print(f"\nThe file is already smaller than {max_size_mb}MB.")
        return
    
    print(f"\nOriginal file size: {file_size / (1024*1024):.2f} MB")
    print(f"Splitting into {num_parts} parts of approximately {max_size_mb} MB each...")
    
    try:
        # Get duration of the audio file
        duration = get_duration(input_file)
        
        # Calculate segment duration
        segment_duration = duration / num_parts
        
        base_name, extension = os.path.splitext(input_file)
        
        for i in range(num_parts):
            start_time = i * segment_duration
            output_file = f"{base_name}_part{i+1}{extension}"
            
            # Use ffmpeg to split the file
            cmd = [
                FFMPEG_PATH,
                '-i', input_file,
                '-ss', str(start_time),
                '-t', str(segment_duration),
                '-c', 'copy',  # Copy without re-encoding
                '-y',  # Overwrite output files
                output_file
            ]
            
            print(f"\nCreating part {i+1} of {num_parts}...")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                print(f"Warning: Error while creating {output_file}")
                print(f"Error message: {result.stderr.decode()}")
            else:
                size_mb = os.path.getsize(output_file) / (1024*1024)
                print(f"Created {output_file} ({size_mb:.2f} MB)")
            
            # Verify the output file size
            if os.path.exists(output_file) and os.path.getsize(output_file) > max_size_mb * 1024 * 1024:
                print(f"Warning: {output_file} is larger than {max_size_mb}MB")
    
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        return
    
    print("\nFile splitting completed successfully!")
    print("You can now find the split files in the same directory as your original file.")

def main():
    # Check if file name is provided as command line argument
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # List all audio files in current directory
        audio_files = [f for f in os.listdir('.') if f.lower().endswith(('.m4a', '.mp3', '.wav'))]
        
        if not audio_files:
            print("\nNo audio files found in the current directory.")
            print("Please place an audio file in the same directory as this script.")
            return
        
        if len(audio_files) == 1:
            input_file = audio_files[0]
        else:
            print("\nAvailable audio files:")
            for i, file in enumerate(audio_files, 1):
                print(f"{i}. {file}")
            
            try:
                choice = int(input("\nEnter the number of the file you want to split: "))
                input_file = audio_files[choice - 1]
            except (ValueError, IndexError):
                print("Invalid choice. Please run the script again and select a valid number.")
                return
    
    # Ask for maximum size if not the default
    try:
        size_input = input("\nEnter maximum size in MB for each part (press Enter for default 19MB): ").strip()
        max_size_mb = float(size_input) if size_input else 19
    except ValueError:
        print("Invalid size entered. Using default 19MB.")
        max_size_mb = 19
    
    split_audio_file(input_file, max_size_mb)

if __name__ == "__main__":
    print("\nAudio File Splitter")
    print("==================")
    main()
