import os
import logging

from slackclient import SlackClient


class SlackNotification(object):

    def __init__(self):
        slack_token = os.getenv('SLACK_API_TOKEN')
        print(slack_token)
        if slack_token:
            self.sc = SlackClient(slack_token)



    def get_slack_id(self, user_email):
        user_email = user_email
        results = self.sc.api_call("users.list")
        users = results.get("members")

        if users:
            user_id = [
                user.get("id")
                for user in users
                if user.get("profile").get("email") == user_email
            ]

        try:
            return user_id[0]
        except Exception:
            logging.info("User not found")
            return None


    def send_message(self, message, slack_id):
        self.sc.api_call(
            "chat.postEphemeral",
            channel=slack_id,
            text=message,
            username='@notifier',
            user=slack_id,
            as_user=True,
            icon_emoji=':ninja:',
        )