from plyer import notification


def _send_notification(title, message, timeout, success_name):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="FocusLens",
            timeout=timeout,
        )
        print(success_name)
    except Exception as e:
        print(f"Error in {success_name}: {e}")


def send_focus_alert():
    _send_notification(
        title="FocusLens Alert",
        message="Phone detected! Stay focused!",
        timeout=5,
        success_name="send_focus_alert",
    )


def send_welcome_back():
    _send_notification(
        title="FocusLens",
        message="Welcome back! Session resumed.",
        timeout=5,
        success_name="send_welcome_back",
    )


def send_break_suggestion():
    _send_notification(
        title="FocusLens",
        message="You look tired. Take a 5 min break!",
        timeout=5,
        success_name="send_break_suggestion",
    )


def send_stranger_alert():
    _send_notification(
        title="FocusLens Security",
        message="Unknown person detected at your desk!",
        timeout=10,
        success_name="send_stranger_alert",
    )
