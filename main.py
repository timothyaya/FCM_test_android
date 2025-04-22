from kivy.app import App
from kivy.uix.button import Button
from kivy.lang.builder import Builder
from kivy.properties import DictProperty
from kivy.properties import ObjectProperty
from kivy.utils import platform

KV = """
BoxLayout:
    orientation: "vertical"
    ScrollableLabel:
        text: str(app.recent_notification_data)
        font_size: 50
        text_size: self.width, None
        size_hint_y: None
        height: self.texture_size[1]
    Button:
        text: "get token"
        on_release: app.get_token()
<ScrollableLabel@Label+ScrollView>
"""


class TestApp(App):
    recent_notification_data = DictProperty(rebind=True)

    def on_start(self):
        Pushyy_Action()

    def build(self):
        # your app project code
        return Builder.load_string(KV)

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