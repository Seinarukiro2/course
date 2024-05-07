from telethon.sync import TelegramClient, events
from telethon.tl.custom import Button
from database import User, session


TELEGRAM_API_ID = 7248451
TELEGRAM_API_HASH = "db9b16eff233ee8dfd7c218138cb2e10"


client = TelegramClient("session_name", TELEGRAM_API_ID, TELEGRAM_API_HASH)

questions = {
    1: {"text": "Ты уверенный в себе человек?", "correct_answer": "yes"},
    2: {"text": "Как ты считаешь: у тебя достаточно энергии?", "correct_answer": "yes"},
    3: {"text": "Чувства стресса и страха частые твои гости?", "correct_answer": "no"},
    4: {
        "text": "Довольна ли ты своими отношениями с близкими?",
        "correct_answer": "yes",
    },
    5: {"text": "Довольна ли ты своим отношением к себе?", "correct_answer": "yes"},
    6: {"text": "Часто ли ты испытываешь чувство вины?", "correct_answer": "no"},
    7: {"text": "Часто ли ты чувствуешь себя счастливой?", "correct_answer": "yes"},
    8: {"text": "Окружающие относятся к тебе справедливо?", "correct_answer": "yes"},
    9: {"text": "Как ты считаешь есть судьба?", "correct_answer": "no"},
    10: {
        "text": "Ты сложно перенесла условия карантина? (Закрытие границ, изоляция от общества)",
        "correct_answer": "no",
    },
    11: {
        "text": "Стараешься ли ты избегать конфликтных ситуаций?",
        "correct_answer": "no",
    },
    12: {
        "text": "Из-за страха совершить ошибку, боишься ли ты перемен?",
        "correct_answer": "no",
    },
    13: {
        "text": "Критика от окружающих отнимает у тебя энергию?",
        "correct_answer": "no",
    },
    14: {
        "text": "Чувствуешь ли ты себя неловко во время секса?",
        "correct_answer": "no",
    },
    15: {
        "text": "Часто ли ты не понимаешь, что присходит с тобой или с твоей жизнью?",
        "correct_answer": "no",
    },
    16: {"text": "Тебе важно мнение окружающих?", "correct_answer": "no"},
    17: {"text": "Довольна ли ты отношениями с партнером?", "correct_answer": "yes"},
    18: {"text": "Ты в мыслях любишь возвращаться в прошлое?", "correct_answer": "no"},
    19: {
        "text": "Другие часто хотят тебя использовать в своих интересах?",
        "correct_answer": "no",
    },
    20: {"text": "Свое завтра ты видишь счастливым?", "correct_answer": "yes"},
    21: {"text": "Ты всецело доверяешь себе?", "correct_answer": "yes"},
}


@client.on(events.CallbackQuery(pattern=b"answer_(yes|no)_\d+"))
async def handle_answer(event):
    answer = event.data.decode("utf-8").split("_")[1]
    question_number = int(event.data.decode("utf-8").split("_")[-1])
    correct_answer = questions[question_number]["correct_answer"]

    user = session.query(User).filter_by(telegram_id=event.sender_id).first()
    if not user:
        await event.answer("Сначала введите команду /start")
        return

    if answer == correct_answer:
        user.test_counter += 1
        session.commit()

    await event.answer()

    next_question_number = question_number + 1
    if next_question_number in questions:
        next_question_data = questions[next_question_number]
        keyboard = Button.inline(
            "Да", f"answer_yes_{next_question_number}"
        ), Button.inline("Нет", f"answer_no_{next_question_number}")
        await event.edit(next_question_data["text"], buttons=[keyboard])
    else:
        await event.edit(
            f"Поздравляю тебя с прохождением теста! Я специально для тебя записала аудио-рекоменадцию.\n\nТвое количество баллов - {user.test_counter}"
        )
        audio_file = None
        if user.test_counter >= 0 and user.test_counter <= 7:
            audio_file = "audio/0-7.m4a"
        elif user.test_counter >= 8 and user.test_counter <= 17:
            audio_file = "audio/8-17.m4a"
        elif user.test_counter >= 18 and user.test_counter <= 21:
            audio_file = "audio/18-21.m4a"

        if audio_file:
            await event.respond("Аудио-рекомендация", file=audio_file)
        await event.respond("Теперь пришло время прослушать подкаст!", buttons=Button.inline("Получить подкаст", f"start_podcast"))


async def menu(event):
    user = session.query(User).filter_by(telegram_id=event.sender_id).first()
    keyboard = [
        [Button.inline("Информация о курсе", b"info")],
        [Button.inline("Оплатить курс", b"pay")],
        [Button.inline("Пройти тест", b"start_test")]
        ]
    await event.respond(f'Добро пожаловать в меню. \nТут ты можешь узнать больше о курсе, получить полезные ссылки, и пройти тест\n\nТвой послдений результат теста {user.test_counter}/21\n\nЧто бы открыть меню снова используй команду /menu', buttons=keyboard)

@client.on(events.NewMessage(pattern="/menu"))
async def start(event):
    await menu(event)

@client.on(events.CallbackQuery(data=b"pay"))
async def start_test(event):
    await event.respond('Тут будет инструкция для оплаты курса. \n\n После оплаты пользователь получит материал курса или будет получать его раз в день')

@client.on(events.CallbackQuery(data=b"info"))
async def start_test(event):
    await event.respond('Тут будет информация о курсе')

@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    user = session.query(User).filter_by(telegram_id=event.sender_id).first()
    if not user:
        new_user = User(telegram_id=event.sender_id)
        session.add(new_user)
        session.commit()
    await menu(event)
    keyboard = Button.inline("Начать тест", b"start_test")
    text = ''' Для того, чтобы открыть дверь в подсознание, нужны ключи.🔑 
И чтобы мы скорей их нашли, необходимо пройти тест на «САМОЦЕННОСТЬ».
Кнопка ниже ⬇️ 

НЕ откладывайте,
сделайте это прямо сейчас 🙂 
''' 
    await event.respond(
        text, buttons=keyboard
    )

@client.on(events.NewMessage(pattern="/get"))
async def start(event):
    await event.respond(event.chat_id)



@client.on(events.CallbackQuery(data=b"start_test"))
async def start_test(event):
    user = session.query(User).filter_by(telegram_id=event.sender_id).first()
    if user:
        user.test_counter = 0
        session.commit()
    text = '''Я подготовила для тебя мой самый надежный тест на самоценность. Тебя ждет 21 вопрос, тест занимает не более 3 минут. Долго не раздумывай над ответом. То, что первое приходит в голову, то и есть верный ответ;) Ну что приступаем к тесту?''' 
    await event.respond(text)
    async with client.conversation(event.sender_id) as conv:
        for question_number, question_data in questions.items():
            keyboard = Button.inline(
                "Да", f"answer_yes_{question_number}"
            ), Button.inline("Нет", f"answer_no_{question_number}")
            await conv.send_message(question_data["text"], buttons=[keyboard])
            response = await conv.get_response(timeout=60)
            answer = response.text
            correct_answer = question_data["correct_answer"]
            user = session.query(User).filter_by(telegram_id=event.sender_id).first()
            if answer == correct_answer:
                user.test_counter += 1
                session.commit()
            await response.delete()

@client.on(events.CallbackQuery(data=b"start_podcast"))
async def start_test(event):
    channel_id = -1002013957579
    message_id = 5
    await client.forward_messages(event.chat_id, message_id, channel_id, drop_author=True)

client.start()
client.run_until_disconnected()
