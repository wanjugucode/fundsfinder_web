# consumers.py
import json
from channels.generic.websocket import WebsocketConsumer
from .models import Notification

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        pass  # You can add logic to handle incoming messages if needed

    def send_notification(self, notification):
        self.send(text_data=json.dumps({
            'message': notification.message
        }))

