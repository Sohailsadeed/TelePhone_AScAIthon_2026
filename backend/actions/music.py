import threading
import os

from playsound import playsound


_music_lock = threading.Lock()
_music_thread = None
_stop_event = threading.Event()


def _play_sound_file(sound_path):
    try:
        if not os.path.exists(sound_path):
            print("Sound file not found")
            return

        playsound(sound_path)
    except Exception as e:
        print(f"Error playing sound: {e}")


def play_ambient_music():
    global _music_thread

    try:
        sound_path = os.path.join("sounds", "ambient.mp3")
        if not os.path.exists(sound_path):
            print("Sound file not found")
            return

        with _music_lock:
            _stop_event.clear()
            _music_thread = threading.Thread(
                target=_play_sound_file,
                args=(sound_path,),
                daemon=True,
            )
            _music_thread.start()

        print("Music started")
    except Exception as e:
        print(f"Error starting music: {e}")


def stop_music():
    global _music_thread

    try:
        with _music_lock:
            _stop_event.set()
            _music_thread = None

        print("Music stopped")
    except Exception as e:
        print(f"Error stopping music: {e}")


def play_alert_sound():
    try:
        sound_path = os.path.join("sounds", "alert.mp3")
        if not os.path.exists(sound_path):
            print("Sound file not found")
            return

        playsound(sound_path)
        print("Alert sound played")
    except Exception as e:
        print(f"Error playing alert sound: {e}")
