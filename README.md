# FCM_test_android_kivy
firebase push notification for android
The attached file is based on the "fox520 pushyy" project, with some modifications and comments added.
the original link: https://github.com/Fox520/pushyy

the steps:
1. In the project directory, run:
   git clone https://github.com/kivy/python-for-android.git

2. Open the file:
  ./python-for-android/pythonforandroid/bootstraps/common/build/templates/build.tmpl.gradle, and make the following changes:
   
  2.1 Under the buildscript section in dependencies, add the following line after
   ```
   classpath 'com.android.tools.build:gradle:8.1.1 ->
   classpath 'com.google.gms:google-services:4.4.2' ← (You can find the latest version on the Firebase website)
   ```
  2.2 Find apply plugin: 'com.android.application' and add the following line directly below it:
   ```
   apply plugin: 'com.google.gms.google-services'
   ```
      
  2.3 At the bottom of the file, under the Dependencies: section, add:
   ```
   implementation platform('com.google.firebase:firebase-bom:33.1.2') ← (Get the latest version from Firebase)
   ```

3. Modify ./python-for-android/pythonforandroid/bootstraps/sdl2/build/templates/AndroidManifest.tmpl.xml
   Before the closing </Dependencies> tag, insert:
   ```
   <service
     android:name="org.kivy.plugins.messaging.KivyFirebaseMessagingBackgroundService"
     android:permission="android.permission.BIND_JOB_SERVICE"
     android:exported="false"/>
   <service android:name="org.kivy.plugins.messaging.KivyFirebaseMessagingService"
     android:exported="false">
     <intent-filter>
       <action android:name="com.google.firebase.MESSAGING_EVENT"/>
     </intent-filter>
   </service>
     <receiver
     android:name="org.kivy.plugins.messaging.KivyFirebaseMessagingReceiver"
     android:exported="true"
     android:permission="com.google.android.c2dm.permission.SEND">
     <intent-filter>
       <action android:name="com.google.android.c2dm.intent.RECEIVE" />
     </intent-filter>
   </receiver>
   ```
4. In Firebase FCM, create a project, add an Android app, and obtain the google-services.json file.  Place this file in the directory:
   ```
   ./python-for-android/pythonforandroid/bootstraps/common/build
   ```
5. Go to: https://github.com/Fox520/pushyy
   
  5.1 Download the entire src/python/pushyy directory into your project directory.
  
  5.2 Download src/python/python_notification_handler.py into your project directory, and modify it to add foreground support (the code will be provided later).
      after testing, don't need this file
  
  5.3 Download src/python/python/libs into your project directory, and modify the following:
  
   In libs/PlatformIntermediate.java: Mark the service section as a comment 
   
   ~~update the package name and the service name to match the value of services = Myservice:python_notification_handler.py in 
      buildozer.spec. In this case the value is Myservice~~
      

   ```
   public static void addbackroundMessage(Map<String, Object> remoteMessageMap, Context context) {
   //try {
   // com.test.testapp.ServiceMyservice.start(org.kivy.android.PythonActivity.mActivity, "");
   //} catch (Exception e) {
   //    Log.d("PlatformIntermediate", "Exception occurred while trying to start service: " + e.getMessage());
   //}
   ```

   In libs/KivyFirebaseMessagingBackgroundExecutor.java: 
   
   Mark the service section as a comment
   
   ~~update the package name and service name similarly.~~
   
   ```
   private static AtomicBoolean started = new AtomicBoolean(false);
        public static void startBackgroundPythonService() {
        Log.d("BackgroundExecutor", "Starting background service");
        //com.test.testapp.ServiceMyservice.start(ContextHolder.getApplicationContext(), "");
        Log.d("BackgroundExecutor", "Background service started");
   ```
      
   In libs/KivyFirebaseMessagingReceiver.java:
   
   Change
   ```
        Log.d("BTW, title is " + remoteMessage.getNotification().getTitle());
        Log.d("BTW", "title is " + remoteMessage.getNotification().getTitle());
        (The original author made a typo—Log.d requires two arguments)
   ```
