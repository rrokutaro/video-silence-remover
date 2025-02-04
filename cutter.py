import argparse
import numpy as np
import librosa
import json
import os
import tempfile
from moviepy.editor import VideoFileClip

def extract_audio(video):
    """
    Safely extract audio from video clip for moviepy 1.0.3
    """
    temp_dir = tempfile.gettempdir()
    temp_audio_path = os.path.join(temp_dir, 'temp_audio.wav')
    
    video.audio.write_audiofile(temp_audio_path, fps=44100, verbose=False, logger=None)
    audio_array, sample_rate = librosa.load(temp_audio_path, sr=None)
    
    try:
        os.remove(temp_audio_path)
    except:
        pass
        
    return audio_array, sample_rate

def detect_silent_parts(audio_array, sample_rate, silence_threshold_db=-10, min_silence_duration=1, buffer_duration=0.5):
    """
    Detect silent parts in audio with buffer zones.
    """
    if len(audio_array.shape) > 1:
        audio_array = audio_array.mean(axis=1)
    
    eps = np.finfo(float).eps
    db = librosa.amplitude_to_db(np.abs(audio_array) + eps, ref=np.max)
    
    non_silent = db > silence_threshold_db
    
    buffer_samples = int(buffer_duration * sample_rate)
    min_silence_samples = int(min_silence_duration * sample_rate)
    
    buffered = np.copy(non_silent)
    for i in range(1, buffer_samples + 1):
        shifted_right = np.pad(non_silent[:-i], (i, 0), mode='edge')
        shifted_left = np.pad(non_silent[i:], (0, i), mode='edge')
        buffered |= shifted_right
        buffered |= shifted_left
    
    changes = np.diff(buffered.astype(int))
    segment_starts = np.where(changes == 1)[0] + 1
    segment_ends = np.where(changes == -1)[0] + 1
    
    if buffered[0]:
        segment_starts = np.insert(segment_starts, 0, 0)
    if buffered[-1]:
        segment_ends = np.append(segment_ends, len(buffered))
    
    intervals = []
    for start, end in zip(segment_starts, segment_ends):
        duration = (end - start) / sample_rate
        if duration >= min_silence_duration:
            intervals.append({
                "start": round(start / sample_rate, 3),
                "end": round(end / sample_rate, 3),
                "duration": round(duration, 3)
            })
    
    return intervals

def detect_non_silent_segments(video_path, output_json, silence_threshold_db=-40, 
                             min_silence_duration=0.5, buffer_duration=0.2):
    """
    Analyze video and output non-silent segment information to JSON.
    """
    print("Loading video...")
    video = VideoFileClip(video_path, audio=True)
    original_duration = video.duration
    
    print("Extracting audio...")
    audio_array, sample_rate = extract_audio(video)
    
    print("Detecting non-silent intervals...")
    intervals = detect_silent_parts(
        audio_array, 
        sample_rate,
        silence_threshold_db=silence_threshold_db,
        min_silence_duration=min_silence_duration,
        buffer_duration=buffer_duration
    )
    
    if not intervals:
        print("No silent segments found with current parameters. Try adjusting the silence threshold.")
        video.close()
        return
    
    total_duration = sum(segment["duration"] for segment in intervals)
    removed_duration = original_duration - total_duration
    
    output_data = {
        "input_file": video_path,
        "original_duration": round(original_duration, 3),
        "new_duration": round(total_duration, 3),
        "removed_duration": round(removed_duration, 3),
        "number_of_segments": len(intervals),
        "segments": intervals,
        "parameters": {
            "silence_threshold_db": silence_threshold_db,
            "min_silence_duration": min_silence_duration,
            "buffer_duration": buffer_duration
        }
    }
    
    with open(output_json, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Found {len(intervals)} non-silent segments")
    print(f"Original duration: {original_duration:.2f}s")
    print(f"New duration: {total_duration:.2f}s")
    print(f"Removed: {removed_duration:.2f}s")
    print(f"Results written to: {output_json}")
    
    video.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect non-silent segments in a video and output JSON.")
    parser.add_argument("-i","--input", type=str, help="Path to the input video file.")
    parser.add_argument("-o", "--output", type=str, help="Path to save the output JSON file.")
    parser.add_argument("-t", "--threshold", type=float, default=-10, help="Silence threshold in dB (default: -10).")
    parser.add_argument("-m", "--min_silence", type=float, default=1, help="Minimum silence duration in seconds (default: 1).")
    parser.add_argument("-b", "--buffer", type=float, default=0.5, help="Buffer duration in seconds (default: 0.5).")

    args = parser.parse_args()
    
    detect_non_silent_segments(
        video_path=args.input,
        output_json=args.output,
        silence_threshold_db=args.threshold,
        min_silence_duration=args.min_silence,
        buffer_duration=args.buffer
    )
