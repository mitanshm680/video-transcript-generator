# Video to Transcript Converter

This project provides a Python script to extract audio from a video file, split the audio into manageable chunks, and transcribe the chunks to text with timestamps. The resulting transcript is saved to a text file.

## Requirements

- `moviepy` - for extracting audio from video files.
- `pydub` - for audio file manipulation.
- `speech_recognition` - for transcribing audio to text.
- `tqdm` - for showing progress bars during transcription.

You can install the required packages using pip:

```bash
pip install moviepy pydub SpeechRecognition tqdm
```

## Script Overview

### Functions

1. **`extract_audio_from_video(video_path, audio_path)`**: Extracts audio from the specified video file and saves it as a WAV file.

2. **`split_audio(audio_path, chunk_length_ms=30000)`**: Splits the audio file into chunks of a specified length (default is 30 seconds).

3. **`transcribe_chunk(chunk, start_time, end_time, chunk_index)`**: Transcribes an audio chunk using Google Speech Recognition and includes timestamps.

4. **`audio_chunks_to_text(chunks)`**: Transcribes a list of audio chunks in parallel and collects the results.

5. **`save_transcript_with_timestamps(transcript, file_path)`**: Saves the transcription results with timestamps to a file.

6. **`video_to_transcript(video_path, audio_path, transcript_path)`**: Orchestrates the process of extracting audio, splitting it, transcribing, and saving the transcript.

### How to Use

1. **Set File Paths**: Update the `video_path`, `audio_path`, and `transcript_path` variables with your file paths.

    ```python
    video_path = "file.mp4"
    audio_path = "extracted_audio.wav"
    transcript_path = "transcript_with_timestamps.txt"
    ```

2. **Run the Script**: Execute the script to process the video file and generate the transcript.

    ```bash
    python main.py
    ```

### Example

For a video file named `example_video.mp4`, the audio will be extracted to `extracted_audio.wav`, and the transcript will be saved to `transcript_with_timestamps.txt`.