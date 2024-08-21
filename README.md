# MP3 Splitter

This Python script allows you to split large MP3 files into smaller chunks of a specified maximum size. It uses FFmpeg for audio processing and can automatically download FFmpeg if it's not already installed on your system.

## Features

- Split MP3 files into smaller chunks
- Automatically download FFmpeg if not present
- Specify maximum chunk size in MB
- Output chunks to a designated folder

## Requirements

- Python 3.6+
- ffmpeg-python library

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/artsnoob/mp3splitter.git
   cd mp3-splitter
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Place your MP3 file in the same directory as the script.

2. Run the script:
   ```
   python mp3_splitter.py
   ```

   By default, the script will look for a file named `videns.mp3` and split it into 2MB chunks.

3. To use a different file or chunk size, modify the following lines in the script:
   ```python
   input_file = "your_file_name.mp3"
   split_mp3(input_file, max_size_mb=your_desired_size)
   ```

4. The split MP3 chunks will be saved in an `output` folder in the same directory.

## How it Works

1. The script first checks if FFmpeg is installed. If not, it downloads and sets up FFmpeg automatically.
2. It then calculates the duration of each chunk based on the desired maximum size.
3. Using FFmpeg, it splits the input MP3 file into chunks of the calculated duration.
4. The resulting chunks are saved in the output folder.

## Note

This script is designed for Windows systems. For other operating systems, you may need to modify the FFmpeg download URL and path setup.
