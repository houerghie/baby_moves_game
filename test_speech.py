import pyttsx3
import time

def list_available_voices():
    """List all available voices on the system."""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if voices:
            print("Available voices:")
            for i, voice in enumerate(voices):
                print(f"{i}: {voice.name} (ID: {voice.id})")
                if hasattr(voice, 'languages'):
                    print(f"    Languages: {voice.languages}")
        else:
            print("No voices found")
        del engine
    except Exception as e:
        print(f"Error listing voices: {e}")

def test_speech():
    # List of words/phrases for babies
    baby_words = [
        "Hello baby!",
        "Let's play a game!",
        "Move your hands up!",
        "Wave hello!",
        "Clap your hands!",
        "Touch your nose!",
        "Great job!",
        "Well done!",
        "Try again!",
        "You're amazing!"
    ]
    
    print("Testing text-to-speech with baby-friendly words...")
    print("Speaking each phrase with a pause between them:\n")
    
    for i, phrase in enumerate(baby_words, 1):
        print(f"{i}. Speaking: '{phrase}'")
        
        # Create a fresh engine instance for each phrase
        engine = pyttsx3.init()
        
        # Configure speech properties
        engine.setProperty('rate', 150)  # Slower rate for babies
        engine.setProperty('volume', 1.0)  # Max volume
        
        # Get available voices
        voices = engine.getProperty('voices')
        if voices:
            # Try to use a female voice (often better for babies)
            for voice in voices:
                if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            else:
                # Use first available voice
                engine.setProperty('voice', voices[1].id)
        
        engine.say(phrase)
        engine.runAndWait()
        
        # Clean up the engine
        del engine
        # time.sleep(1)  # Pause between phrases
    
    print("\nSpeech test completed!")

if __name__ == "__main__":
    try:
        print("=== Available Voices ===")
        list_available_voices()
        print("\n=== Testing Speech ===")
        test_speech()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have installed pyttsx3: pip install pyttsx3")