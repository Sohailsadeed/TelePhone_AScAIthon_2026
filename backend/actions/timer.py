import time
import datetime
import threading


_timer_lock = threading.Lock()
_timer_start_time = None
_timer_stop_event = None
_timer_thread = None


def _timer_worker(stop_event):
    try:
        while not stop_event.is_set():
            time.sleep(1)
    except Exception as e:
        print(f"Error in timer thread: {e}")


def start_timer():
    global _timer_start_time, _timer_stop_event, _timer_thread

    try:
        with _timer_lock:
            _timer_start_time = datetime.datetime.now()
            _timer_stop_event = threading.Event()
            _timer_thread = threading.Thread(
                target=_timer_worker,
                args=(_timer_stop_event,),
                daemon=True,
            )
            _timer_thread.start()
        print("Timer started")
    except Exception as e:
        print(f"Error starting timer: {e}")


def stop_timer():
    global _timer_start_time, _timer_stop_event, _timer_thread

    try:
        with _timer_lock:
            if _timer_start_time is None:
                print("Timer stopped")
                return 0.0

            end_time = datetime.datetime.now()
            duration = (end_time - _timer_start_time).total_seconds() / 60.0

            if _timer_stop_event is not None:
                _timer_stop_event.set()

            _timer_start_time = None
            _timer_stop_event = None
            _timer_thread = None

        print("Timer stopped")
        return duration
    except Exception as e:
        print(f"Error stopping timer: {e}")
        return 0.0


def get_elapsed_time():
    try:
        with _timer_lock:
            if _timer_start_time is None:
                return "00:00"

            elapsed_seconds = int((datetime.datetime.now() - _timer_start_time).total_seconds())

        minutes, seconds = divmod(elapsed_seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"
    except Exception as e:
        print(f"Error getting elapsed time: {e}")
        return "00:00"
