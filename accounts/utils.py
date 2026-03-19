import config.firebase  # Ensures Firebase app is initialized before first use
from firebase_admin import messaging


def send_push_notification(user, title, body):

    if not user.fcm_token:
        return

    try:
        message = messaging.Message(

            notification=messaging.Notification(
                title=title,
                body=body
            ),

            token=user.fcm_token
        )

        messaging.send(message)

    except Exception as e:
        # Log the error but don't crash the calling view
        print(f"[FCM] Failed to send push notification to {user.email}: {e}")