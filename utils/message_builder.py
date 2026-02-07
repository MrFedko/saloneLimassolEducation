class MessageBuilder:
    def __init__(self):
        self.names = {
            "taste": "Taste",
            "info": "Information",
            "glass": "Serving glass",
            "description": "Description",
            "rus_description": "Description in Russian",
            "extra_info": "Additional information",
            "serving": "Serving set",
            "abv": "Alcohol by volume %",
            "history": "History"
        }
        self.EXCLUDED_KEYS = {"name", "id", "photo_link", "category"}

    def message_return(self, sheet_name: str):
        types_messages = {
            "bar": self.main_message,
            "info": self.info_message,
            "cuisine": self.main_message,
            "shibui": self.main_message,
            "alcohol": self.main_message,
        }
        return types_messages[sheet_name]


    def info_message(self, info: dict) -> str:
        text = f"""<b>{info['name']}</b>\n\n"""
        for key, value in info.items():
            if key not in self.EXCLUDED_KEYS and value:
                if key == "file_link":
                    text += f"<b>{self.names[key]}:</b>\n<a href='{value}'>Download file</a>\n\n"
                else:
                    text += f"<b>{self.names[key]}:</b>\n{value}\n\n"
        return text

    def main_message(self, info: dict) -> str:
        text = f"""<b>{info['name']}</b>\n\n"""
        for key, value in info.items():
            if key not in self.EXCLUDED_KEYS and value:
                text += f"<b>{self.names[key]}:</b>\n{value}\n\n"
        return text
