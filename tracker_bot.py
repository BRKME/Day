#!/usr/bin/env python3
"""
Telegram бот для отслеживания выполнения задач
Обрабатывает кнопку "Обновить прогресс" и ведёт статистику
"""

import asyncio
import aiohttp
from aiohttp import web
import json
import logging
from datetime import datetime, timedelta
import os
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskTrackerBot:
    def __init__(self):
        self.telegram_token = "8442392037:AAEiM_b4QfdFLqbmmc1PXNvA99yxmFVLEp8"
        self.chat_id = "350766421"
        self.stats_file = "stats.json"
        self.last_update_id = 0
        
        # Хранилище текущего состояния (message_id -> данные)
        self.current_messages = {}
        
    def load_stats(self):
        """Загружает статистику из файла"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки статистики: {e}")
            return {}
    
    def save_stats(self, stats):
        """Сохраняет статистику в файл"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            logger.info("✅ Статистика сохранена")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения статистики: {e}")
            return False
    
    def commit_to_github(self):
        """Делает commit и push в GitHub"""
        try:
            subprocess.run(['git', 'add', self.stats_file], check=True)
            subprocess.run(['git', 'commit', '-m', f'Update stats: {datetime.now().strftime("%Y-%m-%d %H:%M")}'], check=True)
            subprocess.run(['git', 'push'], check=True)
            logger.info("✅ Изменения отправлены в GitHub")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Не удалось отправить в GitHub: {e}")
            return False
    
    def get_today_key(self):
        """Возвращает ключ для сегодняшнего дня"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def calculate_percentage(self, completed, total):
        """Вычисляет процент выполнения"""
        if total == 0:
            return 0
        return int((len(completed) / total) * 100)
    
    def get_progress_bar(self, percentage, length=8):
        """Создаёт прогресс-бар"""
        filled = int((percentage / 100) * length)
        return '▓' * filled + '░' * (length - filled)
    
    def get_stars(self, percentage):
        """Возвращает звёздочки по проценту"""
        if percentage >= 90:
            return '⭐⭐⭐⭐⭐'
        elif percentage >= 80:
            return '⭐⭐⭐⭐'
        elif percentage >= 70:
            return '⭐⭐⭐'
        elif percentage >= 60:
            return '⭐⭐'
        elif percentage >= 50:
            return '⭐'
        return ''
    
    def get_motivation(self, percentage):
        """Возвращает мотивационное сообщение"""
        if percentage >= 90:
            return "🏆 Идеально! Так держать!"
        elif percentage >= 80:
            return "✨ Отлично! Продуктивный день!"
        elif percentage >= 70:
            return "💪 Хороший день!"
        elif percentage >= 60:
            return "👍 Неплохо, есть к чему стремиться"
        elif percentage >= 50:
            return "📈 Слабовато, но завтра лучше!"
        return "💪 Не сдавайся! Завтра новый день!"
    
    async def send_daily_summary(self):
        """Отправляет итоги дня в 23:00"""
        stats = self.load_stats()
        today_key = self.get_today_key()
        
        if today_key not in stats:
            logger.info("📊 Нет данных за сегодня для итогов")
            return
        
        today_data = stats[today_key]
        
        # Формируем сообщение
        message = f"🌙 <b>ИТОГИ ДНЯ - {datetime.now().strftime('%d.%m.%Y')}</b>\n\n"
        message += "━━━━━━━━━━━━━━━━━━\n\n"
        
        # Статистика по периодам
        if 'morning' in today_data:
            morning = today_data['morning']
            perc = self.calculate_percentage(morning.get('completed', []), morning.get('total', 0))
            bar = self.get_progress_bar(perc)
            message += f"☀️ Утро: {bar} {len(morning.get('completed', []))}/{morning.get('total', 0)} ({perc}%)\n"
        
        if 'day' in today_data:
            day = today_data['day']
            perc = self.calculate_percentage(day.get('completed', []), day.get('total', 0))
            bar = self.get_progress_bar(perc)
            message += f"🌤️ День: {bar} {len(day.get('completed', []))}/{day.get('total', 0)} ({perc}%)\n"
        
        if 'evening' in today_data:
            evening = today_data['evening']
            perc = self.calculate_percentage(evening.get('completed', []), evening.get('total', 0))
            bar = self.get_progress_bar(perc)
            message += f"🌙 Вечер: {bar} {len(evening.get('completed', []))}/{evening.get('total', 0)} ({perc}%)\n"
        
        message += "\n━━━━━━━━━━━━━━━━━━\n"
        message += f"🎯 <b>РЕЗУЛЬТАТ ДНЯ:</b>\n"
        message += f"💯 {today_data.get('points', 0)}/{today_data.get('max_points', 0)} задач ({today_data.get('percentage', 0)}%)\n"
        message += f"🏆 Баллы: {today_data.get('points', 0)} из {today_data.get('max_points', 0) - 3}\n\n"
        
        stars = self.get_stars(today_data.get('percentage', 0))
        if stars:
            message += f"{stars} "
        message += self.get_motivation(today_data.get('percentage', 0))
        
        # Отправляем
        await self.send_telegram_message(message)
    
    async def send_weekly_summary(self):
        """Отправляет итоги недели в воскресенье 23:00"""
        stats = self.load_stats()
        
        # Получаем последние 7 дней
        today = datetime.now()
        week_data = []
        
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_key = day.strftime("%Y-%m-%d")
            day_name = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][day.weekday()]
            
            if day_key in stats:
                percentage = stats[day_key].get('percentage', 0)
                week_data.append({
                    'name': day_name,
                    'percentage': percentage,
                    'date': day.strftime('%d.%m')
                })
            else:
                week_data.append({
                    'name': day_name,
                    'percentage': 0,
                    'date': day.strftime('%d.%m')
                })
        
        # Формируем сообщение
        week_start = (today - timedelta(days=6)).strftime('%d.%m')
        week_end = today.strftime('%d.%m')
        
        message = f"📈 <b>ИТОГИ НЕДЕЛИ</b>\n"
        message += f"{week_start} - {week_end}.2024\n\n"
        message += "━━━━━━━━━━━━━━━━━━\n\n"
        
        total_percentage = 0
        streak = 0
        
        for day_data in week_data:
            perc = day_data['percentage']
            bar = self.get_progress_bar(perc)
            stars = self.get_stars(perc)
            message += f"{day_data['name']}: {bar} {perc}% {stars}\n"
            
            total_percentage += perc
            if perc >= 70:
                streak += 1
        
        avg_percentage = int(total_percentage / 7) if week_data else 0
        
        message += "\n━━━━━━━━━━━━━━━━━━\n"
        message += f"📊 Средний результат: {avg_percentage}%\n"
        message += f"🔥 Дней подряд 70%+: {streak}\n\n"
        
        if avg_percentage >= 80:
            message += "🏆 Отличная неделя!\nТак держать! 💪"
        elif avg_percentage >= 70:
            message += "✨ Хорошая неделя!\nПродолжай в том же духе! 💪"
        elif avg_percentage >= 60:
            message += "👍 Неплохая неделя!\nЕщё чуть-чуть! 💪"
        else:
            message += "📈 Есть над чем работать!\nСледующая неделя будет лучше! 💪"
        
        await self.send_telegram_message(message)
    
    async def check_schedule(self):
        """Проверяет расписание для отправки итогов"""
        now = datetime.now()
        
        # Итоги дня в 23:00
        if now.hour == 23 and now.minute == 0:
            logger.info("⏰ Время для итогов дня")
            await self.send_daily_summary()
            
            # Итоги недели в воскресенье
            if now.weekday() == 6:  # Воскресенье
                logger.info("⏰ Время для итогов недели")
                await asyncio.sleep(60)  # Подождём минуту после итогов дня
                await self.send_weekly_summary()
    
    async def send_telegram_message(self, message):
        """Отправляет сообщение в Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        logger.info("✅ Сообщение отправлено")
                        return True
                    else:
                        logger.error(f"❌ Ошибка отправки: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            return False
    
    async def edit_message(self, message_id, text, reply_markup=None):
        """Редактирует сообщение"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/editMessageText"
            payload = {
                'chat_id': self.chat_id,
                'message_id': message_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            if reply_markup:
                payload['reply_markup'] = reply_markup
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        logger.info("✅ Сообщение обновлено")
                        return True
                    else:
                        logger.error(f"❌ Ошибка обновления: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            return False
    
    async def answer_callback_query(self, callback_query_id, text=None):
        """Отвечает на callback query"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/answerCallbackQuery"
            payload = {'callback_query_id': callback_query_id}
            
            if text:
                payload['text'] = text
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            return False
    
    async def process_callback(self, callback_data, callback_query_id, message_id, message_text):
        """Обрабатывает callback от кнопок"""
        logger.info(f"📞 Получен callback: {callback_data}")
        
        if callback_data == 'update_progress':
            # Показываем чек-лист
            await self.show_checklist(message_id, message_text)
            await self.answer_callback_query(callback_query_id, "Отметь выполненные задачи ✅")
        
        elif callback_data.startswith('toggle_'):
            # Переключаем задачу
            parts = callback_data.split('_')
            period = parts[1]  # morning/day/evening
            task_idx = int(parts[2])
            
            await self.toggle_task(message_id, period, task_idx, message_text)
            await self.answer_callback_query(callback_query_id)
        
        elif callback_data == 'save_progress':
            # Сохраняем прогресс
            await self.save_progress(message_id, message_text)
            await self.answer_callback_query(callback_query_id, "✅ Прогресс сохранён!")
        
        elif callback_data == 'cancel_update':
            # Отменяем обновление
            await self.cancel_update(message_id, message_text)
            await self.answer_callback_query(callback_query_id, "❌ Отменено")
    
    async def show_checklist(self, message_id, original_message):
        """Показывает чек-лист для отметки задач"""
        # TODO: Парсим исходное сообщение и показываем кнопки
        # Пока заглушка
        text = "✅ <b>Отметь выполненные задачи:</b>\n\n"
        text += "Функция в разработке..."
        
        await self.edit_message(message_id, text)
    
    async def toggle_task(self, message_id, period, task_idx, message_text):
        """Переключает статус задачи"""
        # TODO: Реализация переключения
        pass
    
    async def save_progress(self, message_id, message_text):
        """Сохраняет прогресс в stats.json"""
        # TODO: Сохранение данных
        pass
    
    async def cancel_update(self, message_id, original_message):
        """Отменяет обновление, возвращает исходное сообщение"""
        await self.edit_message(message_id, original_message)
    
    async def get_updates(self):
        """Получает обновления от Telegram (long polling)"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 30
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=40) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('result', [])
                    return []
        except Exception as e:
            logger.error(f"❌ Ошибка получения обновлений: {e}")
            return []
    
    async def health_check(self, request):
        """HTTP endpoint для Render health check"""
        return web.Response(text="OK", status=200)
    
    async def run(self):
        """Основной цикл бота"""
        logger.info("🤖 Tracker Bot запущен!")
        logger.info("📊 Слушаю обновления...")
        
        # Запускаем HTTP сервер для Render
        app = web.Application()
        app.router.add_get('/', self.health_check)
        app.router.add_get('/health', self.health_check)
        
        port = int(os.environ.get('PORT', 10000))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        logger.info(f"🌐 HTTP сервер запущен на порту {port}")
        
        last_schedule_check = datetime.now()
        
        while True:
            try:
                # Проверяем расписание каждую минуту
                now = datetime.now()
                if (now - last_schedule_check).seconds >= 60:
                    await self.check_schedule()
                    last_schedule_check = now
                
                # Получаем обновления
                updates = await self.get_updates()
                
                for update in updates:
                    self.last_update_id = update.get('update_id', 0)
                    
                    # Обрабатываем callback_query
                    if 'callback_query' in update:
                        callback_query = update['callback_query']
                        callback_data = callback_query.get('data', '')
                        callback_query_id = callback_query.get('id', '')
                        message = callback_query.get('message', {})
                        message_id = message.get('message_id', 0)
                        message_text = message.get('text', '')
                        
                        await self.process_callback(callback_data, callback_query_id, message_id, message_text)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Ошибка в главном цикле: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    bot = TaskTrackerBot()
    asyncio.run(bot.run())
