from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import speech_recognition as sr
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

def extract_audio_from_video(video_path, audio_path):
    """
    Extract audio from a video file and save it as a WAV file.

    Args:
        video_path (str): Path to the input video file.
        audio_path (str): Path where the extracted audio will be saved.
    """
    video = VideoFileClip(video_path)  # Load the video file
    video.audio.write_audiofile(audio_path)  # Extract and save the audio as a WAV file

def split_audio(audio_path, chunk_length_ms=30000):
    """
    Split an audio file into chunks of a specified length.

    Args:
        audio_path (str): Path to the input audio file.
        chunk_length_ms (int): Length of each audio chunk in milliseconds (default is 30 seconds).

    Returns:
        list: A list of tuples containing the audio chunk and its start and end times.
    """
    audio = AudioSegment.from_wav(audio_path)  # Load the audio file
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]  # Extract a chunk of the specified length
        chunks.append((chunk, i / 1000.0, (i + chunk_length_ms) / 1000.0))  # Append chunk and its times
    return chunks

def transcribe_chunk(chunk, start_time, end_time, chunk_index):
    """
    Transcribe a chunk of audio to text using Google Speech Recognition.

    Args:
        chunk (AudioSegment): The audio chunk to transcribe.
        start_time (float): The start time of the chunk in seconds.
        end_time (float): The end time of the chunk in seconds.
        chunk_index (int): Index of the chunk.

    Returns:
        str: Transcription result with timestamps.
    """
    recognizer = sr.Recognizer()  # Initialize the speech recognizer
    chunk_path = f"chunk_{chunk_index}.wav"  # Path to save the audio chunk

    # Export the audio chunk to a temporary WAV file
    chunk.export(chunk_path, format="wav")

    with sr.AudioFile(chunk_path) as source:
        audio_data = recognizer.record(source)  # Read the audio data from the file

    try:
        # Perform speech recognition and return the result with timestamps
        text = recognizer.recognize_google(audio_data)
        return f"{start_time:.2f}s - {end_time:.2f}s: {text}"
    except sr.UnknownValueError:
        # Handle cases where speech is unintelligible
        return f"{start_time:.2f}s - {end_time:.2f}s: [unintelligible]"
    except sr.RequestError:
        # Handle request errors
        return f"{start_time:.2f}s - {end_time:.2f}s: [error]"
    finally:
        os.remove(chunk_path)  # Clean up the temporary chunk file

def audio_chunks_to_text(chunks):
    """
    Transcribe a list of audio chunks to text using parallel processing.

    Args:
        chunks (list): List of tuples containing audio chunks and their start and end times.

    Returns:
        list: Transcription results with timestamps for each chunk.
    """
    transcript = []

    # Use ThreadPoolExecutor to transcribe chunks in parallel
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(transcribe_chunk, chunk, start, end, i): i for i, (chunk, start, end) in enumerate(chunks)}

        # Process the results as they become available
        for future in tqdm(as_completed(futures), total=len(futures), desc="Transcribing"):
            chunk_index = futures[future]
            try:
                result = future.result()  # Get the result of transcription
                transcript.append(result)  # Append the result to the transcript list
            except Exception as exc:
                transcript.append(f"Chunk {chunk_index} generated an exception: {exc}")

    return transcript

def save_transcript_with_timestamps(transcript, file_path):
    """
    Save the transcribed text with timestamps to a file.

    Args:
        transcript (list): List of transcription results with timestamps.
        file_path (str): Path to the output file where the transcript will be saved.
    """
    with open(file_path, 'w') as file:
        for line in transcript:
            file.write(line + '\n')  # Write each line of the transcript to the file

def video_to_transcript(video_path, audio_path, transcript_path):
    """
    Convert a video file to a transcript with timestamps.

    Args:
        video_path (str): Path to the input video file.
        audio_path (str): Path where the extracted audio will be saved.
        transcript_path (str): Path to save the final transcript with timestamps.
    """
    start_time = time.time()  # Record the start time
    print("Extracting audio from video...")
    extract_audio_from_video(video_path, audio_path)  # Extract audio from video
    print("Audio extraction complete.")
    
    print("Splitting audio into chunks...")
    audio_chunks = split_audio(audio_path)  # Split the audio into chunks
    print(f"Audio split into {len(audio_chunks)} chunks.")
    
    print("Transcribing audio chunks...")
    transcript = audio_chunks_to_text(audio_chunks)  # Transcribe the audio chunks
    
    print("Saving transcript to file...")
    save_transcript_with_timestamps(transcript, transcript_path)  # Save the transcript with timestamps
    
    end_time = time.time()  # Record the end time
    print(f"Transcription complete. Total time taken: {end_time - start_time:.2f} seconds")

# Define file paths
video_path = "example_video.mp4"
audio_path = "extracted_audio.wav"
transcript_path = "transcript_with_timestamps.txt"

# Run the transcription process
video_to_transcript(video_path, audio_path, transcript_path)
