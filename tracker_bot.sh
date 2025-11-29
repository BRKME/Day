#!/bin/bash

# Скрипт управления Tracker Bot

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_SCRIPT="$SCRIPT_DIR/tracker_bot.py"
PID_FILE="$SCRIPT_DIR/tracker_bot.pid"
LOG_FILE="$SCRIPT_DIR/tracker_bot.log"

start() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "❌ Tracker Bot уже запущен (PID: $PID)"
            return 1
        else
            echo "⚠️  Найден старый PID файл, удаляю..."
            rm "$PID_FILE"
        fi
    fi
    
    echo "🚀 Запускаю Tracker Bot..."
    nohup python3 "$BOT_SCRIPT" >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "✅ Tracker Bot запущен (PID: $(cat $PID_FILE))"
    echo "📋 Логи: $LOG_FILE"
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ Tracker Bot не запущен (PID файл не найден)"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "🛑 Останавливаю Tracker Bot (PID: $PID)..."
        kill $PID
        
        # Ждём завершения
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  Процесс не завершился, принудительно убиваю..."
            kill -9 $PID
        fi
        
        rm "$PID_FILE"
        echo "✅ Tracker Bot остановлен"
    else
        echo "❌ Процесс не найден (PID: $PID)"
        rm "$PID_FILE"
        return 1
    fi
}

status() {
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ Tracker Bot не запущен"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Tracker Bot работает (PID: $PID)"
        echo "📋 Логи: $LOG_FILE"
        return 0
    else
        echo "❌ Tracker Bot не работает (найден старый PID: $PID)"
        rm "$PID_FILE"
        return 1
    fi
}

restart() {
    echo "🔄 Перезапускаю Tracker Bot..."
    stop
    sleep 2
    start
}

logs() {
    if [ ! -f "$LOG_FILE" ]; then
        echo "❌ Лог файл не найден"
        return 1
    fi
    
    if [ "$1" == "-f" ]; then
        tail -f "$LOG_FILE"
    else
        tail -n ${1:-50} "$LOG_FILE"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs "$2"
        ;;
    *)
        echo "Использование: $0 {start|stop|restart|status|logs [-f|N]}"
        echo ""
        echo "Команды:"
        echo "  start    - Запустить бота"
        echo "  stop     - Остановить бота"
        echo "  restart  - Перезапустить бота"
        echo "  status   - Проверить статус"
        echo "  logs     - Показать последние 50 строк логов"
        echo "  logs -f  - Следить за логами в реальном времени"
        echo "  logs N   - Показать последние N строк логов"
        exit 1
        ;;
esac
