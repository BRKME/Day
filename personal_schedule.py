#!/usr/bin/env python3
"""
Personal Daily Schedule Notifier - Full Version
"""

import asyncio
import aiohttp
from datetime import datetime

class PersonalScheduleNotifier:
    def __init__(self):
        # Telegram settings
        self.telegram_token = "8442392037:AAEiM_b4QfdFLqbmmc1PXNvA99yxmFVLEp8"
        self.chat_id = "350766421"
        
        # Personal schedule data
        self.schedule = {
            'monday': {
                'утро': ['⚖️ Весы', '💪 Зарядка', '💊 Прими Витамины', '💝 Комплимент Марте и Саше', '🐱', '📺 Посмотреть Амо блог на youtube', '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'],
                'день': ['📚 Читать 25 минут', '🎯 Проверить Цели', '🤐 Молчание золото. Не перебивай'],
                'нельзя_день': ['❌ Ругаться матом', '❌ Д'],
                'вечер': ['📖 Читать с Мартой', '📔 Заполни Эмоциональный дневник', '💻 Работать 2 часа над Pet Project', '🧠 25 минут "Встреча с Грок психологом"', '🇬🇧 Марта English c папой', '💊 Прими Магний перед сном']
            },
            'tuesday': {
                'утро': ['⚖️ Весы', '💪 Зарядка', '💊 Прими Витамины', '💝 Комплимент Марте и Саше', '🐱', '📺 Посмотреть Амо блог на youtube', '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'],
                'день': ['📚 Читать 25 минут', '⚔️ HH у Самурая нет оффера только отклики', '🤐 Молчание золото. Не перебивай'],
                'нельзя_день': ['❌ Ругаться матом', '❌ Д'],
                'вечер': ['📖 Читать с Мартой', '📔 Заполни Эмоциональный дневник', '💻 Работать 2 часа над Pet Project', '🧠 25 минут "Встреча с Грок психологом"', '🇬🇧 Марта English c папой', '💊 Прими Магний перед сном']
            },
            'wednesday': {
                'утро': ['⚖️ Весы', '💪 Зарядка', '💊 Прими Витамины', '💝 Комплимент Марте и Саше', '🐱', '📺 Посмотреть Амо блог на youtube', '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'],
                'день': ['📚 Читать 25 минут', '🌿 Полить Бансай', '🤐 Молчание золото. Не перебивай'],
                'нельзя_день': ['❌ Ругаться матом', '❌ Д'],
                'вечер': ['📖 Читать с Мартой', '📔 Заполни Эмоциональный дневник', '💻 Работать 2 часа над Pet Project', '🧠 25 минут "Встреча с Грок психологом"', '🇬🇧 Марта English c папой', '💊 Прими Магний перед сном']
            },
            'thursday': {
                'утро': ['⚖️ Весы', '💪 Зарядка', '💊 Прими Витамины', '💝 Комплимент Марте и Саше', '🐱', '📺 Посмотреть Амо блог на youtube', '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'],
                'день': ['📚 Читать 25 минут', '🤐 Молчание золото. Не перебивай'],
                'нельзя_день': ['❌ Ругаться матом', '❌ Д'],
                'вечер': ['📖 Читать с Мартой', '📔 Заполни Эмоциональный дневник', '💻 Работать 2 часа над Pet Project', '🧠 25 минут "Встреча с Грок психологом"', '🇬🇧 Марта English c папой', '💊 Прими Магний перед сном']
            },
            'friday': {
                'утро': ['⚖️ Весы', '💪 Зарядка', '💊 Прими Витамины', '💝 Комплимент Марте и Саше', '🐱', '📺 Посмотреть Амо блог на youtube', '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'],
                'день': ['📚 Читать 25 минут', '⚔️ HH у Самурая нет оффера только отклики', '📞 Позвонить тете Ларисе', '🤐 Молчание золото. Не перебивай'],
                'нельзя_день': ['❌ Ругаться матом', '❌ Д'],
                'вечер': ['📖 Читать с Мартой', '📔 Заполни Эмоциональный дневник', '💻 Работать 2 часа над Pet Project', '🧠 25 минут "Встреча с Грок психологом"', '🇬🇧 Марта English c папой', '💊 Прими Магний перед сном']
            },
            'saturday': {
                'утро': ['⚖️ Весы', '💪 Зарядка', '💊 Прими Витамины', '💝 Комплимент Марте и Саше', '🐱', '📺 Посмотреть Амо блог на youtube', '🚀 Ничего не бойся и не сдавайся! - Девиз этого утра'],
                'день': ['📚 Читать 25 минут', '🌸 Полить Цветы', '🎯 Проверить Цели', '📊 LP %', '🤐 Молчание золото. Не перебивай'],
                'нельзя_день': ['❌ Ругаться матом', '❌ Д'],
                'вечер': ['📖 Читать с Мартой', '📔 Заполни Эмоциональный дневник', '💻 Работать 2 часа над Pet Project', '🧠 25 минут "Встреча с Грок психологом"', '🇬🇧 Марта English c папой', '💊 Прими Магний перед сном']
            },
            'sunday': {
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
                'parse_mode': 'HTML'
            }
            
            print("📤 Sending message to Telegram...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        print("✅ Telegram message sent successfully!")
                        return True
                    else:
                        response_text = await response.text()
                        print(f"❌ Telegram API error: {response_text}")
                        return False
        except Exception as e:
            print(f"❌ Failed to send Telegram message: {e}")
            return False
    
    def get_today_schedule(self):
        """Get today's schedule based on current day of week"""
        try:
            today = datetime.now()
            date_str = today.strftime("%d.%m.%Y")
            
            # English day names for simplicity
            day_of_week = today.strftime("%A").lower()
            
            print(f"📅 Today: {date_str}, {day_of_week}")
            today_schedule = self.schedule.get(day_of_week, {})
            
            return date_str, day_of_week, today_schedule
            
        except Exception as e:
            print(f"❌ Error getting schedule: {e}")
            return "01.01.2024", "monday", {}
    
    def format_morning_message(self, date_str: str, day_of_week: str, schedule: dict):
        """Format morning message (07:30)"""
        day_names = {
            'monday': 'Понедельник',
            'tuesday': 'Вторник', 
            'wednesday': 'Среда',
            'thursday': 'Четверг',
            'friday': 'Пятница',
            'saturday': 'Суббота',
            'sunday': 'Воскресенье'
        }
        
        day_ru = day_names.get(day_of_week, day_of_week)
        
        message = f"🌅 <b>Доброе утро! План на {date_str}</b>\n"
        message += f"🗓️ <b>{day_ru}</b>\n\n"
        
        if schedule.get('утро'):
            message += "<b>Утренние задачи:</b>\n"
            for task in schedule['утро']:
                message += f"• {task}\n"
        
        message += "\n💫 <b>Хорошего дня! Ты можешь всё!</b>"
        return message
    
    def format_day_message(self, date_str: str, day_of_week: str, schedule: dict):
        """Format day message (12:30)"""
        day_names = {
            'monday': 'Понедельник',
            'tuesday': 'Вторник',
            'wednesday': 'Среда',
            'thursday': 'Четверг', 
            'friday': 'Пятница',
            'saturday': 'Суббота',
            'sunday': 'Воскресенье'
        }
        
        day_ru = day_names.get(day_of_week, day_of_week)
        
        message = f"☀️ <b>День в разгаре! План на {date_str}</b>\n"
        message += f"🗓️ <b>{day_ru}</b>\n\n"
        
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
        day_names = {
            'monday': 'Понедельник',
            'tuesday': 'Вторник',
            'wednesday': 'Среда',
            'thursday': 'Четверг',
            'friday': 'Пятница',
            'saturday': 'Суббота', 
            'sunday': 'Воскресенье'
        }
        
        day_ru = day_names.get(day_of_week, day_of_week)
        
        message = f"🌙 <b>Вечерний план на {date_str}</b>\n"
        message += f"🗓️ <b>{day_ru}</b>\n\n"
        
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
    """Main execution function"""
    try:
        print("=" * 50)
        print("🚀 Personal Schedule Notifier")
        print("=" * 50)
        
        # Get current time info
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_utc = datetime.utcnow().strftime("%H:%M")
        
        print(f"🕐 Local Time: {current_time}")
        print(f"🌐 UTC Time: {current_utc}")
        
        notifier = PersonalScheduleNotifier()
        
        # Determine which reminder to send
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
            print(f"⏰ No exact time match for {current_time}")
            # For manual testing, send current time's reminder
            if current_time < "12:00":
                print("🕐 Sending morning reminder for testing")
                success = await notifier.send_morning_reminder()
            elif current_time < "19:00":
                print("🕐 Sending day reminder for testing") 
                success = await notifier.send_day_reminder()
            else:
                print("🕐 Sending evening reminder for testing")
                success = await notifier.send_evening_reminder()
        
        if success:
            print("🎉 Reminder sent successfully!")
        else:
            print("💥 Failed to send reminder!")
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