6. Modify buildozer.spec:
   
   Ensure that the domain name and package name match the values used in your Firebase project.
   
   6.2 p4a.source_dir = python-for-android
   
   6.3 android.add_src = libs/
   
   6.4 android.permissions = android.permission.INTERNET,   VIBRATE,FOREGROUND_SERVICE
   
   6.5 android.api = 33  # (Using 34 may cause issues)
   
   6.6 android.gradle_dependencies = com.google.firebase:firebase-messaging:24.1.1, com.google.code.gson:gson:2.8.9, com.google.firebase:firebase-analytics
       For firebase-messaging and gson, refer to the official repositories for the latest versions.
       analytics can be left blank if unused.

   6.7 ~~Set services = Myservice:python_notification_handler.py~~
   
   
At this point, the setup should be complete. You can now go to Firebase to create and test a message notification.
The contents of python_notification_handler.py and the Cloud Functions setup will be provided later.

In main.py:
you can use the main.py as the fox520/pushyy, or you can modify by yourselves:
Add a new class to distinguish it from the original Kivy project:

```
if platform == "android":
    from kivy.properties import DictProperty
    from pushyy import Pushyy
    from pushyy import RemoteMessage
    class Pushyy_Action():
        recent_notification_data = DictProperty(rebind=True)
        def __init__(self):
            self.app = MDApp.get_running_app()
            Pushyy().foreground_message_handler(self.my_foreground_callback)
            Pushyy().notification_click_handler(self.my_notification_click_callback)
            Pushyy().token_change_listener(self.new_token_callback)
            self.get_token()
        def get_token(self):
            Pushyy().get_device_token(self.my_token_callbac)
```
use the class at on_start() of class mainapp

~~### put nothing in the notification_handler. if do that it will cause sometimes app crash. but this file/services is still needed. if buildozer.spec doesn't content a services = Myservice:python_notification_handler.py description, it will be failed to build~~

in python_notification_handler.py:
```
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
    Build = autoclass('android.os.Build')  # ✅ 補這行
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

    builder.setContentTitle(String('ESP Listening'))
    builder.setContentText(String('waiting ESP8266 signal...'))
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

def phone_action():
    process_background_messages(my_background_callback)
    RingtoneManager = autoclass('android.media.RingtoneManager')
    PythonService = autoclass('org.kivy.android.PythonService')
    # Context = autoclass('android.content.Context')
    service = PythonService.mService
    context = service.getApplicationContext()
    uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
    ringtone = RingtoneManager.getRingtone(context, uri)
    ringtone.play()

if __name__ == '__main__':
    print('8'*80)
    print('service started')
    # start_foreground()
    # for _ in range(3):
    try:
        print('-'*60)
        # phone_action()
        # break
    except Exception as e:
        print(e)
    # time.sleep(0.6)
```

firebase backend:
exec below in power shell (create a project first and go into the project):
```
npm install -g firebase-tools
firebase login
firebase init functions
```

find  index.js and put the code below instead:
```
const functions = require("firebase-functions");
const admin = require("firebase-admin");

admin.initializeApp();

exports.sendPushNotification = functions.https.onRequest((req, res) => {
  const token = req.body.token; // 從前端傳來的裝置 token
  const title = req.body.title;
  const body = req.body.body;

  const message = {
    notification: {
      title: title,
      body: body,
    },
    token: token,
  };

  admin.messaging().send(message)
    .then((response) => {
      console.log("Successfully sent message:", response);
      res.status(200).send("Notification sent!");
    })
    .catch((error) => {
      console.error("Error sending message:", error);
      res.status(500).send("Notification failed!");
    });
});
```

then delpoy the code:
```
firebase deploy --only functions  (if there's any error do it again or search for help)
```

finally it will give you a link like this:
```
https://us-central1-notification-/<project namd>.net/sendPushNotification
```
you can use it for test
A special thanks to the authors and contributors of the https://github.com/Fox520/pushyy/tree/main/src/python project.
his work made it possible to integrate Firebase Cloud Messaging into a Kivy-based Android application.

for ios push notification, link to:
https://github.com/kivy/kivy-ios/issues/964 or
https://discord.com/channels/423249981340778496/713442856190083094 and search for the author: "Cheaterman", or the title "Push notifications on iOS"
