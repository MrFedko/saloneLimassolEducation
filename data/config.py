import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME = "Education app"
    DB_NAME = "knowledge.db"
    PROJECT_DESCRIPTION = "Education app for restaurant staff"

    BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
    EMAIL_CONTROLLER = str(os.getenv("EMAIL_CONTROLLER"))
    SHEET_ID = str(os.getenv("SHEET_ID"))

    admins = [
        os.getenv("ADMIN_ID"),
    ]

    worksheet_ids = {
    "Bar": (0, "bar"),
    "Info": (794605464, "info"),
    "Kitchen": (437971605, "cuisine"),
    "Shibui": (2039851202, "shibui"),
    "Alcohol": (1619889557, "alcohol"),
    }

    db_tables = {
        0: "bar",
        794605464: "info",
        437971605: "cuisine",
        2039851202: "shibui",
        1619889557: "alcohol",
    }

    # PROJECT_PATH = "/Users/mac/Desktop/my_projects/saloneLimEducation/saloneLimassolEducation/"

    PROJECT_PATH = "/home/educationBot/saloneLimassolEducation/"
    CREDS_PATH = PROJECT_PATH + os.getenv("CREDS_PATH")
    PHOTO_PATH = PROJECT_PATH + "data/photo/"
    DB_PATH = PROJECT_PATH + DB_NAME
    CREDS_PATH = PROJECT_PATH + os.getenv("CREDS_PATH")
    SERVER_IP = "localhost"
    SERVER_PORT = 8000
    SERVER_LINK = f"http://{SERVER_IP}:{SERVER_PORT}"

settings = Settings()
