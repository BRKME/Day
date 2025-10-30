#!/usr/bin/env python3
"""
Personal Daily Schedule Notifier
Sends daily tasks and reminders via Telegram 3 times per day
"""

import asyncio
import aiohttp
from datetime import datetime
import locale
import sys

try:
    # Устанавливаем русскую локаль для дней недели
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')
    except:
        print("⚠️ Could not set Russian locale, using default")

class PersonalScheduleNotifier:
    def __init__(self):
        # Telegram settings
        self.telegram_token = "8442392037:AAEiM_b4QfdFLqbmmc1PXNvA99yxmFVLEp8"
        self.chat_id = "350766421"
        
        # Personal schedule data
        self.schedule = {
            'понедельник': {
                'утро': ['⚖️ Весы', '💪 Зарядка', '💊 Прими Витамины', '💝 Комплимент Марте и Саше', '🐱', '📺 Посмотреть Амо блог на youtube', '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'],
                'день': ['📚 Читать 25 минут', '🎯 Проверить Цели', '🤐 Молчание золото. Не перебивай'],
                'нельзя_день': ['❌ Ругаться матом', '❌ Д'],
                'вечер': ['📖 Читать с Мартой', '📔 Заполни Эмоциональный дневник', '💻 Работать 2 часа над Pet Project', '🧠 25 минут "Встреча с Грок психологом"', '🇬🇧 Марта English c папой', '💊 Прими Магний перед сном']
            },
            'вторник': {
                'утро': ['⚖️ Весы', '💪 Зарядка', '💊 Прими Витамины', '💝 Комплимент Марте и Саше', '🐱', '📺 Посмотреть Амо блог на youtube', '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'],
                'день': ['📚 Читать 25 минут', '⚔️ HH у Самурая нет оффера только отклики', '🤐 Молчание золото. Не перебивай'],
                'нельзя_день': ['❌ Ругаться матом', '❌ Д'],
                'вечер': ['📖 Читать с Мартой', '📔 Заполни Эмоциональный дневник', '💻 Работать 2 часа над Pet Project', '🧠 25 минут "Встреча с Грок психологом"', '🇬🇧 Марта English c папой', '💊 Прими Магний перед сном']
            },
            'среда': {
                'утро': ['⚖️ Весы', '💪 Зарядка', '💊 Прими Витамины', '💝 Комплимент Марте и Саше', '🐱', '📺 Посмотреть Амо блог на youtube', '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'],
                'день': ['📚 Читать 25 минут', '🌿 Полить Бансай', '🤐 Молчание золото. Не перебивай'],
                'нельзя_день': ['❌ Ругаться матом', '❌ Д'],
                'вечер': ['📖 Читать с Мартой', '📔 Заполни Эмоциональный дневник', '💻 Работать 2 часа над Pet Project', '🧠 25 минут "Встреча с Грок психологом"', '🇬🇧 Марта English c папой', '💊 Прими Магний перед сном']
            },
            'четверг': {
                'утро': ['⚖️ Весы', '💪 Зарядка', '💊 Прими Витамины', '💝 Комплимент Марте и Саше', '🐱', '📺 Посмотреть Амо блог на youtube', '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'],
                'день': ['📚 Читать 25 минут', '🤐 Молчание золото. Не перебивай'],
                'нельзя_день': ['❌ Ругаться матом', '❌ Д'],
                'вечер': ['📖 Читать с Мартой', '📔 Заполни Эмоциональный дневник', '💻 Работать 2 часа над Pet Project', '🧠 25 минут "Встреча с Грок психологом"', '🇬🇧 Марта English c папой', '💊 Прими Магний перед сном']
            },
            'пятница': {
                'утро': ['⚖️ Весы', '💪 Зарядка', '💊 Прими Витамины', '💝 Комплимент Марте и Саше', '🐱', '📺 Посмотреть Амо блог на youtube', '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'],
                'день': ['📚 Читать 25 минут', '⚔️ HH у Самурая нет оффера только отклики', '📞 Позвонить тете Ларисе', '🤐 Молчание золото. Не перебивай'],
                'нельзя_день': ['❌ Ругаться матом', '❌ Д'],
                'вечер': ['📖 Читать с Мартой', '📔 Заполни Эмоциональный дневник', '💻 Работать 2 часа над Pet Project', '🧠 25 минут "Встреча с Грок психологом"', '🇬🇧 Марта English c папой', '💊 Прими Магний перед сном']
            },
            'суббота': {
                'утро': ['⚖️ Весы', '💪 Зарядка', '💊 Прими Витамины', '💝 Комплимент Марте и Саше', '🐱', '📺 Посмотреть Амо блог на youtube', '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'],
                'день': ['📚 Читать 25 минут', '🌸 Полить Цветы', '🎯 Проверить Цели', '📊 LP %', '🤐 Молчание золото. Не перебивай'],
                'нельзя_день': ['❌ Ругаться матом', '❌ Д'],
                'вечер': ['📖 Читать с Мартой', '📔 Заполни Эмоциональный дневник', '💻 Работать 2 часа над Pet Project', '🧠 25 минут "Встреча с Грок психологом"', '🇬🇧 Марта English c папой', '💊 Прими Магний перед сном']
            },
            'воскресенье': {
                'утро': ['💝 Комплимент Марте и Саше', '🐱'],
                'день': ['👨‍👩‍👧‍👦 Family Day', '🤐 Молчание золото. Не перебивай', '✅ Д'],
                'нельзя_день': ['❌ Ругаться матом'],
                'вечер': ['💊 Прими Магний перед сном']
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
            
            print("📤 Attempting to send Telegram message...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=30) as response:
                    response_text = await response.text()
                    print(f"📨 Telegram API response: {response.status}")
                    
                    if response.status == 200:
                        print("✅ Telegram message sent successfully!")
                        return True
                    else:
                        print(f"❌ Telegram API error: {response_text}")
                        return False
                        
        except Exception as e:
            print(f"❌ Failed to send Telegram message: {str(e)}")
            return False
    
    def get_today_schedule(self):
        """Get today's schedule based on current day of week"""
        try:
            today = datetime.now()
            date_str = today.strftime("%d.%m.%Y")
            
            # Simple day mapping without locale
            days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
            day_of_week_ru = days[today.weekday()]
            
            today_schedule = self.schedule.get(day_of_week_ru, {})
            
            print(f"📅 Today: {date_str}, {day_of_week_ru}")
            return date_str, day_of_week_ru, today_schedule
            
        except Exception as e:
            print(f"❌ Error getting schedule: {e}")
            return "01.01.2024", "понедельник", {}
    
    def format_morning_message(self, date_str: str, day_of_week: str, schedule: dict):
        """Format morning message"""
        message = f"🌅 <b>Доброе утро! План на {date_str}</b>\n"
        message += f"🗓️ <b>{day_of_week.capitalize()}</b>\n\n"
        
        if schedule.get('утро'):
            message += "<b>Утренние задачи:</b>\n"
            for task in schedule['утро']:
                message += f"• {task}\n"
        
        message += "\n💫 <b>Хорошего дня! Ты можешь всё!</b>"
        return message
    
    def format_day_message(self, date_str: str, day_of_week: str, schedule: dict):
        """Format day message"""
        message = f"☀️ <b>День в разгаре! План на {date_str}</b>\n"
        message += f"🗓️ <b>{day_of_week.capitalize()}</b>\n\n"
        
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
        """Format evening message"""
        message = f"🌙 <b>Вечерний план на {date_str}</b>\n"
        message += f"🗓️ <b>{day_of_week.capitalize()}</b>\n\n"
        
        if schedule.get('вечер'):
            message += "<b>Вечерние задачи:</b>\n"
            for task in schedule['вечер']:
                message += f"• {task}\n"
        
        message += "\n🌜 <b>Отличный день! Завершай дела и отдыхай!</b>"
        return message
    
    async def send_morning_reminder(self):
        """Send morning reminder"""
        print("🌅 Sending morning reminder...")
        date_str, day_of_week, schedule = self.get_today_schedule()
        message = self.format_morning_message(date_str, day_of_week, schedule)
        return await self.send_telegram_message(message)
    
    async def send_day_reminder(self):
        """Send day reminder"""
        print("☀️ Sending day reminder...")
        date_str, day_of_week, schedule = self.get_today_schedule()
        message = self.format_day_message(date_str, day_of_week, schedule)
        return await self.send_telegram_message(message)
    
    async def send_evening_reminder(self):
        """Send evening reminder"""
        print("🌙 Sending evening reminder...")
        date_str, day_of_week, schedule = self.get_today_schedule()
        message = self.format_evening_message(date_str, day_of_week, schedule)
        return await self.send_telegram_message(message)

async def main():
    """Main execution function"""
    try:
        print("=" * 50)
        print("🚀 Starting Personal Schedule Notifier")
        print("=" * 50)
        
        # Get current time info
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_utc = datetime.utcnow().strftime("%H:%M")
        
        print(f"🕐 Local Time: {current_time}")
        print(f"🌐 UTC Time: {current_utc}")
        print(f"📅 Date: {now.strftime('%d.%m.%Y')}")
        
        notifier = PersonalScheduleNotifier()
        
        # Determine which reminder to send based on time
        if current_time == "07:30":
            print("⏰ Time matched: 07:30 - Morning reminder")
            success = await notifier.send_morning_reminder()
        elif current_time == "12:30":
            print("⏰ Time matched: 12:30 - Day reminder")
            success = await notifier.send_day_reminder()
        elif current_time == "19:00":
            print("⏰ Time matched: 19:00 - Evening reminder")
            success = await notifier.send_evening_reminder()
        else:
            print(f"⏰ No match for {current_time}, sending test message")
            # Send test message if no time match
            test_msg = f"🧪 <b>Test Message</b>\nTime: {current_time}\nDate: {now.strftime('%d.%m.%Y')}\nStatus: ✅ System Working!"
            success = await notifier.send_telegram_message(test_msg)
        
        if success:
            print("🎉 Operation completed successfully!")
            sys.exit(0)  # Success exit code
        else:
            print("💥 Operation failed!")
            sys.exit(1)  # Error exit code
            
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
