import speech_recognition as sr
import time

def test_microphone():
    """Test if microphone is working."""
    r = sr.Recognizer()
    
    print("Testing microphone access...")
    try:
        # Test microphone access
        with sr.Microphone() as source:
            print("✓ Microphone detected!")
            print("Adjusting for ambient noise...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("✓ Ambient noise adjustment complete")
        return True
    except Exception as e:
        print(f"✗ Microphone error: {e}")
        return False

def test_baby_words():
    """Test speech recognition with simple baby words."""
    if not test_microphone():
        return
    
    r = sr.Recognizer()
    
    # Baby-friendly words to test
    test_words = [
        "mama", "dada", "hi", "bye", "yes", "no", 
        "cat", "dog", "ball", "milk", "up", "go"
    ]
    
    print(f"\n=== Baby Words Speech Test ===")
    print(f"We'll test {len(test_words)} baby-friendly words.")
    print("For each word, you'll hear the word, then have 3 seconds to say it.")
    print("The system will try to recognize what you said.\n")
    
    results = []
    
    for i, word in enumerate(test_words, 1):
        print(f"\n--- Test {i}/{len(test_words)} ---")
        print(f"Target word: '{word.upper()}'")
        
        # Give user time to prepare
        print("Get ready... (2 seconds)")
        time.sleep(2)
        
        try:
            with sr.Microphone() as source:
                print(f"🎤 Say '{word}' now! (3 seconds)")
                # Listen for 3 seconds
                audio = r.listen(source, timeout=1, phrase_time_limit=3)
                
            print("Processing speech...")
            
            # Use Google's free speech recognition
            recognized = r.recognize_google(audio).lower().strip()
            
            print(f"You said: '{recognized}'")
            
            # Check if the word matches (flexible matching)
            is_correct = word.lower() in recognized or recognized in word.lower()
            
            if is_correct:
                print("✅ CORRECT! Good job!")
            else:
                print("❌ Not quite right, but that's okay!")
                
            results.append({
                'target': word,
                'recognized': recognized,
                'correct': is_correct
            })
                
        except sr.WaitTimeoutError:
            print("⏰ No speech detected - that's okay, try speaking louder next time!")
            results.append({
                'target': word,
                'recognized': '(no speech)',
                'correct': False
            })
            
        except sr.UnknownValueError:
            print("🤔 Couldn't understand the speech - try speaking clearer!")
            results.append({
                'target': word,
                'recognized': '(unclear)',
                'correct': False
            })
            
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            results.append({
                'target': word,
                'recognized': f'(error: {e})',
                'correct': False
            })
        
        # Brief pause between words
        time.sleep(1)
    
    # Show results summary
    print(f"\n=== Test Results ===")
    correct_count = sum(1 for r in results if r['correct'])
    total_count = len(results)
    
    print(f"Accuracy: {correct_count}/{total_count} ({correct_count/total_count*100:.1f}%)")
    
    print("\nDetailed results:")
    for r in results:
        status = "✅" if r['correct'] else "❌"
        print(f"{status} '{r['target']}' → '{r['recognized']}'")
    
    if correct_count >= total_count * 0.7:
        print("\n🎉 Great! Speech recognition is working well for baby words!")
    elif correct_count >= total_count * 0.5:
        print("\n👍 Good! Speech recognition is working reasonably well.")
    else:
        print("\n⚠️  Speech recognition might need adjustment. Try:")
        print("   - Speaking closer to the microphone")
        print("   - Speaking more clearly")
        print("   - Reducing background noise")

def quick_test():
    """Quick single-word test."""
    if not test_microphone():
        return
        
    r = sr.Recognizer()
    
    print("\n=== Quick Test ===")
    print("Say any word when prompted...")
    
    try:
        with sr.Microphone() as source:
            print("🎤 Say something! (5 seconds)")
            audio = r.listen(source, timeout=2, phrase_time_limit=5)
            
        print("Processing...")
        recognized = r.recognize_google(audio)
        print(f"You said: '{recognized}'")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Speech Recognition Test for Baby Moves Game")
    print("==========================================")
    
    while True:
        print("\nChoose a test:")
        print("1. Quick test (say any word)")
        print("2. Full baby words test (12 words)")
        print("3. Microphone test only")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            quick_test()
        elif choice == "2":
            test_baby_words()
        elif choice == "3":
            test_microphone()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")