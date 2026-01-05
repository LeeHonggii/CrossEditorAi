import os
import subprocess

def trim_videos():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    backup_dir = os.path.join(base_dir, 'data_backup')
    ffmpeg_path = "/Users/lee-hong-gi/anaconda3/envs/pose/bin/ffmpeg"

    if not os.path.exists(backup_dir):
        print("Backup directory not found, cannot restore source files.")
        return

    # Get list of video files from backup directory
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov']
    files = [f for f in os.listdir(backup_dir) if os.path.splitext(f)[1].lower() in video_extensions]

    for file in files:
        backup_path = os.path.join(backup_dir, file)
        target_path = os.path.join(data_dir, file)

        print(f"Trimming {file} to 30 seconds using ffmpeg...")
        cmd = [
            ffmpeg_path,
            "-y", # Overwrite output
            "-i", backup_path,
            "-t", "30",
            "-c:v", "copy",
            "-c:a", "copy",
            target_path
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Successfully trimmed {file}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to trim {file}: {e.stderr.decode()}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    trim_videos()
