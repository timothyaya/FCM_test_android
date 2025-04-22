import time
import requests
from plyer import vibrator, notification
from jnius import autoclass, cast
from pushyy import RemoteMessage, process_background_messages


def start_foreground():
    PythonService = autoclass('org.kivy.android.PythonService')
    Context = autoclass('android.content.Context')
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    NotificationManager = autoclass('android.app.NotificationManager')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    Build = autoclass('android.os.Build')
    Build.VERSION = autoclass('android.os.Build$VERSION')
    Build.VERSION_CODES = autoclass('android.os.Build$VERSION_CODES')
    String = autoclass('java.lang.String')

    service = PythonService.mService
    app_context = service.getApplicationContext()

    channel_id = String('my_channel')
    channel_name = String('ESP Notifier')
    notification_id = 1

    if Build.VERSION.SDK_INT >= Build.VERSION_CODES.O:
        channel = NotificationChannel(channel_id, channel_name, NotificationManager.IMPORTANCE_DEFAULT)
        manager = cast(NotificationManager, app_context.getSystemService(Context.NOTIFICATION_SERVICE))
        manager.createNotificationChannel(channel)
        builder = NotificationBuilder(app_context, channel_id)
    else:
        builder = NotificationBuilder(app_context)

    builder.setContentTitle(String('ESP listening'))
    builder.setContentText(String('waiting for ESP8266...'))
    icon = app_context.getApplicationInfo().icon
    builder.setSmallIcon(icon)

    notification = builder.build()
    service.startForeground(notification_id, notification)


def my_background_callback(data: RemoteMessage) -> None:
    # ..your code goes here..
    """
    One of the things you can do here: Mark a chat message
    as delivered by making a request to your server
    """
    # print(data)
    try:
        print(data)
        # requests.post("http://192.168.0.171:5000/ac", json = data)
    except Exception as e:
        print(f'error : {e}')
        #pass

if __name__ == '__main__':
    print('service started')
    start_foreground()
    #while True:
    for _ in range(3):
        try:
            process_background_messages(my_background_callback)
            RingtoneManager = autoclass('android.media.RingtoneManager')
            PythonService = autoclass('org.kivy.android.PythonService')
            # Context = autoclass('android.content.Context')
            service = PythonService.mService
            context = service.getApplicationContext()
            uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
            ringtone = RingtoneManager.getRingtone(context, uri)
            ringtone.play()

            break
        except Exception as e:
            # Meh, run the loop again xD
            print(e)
        time.sleep(0.6)

