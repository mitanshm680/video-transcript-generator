from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import speech_recognition as sr
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

def extract_audio_from_video(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def split_audio(audio_path, chunk_length_ms=30000):
    audio = AudioSegment.from_wav(audio_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]
        chunks.append((chunk, i / 1000.0, (i + chunk_length_ms) / 1000.0))
    return chunks

def transcribe_chunk(chunk, start_time, end_time, chunk_index):
    recognizer = sr.Recognizer()
    chunk_path = f"chunk_{chunk_index}.wav"
    chunk.export(chunk_path, format="wav")

    with sr.AudioFile(chunk_path) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        return f"{start_time:.2f}s - {end_time:.2f}s: {text}"
    except sr.UnknownValueError:
        return f"{start_time:.2f}s - {end_time:.2f}s: [unintelligible]"
    except sr.RequestError:
        return f"{start_time:.2f}s - {end_time:.2f}s: [error]"
    finally:
        os.remove(chunk_path)  # Clean up temporary chunk file

def audio_chunks_to_text(chunks):
    transcript = []

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(transcribe_chunk, chunk, start, end, i): i for i, (chunk, start, end) in enumerate(chunks)}

        for future in tqdm(as_completed(futures), total=len(futures), desc="Transcribing"):
            chunk_index = futures[future]
            try:
                result = future.result()
                transcript.append(result)
            except Exception as exc:
                transcript.append(f"Chunk {chunk_index} generated an exception: {exc}")

    return transcript

def save_transcript_with_timestamps(transcript, file_path):
    with open(file_path, 'w') as file:
        for line in transcript:
            file.write(line + '\n')

def video_to_transcript(video_path, audio_path, transcript_path):
    start_time = time.time()
    print("Extracting audio from video...")
    extract_audio_from_video(video_path, audio_path)
    print("Audio extraction complete.")
    
    print("Splitting audio into chunks...")
    audio_chunks = split_audio(audio_path)
    print(f"Audio split into {len(audio_chunks)} chunks.")
    
    print("Transcribing audio chunks...")
    transcript = audio_chunks_to_text(audio_chunks)
    
    print("Saving transcript to file...")
    save_transcript_with_timestamps(transcript, transcript_path)
    
    end_time = time.time()
    print(f"Transcription complete. Total time taken: {end_time - start_time:.2f} seconds")

video_path = "file.mp4"
audio_path = "extracted_audio.wav"
transcript_path = "transcript_with_timestamps.txt"

video_to_transcript(video_path, audio_path, transcript_path)
