"""
Audio processing utilities for the meeting recorder application.
"""

import os
import tempfile
import wave
from typing import List

def get_audio_duration(audio_file: str) -> float:
    """Get the duration of an audio file in seconds."""
    try:
        with wave.open(audio_file, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)
            return duration
    except Exception as e:
        print(f"Error getting audio duration: {str(e)}")
        return 0

def split_audio_file(audio_file: str, max_duration: int = 600) -> List[str]:
    """
    Split a large audio file into smaller chunks of specified maximum duration.
    
    Args:
        audio_file: Path to the audio file to split
        max_duration: Maximum duration of each chunk in seconds (default: 10 minutes)
        
    Returns:
        List of paths to the split audio files
    """
    # Check if audio_file is None or doesn't exist
    if audio_file is None or not os.path.exists(audio_file):
        print(f"Audio file is None or doesn't exist: {audio_file}")
        return []
    
    try:
        duration = get_audio_duration(audio_file)
        
        # If the audio is shorter than the max duration, return the original file
        if duration <= max_duration:
            return [audio_file]
        
        # Calculate number of chunks needed
        num_chunks = int(duration / max_duration) + 1
        chunk_files = []
        
        # Get audio properties
        with wave.open(audio_file, 'rb') as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            framerate = wf.getframerate()
            
        # Create a directory for the chunks if it doesn't exist
        temp_dir = tempfile.mkdtemp()
        
        # Split the audio file using wave module
        for i in range(num_chunks):
            start_time = i * max_duration
            end_time = min((i + 1) * max_duration, duration)
            chunk_duration = end_time - start_time
            
            # Create a temporary file for this chunk
            chunk_file = os.path.join(temp_dir, f"chunk_{i}.wav")
            chunk_files.append(chunk_file)
            
            # Use wave module to extract the chunk
            with wave.open(audio_file, 'rb') as wf:
                # Skip to the start position
                wf.setpos(int(start_time * framerate))
                
                # Read the chunk data
                chunk_frames = int(chunk_duration * framerate)
                chunk_data = wf.readframes(chunk_frames)
                
                # Write the chunk to a new file
                with wave.open(chunk_file, 'wb') as chunk_wf:
                    chunk_wf.setnchannels(channels)
                    chunk_wf.setsampwidth(sample_width)
                    chunk_wf.setframerate(framerate)
                    chunk_wf.writeframes(chunk_data)
        
        return chunk_files
    except Exception as e:
        print(f"Error splitting audio file: {str(e)}")
        # Return the original file if there's an error
        return [audio_file] if audio_file else []

def combine_transcriptions(transcriptions: List[str]) -> str:
    """
    Combine multiple transcription segments into a single coherent text.
    
    Args:
        transcriptions: List of transcription segments
        
    Returns:
        Combined transcription text
    """
    # Simple concatenation with newlines between segments
    return "\n".join(transcriptions)
