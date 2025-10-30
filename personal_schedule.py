#!/usr/bin/env python3
"""
Personal Daily Schedule Notifier
Sends daily tasks and reminders via Telegram 3 times per day
"""

import asyncio
import aiohttp
from datetime import datetime
import locale

# Устанавливаем русскую локаль для дней недели
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')
    except:
        pass

class PersonalScheduleNotifier:
    def __init__(self):
        # Telegram settings
        self.telegram_token = "8442392037:AAEiM_b4QfdFLqbmmc1PXNvA99yxmFVLEp8"
        self.chat_id = "350766421"
        
        # Personal schedule data (остается без изменений)
        self.schedule = {
            'понедельник': {
                'утро': [
                    '⚖️ Весы',
                    '💪 Зарядка', 
                    '💊 Прими Витамины',
                    '💝 Комплимент Марте и Саше',
                    '🐱',
                    '📺 Посмотреть Амо блог на youtube',
                    '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'
                ],
                'день': [
                    '📚 Читать 25 минут',
                    '🎯 Проверить Цели',
                    '🤐 Молчание золото. Не перебивай'
                ],
                'нельзя_день': [
                    '❌ Ругаться матом',
                    '❌ Д'
                ],
                'вечер': [
                    '📖 Читать с Мартой',
                    '📔 Заполни Эмоциональный дневник',
                    '💻 Работать 2 часа над Pet Project',
                    '🧠 25 минут "Встреча с Грок психологом"',
                    '🇬🇧 Марта English c папой',
                    '💊 Прими Магний перед сном'
                ]
            },
            'вторник': {
                'утро': [
                    '⚖️ Весы',
                    '💪 Зарядка',
                    '💊 Прими Витамины',
                    '💝 Комплимент Марте и Саше',
                    '🐱',
                    '📺 Посмотреть Амо блог на youtube',
                    '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'
                ],
                'день': [
                    '📚 Читать 25 минут',
                    '⚔️ HH у Самурая нет оффера только отклики',
                    '🤐 Молчание золото. Не перебивай'
                ],
                'нельзя_день': [
                    '❌ Ругаться матом',
                    '❌ Д'
                ],
                'вечер': [
                    '📖 Читать с Мартой',
                    '📔 Заполни Эмоциональный дневник',
                    '💻 Работать 2 часа над Pet Project',
                    '🧠 25 минут "Встреча с Грок психологом"',
                    '🇬🇧 Марта English c папой',
                    '💊 Прими Магний перед сном'
                ]
            },
            'среда': {
                'утро': [
                    '⚖️ Весы',
                    '💪 Зарядка',
                    '💊 Прими Витамины',
                    '💝 Комплимент Марте и Саше',
                    '🐱',
                    '📺 Посмотреть Амо блог на youtube',
                    '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'
                ],
                'день': [
                    '📚 Читать 25 минут',
                    '🌿 Полить Бансай',
                    '🤐 Молчание золото. Не перебивай'
                ],
                'нельзя_день': [
                    '❌ Ругаться матом',
                    '❌ Д'
                ],
                'вечер': [
                    '📖 Читать с Мартой',
                    '📔 Заполни Эмоциональный дневник',
                    '💻 Работать 2 часа над Pet Project',
                    '🧠 25 минут "Встреча с Грок психологом"',
                    '🇬🇧 Марта English c папой',
                    '💊 Прими Магний перед сном'
                ]
            },
            'четверг': {
                'утро': [
                    '⚖️ Весы',
                    '💪 Зарядка',
                    '💊 Прими Витамины',
                    '💝 Комплимент Марте и Саше',
                    '🐱',
                    '📺 Посмотреть Амо блог на youtube',
                    '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'
                ],
                'день': [
                    '📚 Читать 25 минут',
                    '🤐 Молчание золото. Не перебивай'
                ],
                'нельзя_день': [
                    '❌ Ругаться матом',
                    '❌ Д'
                ],
                'вечер': [
                    '📖 Читать с Мартой',
                    '📔 Заполни Эмоциональный дневник',
                    '💻 Работать 2 часа над Pet Project',
                    '🧠 25 минут "Встреча с Грок психологом"',
                    '🇬🇧 Марта English c папой',
                    '💊 Прими Магний перед сном'
                ]
            },
            'пятница': {
                'утро': [
                    '⚖️ Весы',
                    '💪 Зарядка',
                    '💊 Прими Витамины',
                    '💝 Комплимент Марте и Саше',
                    '🐱',
                    '📺 Посмотреть Амо блог на youtube',
                    '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'
                ],
                'день': [
                    '📚 Читать 25 минут',
                    '⚔️ HH у Самурая нет оффера только отклики',
                    '📞 Позвонить тете Ларисе',
                    '🤐 Молчание золото. Не перебивай'
                ],
                'нельзя_день': [
                    '❌ Ругаться матом',
                    '❌ Д'
                ],
                'вечер': [
                    '📖 Читать с Мартой',
                    '📔 Заполни Эмоциональный дневник',
                    '💻 Работать 2 часа над Pet Project',
                    '🧠 25 минут "Встреча с Грок психологом"',
                    '🇬🇧 Марта English c папой',
                    '💊 Прими Магний перед сном'
                ]
            },
            'суббота': {
                'утро': [
                    '⚖️ Весы',
                    '💪 Зарядка',
                    '💊 Прими Витамины',
                    '💝 Комплимент Марте и Саше',
                    '🐱',
                    '📺 Посмотреть Амо блог на youtube',
                    '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'
                ],
                'день': [
                    '📚 Читать 25 минут',
                    '🌸 Полить Цветы',
                    '🎯 Проверить Цели',
                    '📊 LP %',
                    '🤐 Молчание золото. Не перебивай'
                ],
                'нельзя_день': [
                    '❌ Ругаться матом',
                    '❌ Д'
                ],
                'вечер': [
                    '📖 Читать с Мартой',
                    '📔 Заполни Эмоциональный дневник',
                    '💻 Работать 2 часа над Pet Project',
                    '🧠 25 минут "Встреча с Грок психологом"',
                    '🇬🇧 Марта English c папой',
                    '💊 Прими Магний перед сном'
                ]
            },
            'воскресенье': {
                'утро': [
                    '💝 Комплимент Марте и Саше',
                    '🐱'
                ],
                'день': [
                    '👨‍👩‍👧‍👦 Family Day',
                    '🤐 Молчание золото. Не перебивай',
                    '✅ Д'
                ],
                'нельзя_день': [
                    '❌ Ругаться матом'
                ],
                'вечер': [
                    '💊 Прими Магний перед сном'
                ]
            }
        }
    
    async def send_telegram_message(self, message: str):
        """Send message to Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        print("✅ Telegram message sent successfully")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ Telegram API error: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ Failed to send Telegram message: {e}")
            return False
    
    def get_today_schedule(self):
        """Get today's schedule based on current day of week"""
        today = datetime.now()
        
        # Format date and day of week in Russian
        date_str = today.strftime("%d.%m.%Y")
        
        try:
            day_of_week = today.strftime("%A").lower()
            day_of_week_ru = {
                'monday': 'понедельник',
                'tuesday': 'вторник',
                'wednesday': 'среда', 
                'thursday': 'четверг',
                'friday': 'пятница',
                'saturday': 'суббота',
                'sunday': 'воскресенье'
            }.get(day_of_week, day_of_week)
        except:
            # Fallback if locale doesn't work
            days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
            day_of_week_ru = days[today.weekday()]
        
        today_schedule = self.schedule.get(day_of_week_ru, {})
        
        return date_str, day_of_week_ru, today_schedule
    
    def format_morning_message(self, date_str: str, day_of_week: str, schedule: dict):
        """Format morning message (07:30)"""
        day_capitalized = day_of_week.capitalize()
        
        message = f"🌅 <b>Доброе утро! План на {date_str}</b>\n"
        message += f"🗓️ <b>{day_capitalized}</b>\n\n"
        
        if schedule.get('утро'):
            message += "<b>Утренние задачи:</b>\n"
            for task in schedule['утро']:
                message += f"• {task}\n"
        
        message += "\n💫 <b>Хорошего дня! Ты можешь всё!</b>"
        
        return message
    
    def format_day_message(self, date_str: str, day_of_week: str, schedule: dict):
        """Format day message (12:30)"""
        day_capitalized = day_of_week.capitalize()
        
        message = f"☀️ <b>День в разгаре! План на {date_str}</b>\n"
        message += f"🗓️ <b>{day_capitalized}</b>\n\n"
        
        if schedule.get('день'):
            message += "<b>Дневные задачи:</b>\n"
            for task in schedule['день']:
                message += f"• {task}\n"
        
        if schedule.get('нельзя_день'):
            message += "\n<b>Нельзя делать:</b>\n"
            for prohibition in schedule['нельзя_день']:
                message += f"• {prohibition}\n"
        
        message += "\n💪 <b>Продолжаем в том же духе!</b>"
        
        return message
    
    def format_evening_message(self, date_str: str, day_of_week: str, schedule: dict):
        """Format evening message (19:00)"""
        day_capitalized = day_of_week.capitalize()
        
        message = f"🌙 <b>Вечерний план на {date_str}</b>\n"
        message += f"🗓️ <b>{day_capitalized}</b>\n\n"
        
        if schedule.get('вечер'):
            message += "<b>Вечерние задачи:</b>\n"
            for task in schedule['вечер']:
                message += f"• {task}\n"
        
        message += "\n🌜 <b>Отличный день! Завершай дела и отдыхай!</b>"
        
        return message
    
    async def send_morning_reminder(self):
        """Send morning reminder at 07:30"""
        print("🌅 Sending morning reminder...")
        date_str, day_of_week, schedule = self.get_today_schedule()
        message = self.format_morning_message(date_str, day_of_week, schedule)
        return await self.send_telegram_message(message)
    
    async def send_day_reminder(self):
        """Send day reminder at 12:30"""
        print("☀️ Sending day reminder...")
        date_str, day_of_week, schedule = self.get_today_schedule()
        message = self.format_day_message(date_str, day_of_week, schedule)
        return await self.send_telegram_message(message)
    
    async def send_evening_reminder(self):
        """Send evening reminder at 19:00"""
        print("🌙 Sending evening reminder...")
        date_str, day_of_week, schedule = self.get_today_schedule()
        message = self.format_evening_message(date_str, day_of_week, schedule)
        return await self.send_telegram_message(message)

async def main():
    """Main execution function - определяет время и отправляет соответствующее напоминание"""
    try:
        notifier = PersonalScheduleNotifier()
        current_time = datetime.now().strftime("%H:%M")
        
        print(f"🕐 Current time: {current_time}")
        
        if current_time == "07:30":
            await notifier.send_morning_reminder()
        elif current_time == "12:30":
            await notifier.send_day_reminder()
        elif current_time == "19:00":
            await notifier.send_evening_reminder()
        else:
            print(f"ℹ️ No scheduled reminder for {current_time}")
            
    except Exception as e:
        print(f"❌ Critical error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
