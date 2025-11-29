#!/usr/bin/env python3
"""
Telegram бот для отслеживания выполнения задач - ЭТАП 2
Полноценный чек-лист с inline-кнопками
"""

import asyncio
import aiohttp
from aiohttp import web
import json
import logging
from datetime import datetime, timedelta
import os
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskTrackerBot:
    def __init__(self):
        self.telegram_token = "8442392037:AAEiM_b4QfdFLqbmmc1PXNvA99yxmFVLEp8"
        self.chat_id = "350766421"
        self.stats_file = "stats.json"
        self.last_update_id = 0
        
        # Хранилище текущего состояния для каждого сообщения
        # {message_id: {'morning': [0,1,2], 'day': [0], 'evening': [], 'original_text': '...'}}
        self.message_state = {}
        
    def parse_tasks(self, message_text):
        """Парсит задачи из сообщения notifier.py"""
        tasks = {
            'morning': [],
            'day': [],
            'evening': []
        }
        
        lines = message_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Определяем секцию (убираем HTML теги для проверки)
            clean_line = line.replace('<b>', '').replace('</b>', '')
            
            if '☀️ Утренние задачи' in clean_line or 'Утренние задачи' in clean_line:
                current_section = 'morning'
                continue
            elif '🌤️ Дневные задачи' in clean_line or 'Дневные задачи' in clean_line:
                current_section = 'day'
                continue
            elif '🌙' in clean_line and 'Вечерн' in clean_line:
                # Вечернее сообщение может быть "🌙 Вечерний план" или "Вечерние задачи"
                current_section = 'evening'
                continue
            elif 'Вечерние задачи' in clean_line:
                current_section = 'evening'
                continue
            elif '⛔' in line or 'Нельзя' in line:
                # "Нельзя делать" - это не период, пропускаем
                current_section = None
                continue
            elif '🎯' in line or '💡' in line or '🙏' in line or '🎉' in line:
                # Конец задач
                current_section = None
                continue
            
            # Собираем задачи
            if current_section and line.startswith('•'):
                task_text = line[1:].strip()  # Убираем •
                if task_text:
                    tasks[current_section].append(task_text)
        
        logger.info(f"📋 Распарсено задач: утро={len(tasks['morning'])}, день={len(tasks['day'])}, вечер={len(tasks['evening'])}")
        return tasks
    
    def create_checklist_keyboard(self, tasks, completed):
        """Создаёт inline-клавиатуру с задачами"""
        keyboard = []
        
        # Утренние задачи
        if tasks['morning']:
            keyboard.append([{'text': '☀️ УТРЕННИЕ ЗАДАЧИ', 'callback_data': 'header'}])
            for idx, task in enumerate(tasks['morning']):
                is_done = idx in completed.get('morning', [])
                emoji = '☑️' if is_done else '☐'
                # Обрезаем длинный текст для кнопки
                short_task = task[:35] + '...' if len(task) > 35 else task
                keyboard.append([{
                    'text': f'{emoji} {idx+1}. {short_task}',
                    'callback_data': f'toggle_morning_{idx}'
                }])
        
        # Дневные задачи
        if tasks['day']:
            keyboard.append([{'text': '🌤️ ДНЕВНЫЕ ЗАДАЧИ', 'callback_data': 'header'}])
            for idx, task in enumerate(tasks['day']):
                is_done = idx in completed.get('day', [])
                emoji = '☑️' if is_done else '☐'
                short_task = task[:35] + '...' if len(task) > 35 else task
                keyboard.append([{
                    'text': f'{emoji} {idx+1}. {short_task}',
                    'callback_data': f'toggle_day_{idx}'
                }])
        
        # Вечерние задачи  
        if tasks['evening']:
            keyboard.append([{'text': '🌙 ВЕЧЕРНИЕ ЗАДАЧИ', 'callback_data': 'header'}])
            for idx, task in enumerate(tasks['evening']):
                is_done = idx in completed.get('evening', [])
                emoji = '☑️' if is_done else '☐'
                short_task = task[:35] + '...' if len(task) > 35 else task
                keyboard.append([{
                    'text': f'{emoji} {idx+1}. {short_task}',
                    'callback_data': f'toggle_evening_{idx}'
                }])
        
        # Кнопки управления
        keyboard.append([
            {'text': '💾 Сохранить', 'callback_data': 'save_progress'},
            {'text': '❌ Отмена', 'callback_data': 'cancel_update'}
        ])
        
        return {'inline_keyboard': keyboard}
    
    def format_checklist_message(self, tasks, completed):
        """Форматирует текст сообщения с чек-листом"""
        msg = "✅ <b>Отметь выполненные задачи:</b>\n\n"
        
        total_tasks = 0
        total_done = 0
        
        if tasks['morning']:
            msg += "☀️ <b>УТРЕННИЕ:</b>\n"
            for idx, task in enumerate(tasks['morning']):
                emoji = '☑' if idx in completed.get('morning', []) else '☐'
                msg += f"{emoji} {task}\n"
                total_tasks += 1
                if idx in completed.get('morning', []):
                    total_done += 1
            msg += "\n"
        
        if tasks['day']:
            msg += "🌤️ <b>ДНЕВНЫЕ:</b>\n"
            for idx, task in enumerate(tasks['day']):
                emoji = '☑' if idx in completed.get('day', []) else '☐'
                msg += f"{emoji} {task}\n"
                total_tasks += 1
                if idx in completed.get('day', []):
                    total_done += 1
            msg += "\n"
        
        if tasks['evening']:
            msg += "🌙 <b>ВЕЧЕРНИЕ:</b>\n"
            for idx, task in enumerate(tasks['evening']):
                emoji = '☑' if idx in completed.get('evening', []) else '☐'
                msg += f"{emoji} {task}\n"
                total_tasks += 1
                if idx in completed.get('evening', []):
                    total_done += 1
            msg += "\n"
        
        # Прогресс
        percentage = int((total_done / total_tasks * 100)) if total_tasks > 0 else 0
        msg += f"📊 <b>Прогресс:</b> {total_done}/{total_tasks} ({percentage}%)\n"
        
        return msg
    
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
                        error_text = await response.text()
                        logger.error(f"❌ Ошибка обновления: {response.status} - {error_text}")
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
            
            await self.toggle_task(message_id, period, task_idx)
            await self.answer_callback_query(callback_query_id)
        
        elif callback_data == 'save_progress':
            # Сохраняем прогресс
            await self.save_progress(message_id)
            await self.answer_callback_query(callback_query_id, "✅ Прогресс сохранён!")
        
        elif callback_data == 'cancel_update':
            # Отменяем обновление
            await self.cancel_update(message_id)
            await self.answer_callback_query(callback_query_id, "❌ Отменено")
        
        elif callback_data == 'header':
            # Заголовки не кликабельны
            await self.answer_callback_query(callback_query_id)
    
    async def show_checklist(self, message_id, original_message):
        """Показывает чек-лист для отметки задач"""
        # Парсим задачи
        tasks = self.parse_tasks(original_message)
        
        # Инициализируем состояние для этого сообщения
        if message_id not in self.message_state:
            self.message_state[message_id] = {
                'tasks': tasks,
                'completed': {'morning': [], 'day': [], 'evening': []},
                'original_text': original_message
            }
        
        # Формируем сообщение и клавиатуру
        state = self.message_state[message_id]
        text = self.format_checklist_message(state['tasks'], state['completed'])
        keyboard = self.create_checklist_keyboard(state['tasks'], state['completed'])
        
        await self.edit_message(message_id, text, keyboard)
    
    async def toggle_task(self, message_id, period, task_idx):
        """Переключает статус задачи"""
        if message_id not in self.message_state:
            logger.error(f"❌ Состояние для сообщения {message_id} не найдено")
            return
        
        state = self.message_state[message_id]
        completed = state['completed'][period]
        
        # Переключаем
        if task_idx in completed:
            completed.remove(task_idx)
            logger.info(f"☐ Задача {period}[{task_idx}] снята")
        else:
            completed.append(task_idx)
            logger.info(f"☑ Задача {period}[{task_idx}] отмечена")
        
        # Обновляем сообщение
        text = self.format_checklist_message(state['tasks'], state['completed'])
        keyboard = self.create_checklist_keyboard(state['tasks'], state['completed'])
        await self.edit_message(message_id, text, keyboard)
    
    async def save_progress(self, message_id):
        """Сохраняет прогресс в stats.json"""
        if message_id not in self.message_state:
            logger.error(f"❌ Состояние для сообщения {message_id} не найдено")
            return
        
        state = self.message_state[message_id]
        today_key = self.get_today_key()
        
        # Загружаем статистику
        stats = self.load_stats()
        
        # Считаем общие показатели
        total_completed = (
            len(state['completed']['morning']) +
            len(state['completed']['day']) +
            len(state['completed']['evening'])
        )
        total_tasks = (
            len(state['tasks']['morning']) +
            len(state['tasks']['day']) +
            len(state['tasks']['evening'])
        )
        
        percentage = int((total_completed / total_tasks * 100)) if total_tasks > 0 else 0
        
        # Сохраняем данные за сегодня
        stats[today_key] = {
            'morning': {
                'completed': state['completed']['morning'],
                'total': len(state['tasks']['morning'])
            },
            'day': {
                'completed': state['completed']['day'],
                'total': len(state['tasks']['day'])
            },
            'evening': {
                'completed': state['completed']['evening'],
                'total': len(state['tasks']['evening'])
            },
            'percentage': percentage,
            'points': total_completed,
            'max_points': total_tasks
        }
        
        # Сохраняем в файл
        if self.save_stats(stats):
            # Возвращаем исходное сообщение
            await self.cancel_update(message_id)
            
            # Отправляем подтверждение
            confirm_msg = f"✅ <b>Прогресс сохранён!</b>\n\n"
            confirm_msg += f"📊 Сегодня: {total_completed}/{total_tasks} задач ({percentage}%)\n"
            confirm_msg += f"💪 Отличная работа!"
            
            await self.send_telegram_message(confirm_msg)
            
            logger.info(f"💾 Прогресс сохранён: {percentage}%")
    
    async def cancel_update(self, message_id):
        """Отменяет обновление, возвращает исходное сообщение"""
        if message_id in self.message_state:
            original_text = self.message_state[message_id]['original_text']
            
            # Создаём кнопку "Обновить прогресс"
            keyboard = {
                'inline_keyboard': [
                    [{'text': '🔄 Обновить прогресс', 'callback_data': 'update_progress'}]
                ]
            }
            
            await self.edit_message(message_id, original_text, keyboard)
            
            # Очищаем состояние
            del self.message_state[message_id]
    
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
        
        while True:
            try:
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
