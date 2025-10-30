#!/usr/bin/env python3
"""
Personal Daily Schedule Notifier - Simple Version
"""

import asyncio
import aiohttp
from datetime import datetime

class PersonalScheduleNotifier:
    def __init__(self):
        # Telegram settings
        self.telegram_token = "8442392037:AAEiM_b4QfdFLqbmmc1PXNvA99yxmFVLEp8"
        self.chat_id = "350766421"
    
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
                    response_text = await response.text()
                    print(f"📨 Response status: {response.status}")
                    
                    if response.status == 200:
                        print("✅ Telegram message sent successfully!")
                        return True
                    else:
                        print(f"❌ Telegram API error: {response_text}")
                        return False
        except Exception as e:
            print(f"❌ Failed to send Telegram message: {e}")
            return False

async def main():
    """Simple test function"""
    print("🚀 Starting simple test...")
    
    # Get current time
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%d.%m.%Y")
    
    print(f"🕐 Current time: {current_time}")
    print(f"📅 Current date: {current_date}")
    
    notifier = PersonalScheduleNotifier()
    
    # Test message
    test_message = f"🧪 <b>Test Message from GitHub</b>\n"
    test_message += f"📅 Date: {current_date}\n"
    test_message += f"🕐 Time: {current_time}\n"
    test_message += f"🔧 GitHub Actions Test\n"
    test_message += f"✅ If you see this, everything works!"
    
    success = await notifier.send_telegram_message(test_message)
    
    if success:
        print("🎉 Test completed successfully!")
    else:
        print("💥 Test failed!")

if __name__ == "__main__":
    asyncio.run(main())
