import subprocess
import os
import datetime

from plyer import notification
from PIL import Image
import numpy as np


def lock_screen():
    try:
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
        print("Screen locked")
    except Exception as e:
        print(f"Error locking screen: {e}")


def send_notification(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="FocusLens",
            timeout=5,
        )
        print("Notification sent")
    except Exception as e:
        print(f"Error sending notification: {e}")


def save_screenshot(frame):
    try:
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(screenshots_dir, filename)

        image = Image.fromarray(np.asarray(frame))
        image.save(filepath)

        print("Screenshot saved")
    except Exception as e:
        print(f"Error saving screenshot: {e}")
