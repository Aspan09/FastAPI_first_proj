import os
from fastapi import FastAPI, HTTPException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from dotenv import load_dotenv
from pydantic import BaseModel


app = FastAPI()

load_dotenv()

SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

# Создание логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailRequest(BaseModel):
    to: str
    subject: str
    message: str



@app.post("/send_email")
async def send_email(email: EmailRequest):
    # Проверка формата адреса электронной почты
    if not validate_email(email.to):
        raise HTTPException(status_code=400, detail="Некорректный формат адреса электронной почты")
    try:
        # Отправка письма
        send_email_smtp(email)
        logger.info(f"Отправлено письмо на адрес {email.to}")
        return {"message": "Письмо успешно отправлено"}
    except Exception as e:
        logger.error(f"Ошибка при отправке письма: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при отправке письма")


def validate_email(email):
    # Простейшая проверка формата адреса электронной почты
    return "@" in email and "." in email


def send_email_smtp(email):
    # Настройки SMTP-сервера (пример для Gmail)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = SMTP_USERNAME
    smtp_password = SMTP_PASSWORD  # Важно: храните пароль в безопасном месте

    # Создание объекта SMTP-клиента
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)

    # Создание письма
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = email.to
    msg['Subject'] = email.subject

    # Добавление текстового сообщения
    msg.attach(MIMEText(email.message, 'plain'))

    # Отправка письма
    server.sendmail(smtp_username, email.to, msg.as_string())

    # Завершение соединения с SMTP-сервером
    server.quit()
