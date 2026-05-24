"""
player_bot.py — бот-игрок для Telegram чата
Играет в слоты и кости с 10:00 до 22:00, раз в 10 минут (чередует).
Раз в 20 минут пишет провокационную фразу.

Настройки:
  PLAYER_TOKEN  — токен бота-игрока
  CHAT_ID       — ID чата (для групп отрицательное число)
  BET           — ставка
"""

import asyncio
import logging
import random
from datetime import datetime, time as dtime

from telegram import Bot

# ══════════════════════════════════════════════
#  НАСТРОЙКИ
# ══════════════════════════════════════════════

PLAYER_TOKEN = "5973570027:AAG3nUQPRZPz97qcYSC1Di8Ju_3xfTlRDug"      # вставь токен сюда
CHAT_ID      = -1003996705724     # ID чата
BET          = 100               # ставка

WORK_START = dtime(10, 0)
WORK_END   = dtime(22, 0)

GAME_INTERVAL   = 10 * 60   # 10 минут
PHRASE_INTERVAL = 20 * 60   # 20 минут

# ══════════════════════════════════════════════
#  ФРАЗЫ
# ══════════════════════════════════════════════

PHRASES = [
    "Ну что, кто рискнёт сыграть против меня? Или слабо? 😏",
    "Я уже выиграл больше, чем вы все вместе взятые. Факт. 💰",
    "Кто последний — тот лох. Я первый. Всегда. 😎",
    "Казино плачет, когда я захожу. Сегодня снова. 🎰",
    "Удача — это не случайность. Это я. 🍀",
    "Вы вообще играете или только смотрите? Зрители бесплатно не выигрывают. 👀",
    "Говорят, везёт дуракам. Значит, я гений — мне везёт в два раза больше. 🧠",
    "Пока вы думаете — я уже выиграл. Быстрее соображайте! ⚡",
    "Я не суеверный, но мои кости всегда падают правильно. Странно, да? 🎲",
    "Слоты крутятся — деньги льются. Присоединяйтесь или завидуйте молча. 🔄",
    "Сегодня особенно везёт. Чувствую нутром. Или это просто я такой. 🔥",
    "Ва-банк — это не стратегия. Это образ жизни. 🃏",
    "Новички пусть учатся. Я покажу, как это делается. 📚",
    "Риск — благородное дело. Трусость — нет. Выбирайте сами. ⚖️",
    "Мои кости знают своё дело. Лет пять уже вместе. 🎲",
    "Хочешь выиграть — сначала научись проигрывать. Я научился. Давно. 💪",
    "Сегодня я в ударе. Это не хвастовство, это медицинский факт. 🏆",
    "Кто не рискует — тот не пьёт шампанское. Я пью. Часто. 🥂",
    "Один раунд — и я снова в плюсе. Привычка. 📈",
    "Слабаки сидят тихо. Сильные — играют. Выбор очевиден. 💎",
]

# ══════════════════════════════════════════════
#  ЛОГИКА
# ══════════════════════════════════════════════

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)


def is_work_time() -> bool:
    now = datetime.now().time()
    return WORK_START <= now < WORK_END


def next_game_command(state: dict) -> str:
    """Чередует слоты и кости. Число для костей выбирается случайно."""
    if state["last_game"] == "slots":
        state["last_game"] = "dice"
        number = random.randint(1, 6)
        return f"кости {number} {BET}"
    else:
        state["last_game"] = "slots"
        return f"слоты {BET}"


def next_phrase(state: dict) -> str:
    idx = state["phrase_idx"] % len(PHRASES)
    state["phrase_idx"] += 1
    return PHRASES[idx]


async def game_loop(bot: Bot, state: dict):
    """Цикл игры — каждые ~10 минут."""
    while True:
        jitter = random.randint(-60, 60)
        await asyncio.sleep(GAME_INTERVAL + jitter)

        if not is_work_time():
            log.info("Не рабочее время, пропускаю игру.")
            continue

        cmd = next_game_command(state)
        try:
            await bot.send_message(chat_id=CHAT_ID, text=cmd)
            log.info(f"Отправил: {cmd}")
        except Exception as e:
            log.error(f"Ошибка отправки игры: {e}")


async def phrase_loop(bot: Bot, state: dict):
    """Цикл фраз — каждые ~20 минут. Старт через 5 мин после запуска."""
    await asyncio.sleep(5 * 60)

    while True:
        jitter = random.randint(-90, 90)
        await asyncio.sleep(PHRASE_INTERVAL + jitter)

        if not is_work_time():
            log.info("Не рабочее время, пропускаю фразу.")
            continue

        phrase = next_phrase(state)
        try:
            await bot.send_message(chat_id=CHAT_ID, text=phrase)
            log.info(f"Отправил фразу: {phrase[:50]}...")
        except Exception as e:
            log.error(f"Ошибка отправки фразы: {e}")


async def main():
    log.info("Бот-игрок запускается...")
    bot = Bot(token=PLAYER_TOKEN)
    me = await bot.get_me()
    log.info(f"Авторизован как @{me.username}")

    state = {
        "last_game": "dice",   # первым пойдут слоты
        "phrase_idx": 0,
    }

    await asyncio.gather(
        game_loop(bot, state),
        phrase_loop(bot, state),
    )


if __name__ == "__main__":
    asyncio.run(main())
