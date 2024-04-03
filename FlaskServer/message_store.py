class MessageStore:
    def __init__(self):
        self.messages = {}

    def add_message(self, sender, recipient, message):
        chat_key = (sender, recipient) if sender < recipient else (recipient, sender)
        if chat_key not in self.messages:
            self.messages[chat_key] = []
        self.messages[chat_key].append(message)

    def get_messages(self, sender, recipient):
        chat_key = (sender, recipient) if sender < recipient else (recipient, sender)
        return self.messages.get(chat_key, [])