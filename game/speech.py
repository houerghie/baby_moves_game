import pyttsx3
import threading

def _speak_text(text: str):
    """Simple function that speaks text using a fresh engine."""
    if not text:
        return
        
    try:
        # Create fresh engine for each speech
        engine = pyttsx3.init()
        
        # Configure speech properties for babies
        engine.setProperty('rate', 140)  # Slower rate for babies
        engine.setProperty('volume', 1.0)  # Max volume
        
        # Try to find English voice specifically
        voices = engine.getProperty('voices')
        if voices:
            # Look for English voices first
            for voice in voices:
                if 'english' in voice.name.lower() or 'en-' in voice.id.lower() or 'en_' in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
            else:
                # If no English found, try for female voice
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use second available voice as fallback (often better than first)
                    if len(voices) > 1:
                        engine.setProperty('voice', voices[1].id)
        
        print(f"Speaking: {text}")
        engine.say(text)
        engine.runAndWait()
        print(f"Finished speaking: {text}")

        # Clean up
        del engine
    except Exception as e:
        print(f"Speech error: {e}")

def speak_instruction(move: str, friendly_label: str):
    """Speak an instruction for a specific move in a separate thread."""
    # Create baby-friendly instruction
    instruction = _create_instruction(move, friendly_label)
    
    def _speak_in_thread():
        _speak_text(instruction)
    
    # Create and start thread that will be destroyed when done
    thread = threading.Thread(target=_speak_in_thread, daemon=True)
    thread.start()

def speak_feedback(message: str):
    """Speak feedback message in a separate thread."""
    def _speak_in_thread():
        _speak_text(message)
    
    # Create and start thread that will be destroyed when done
    thread = threading.Thread(target=_speak_in_thread, daemon=True)
    thread.start()

def _create_instruction(move: str, friendly_label: str) -> str:
    """Create a baby-friendly instruction from the move and label."""
    # Remove emojis for speech
    clean_label = friendly_label
    for emoji in ['🙌', '👏', '👋', '🦘', '👍', '👎', '✋']:
        clean_label = clean_label.replace(emoji, '')
    clean_label = clean_label.strip()
    
    # Add encouraging prefix
    prefixes = [
        "Let's try this! ",
        "Can you do this? ",
        "Your turn! ",
        "Show me how you can "
    ]
    
    import random
    prefix = random.choice(prefixes)
    
    return prefix + clean_label.lower()