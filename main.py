from telethon.sync import TelegramClient, events
from telethon.tl.custom import Button
from database import User, session
from yookassa import Configuration, Payment
import asyncio

TELEGRAM_API_ID = 7248451
TELEGRAM_API_HASH = "db9b16eff233ee8dfd7c218138cb2e10"

channel_id = 2173040707
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
        [Button.inline("Информация интенсива", b"info")],
        [Button.inline("Оплатить интенсив", b"pay")],
        [Button.inline("Пройти тест", b"start_test")]
        ]
    await event.respond(f'Добро пожаловать в меню. \nТут ты можешь узнать больше о интенсиве, получить полезные ссылки, и пройти тест\n\nТвой послдений результат теста {user.test_counter}/21\n\nЧто бы открыть меню снова используй команду /menu', buttons=keyboard)

@client.on(events.NewMessage(pattern="/menu"))
async def start(event):
    await menu(event)



@client.on(events.CallbackQuery(data=b"pay"))
async def start_test(event):
    shop_id = '374651'
    secret_key = 'live_iiSRycMjbce_SzWoYs0EBBI46Iyw3gpGrbuik1gty0o'
    Configuration.configure(shop_id, secret_key)
    chat_id = event.chat_id
    # Создание платежа
    payment = Payment.create({
        "amount": {
            "value": "888.00",  # Сумма платежа
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://your-website.com/return_after_payment"
        },
        "capture": True,
        "description": "Оплата интенсива СамоценнаЯ"
    })

    # Отправка ссылки для оплаты пользователю
    payment_url = payment.confirmation.confirmation_url
    await client.send_message(chat_id, f"Пожалуйста, перейдите по ссылке для оплаты: {payment_url}")


@client.on(events.CallbackQuery(data=b"info"))
async def start_test(event):
    await event.respond('Тут будет информация про интенсиве')

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
            
            try:
                await conv.send_message(question_data["text"], buttons=[keyboard])
                response = await conv.get_response()
                answer = response.text
                correct_answer = question_data["correct_answer"]
                user = session.query(User).filter_by(telegram_id=event.sender_id).first()
                if answer == correct_answer:
                    user.test_counter += 1
                    session.commit()
                await response.delete()
            except asyncio.TimeoutError:
                break

# @client.on(events.CallbackQuery(data=b"start_podcast"))
# async def start_test(event):
#     channel_id = 2173040707
#     message_id = 3
#     await client.forward_messages(event.chat_id, message_id, channel_id, drop_author=True)

@client.on(events.CallbackQuery(data=b"start_podcast"))
async def start_test(event):
    channel_id = 2173040707
    message_id = 3
    await client.forward_messages(event.chat_id, message_id, channel_id, drop_author=True)
    keyboard = Button.inline("Я готова", b"ready")
    await event.respond('''Теперь, после прослушивания подкаста, предлагаю тебе так же выполнить задание на самоценность: 

Опиши свою внешность, что тебе в себе нравится, а что категорически не нравится.
Ты часто об этом думаешь и смотря на себя в зеркало постоянно акцентируешь свое внимание на этом. 

Также опиши свои достоинства и недостатки в своей личности. 
''', buttons=keyboard)

@client.on(events.NewMessage(pattern="/course"))
async def start_course_day_one(event):
    print('1')
    user = await event.get_sender()
    await event.respond(f'''Дорогая {user.first_name}
приветствую тебя на интенсиве «СамоценнаЯ»!

Он рассчитан на 5 дней, но создан таким образом, что ты можешь проходить его в своем темпе, но не более 14 дней. 

После чего доступ к нему у тебя закроется, это сделано с заботой о тебе.🤍''')
    
    join_chat = Button.url("Присоединиться к чату", "https://t.me/+-5Hrf4ZGFcFmZjU6")
    await event.respond('''Для наилучшего твоего результата помимо этого замечательного бота у тебя будет моя поддержка в общем чате интенсива. Там ты всегда можешь получить пояснения и поддержку от меня. Все участники интенсива смогут общаться внутри чата и делиться своими ощущениями, состоянием, проблемами и результатами.''', buttons=join_chat)

    continue_button = Button.inline("Продолжить", b"first_podcast_intro")
    await asyncio.sleep(5)
    await event.respond('''Отлично👍, 
мы закончили с пояснениями, 
а сейчас я предлагаю тебе послушать первый подкаст.⬇️

Важно❣️
После прослушивания пройди небольшой быстрый тест и выполни задания. 

На интенсиве нет ненужной для тебя информации и заданий, поэтому если ты действительно хочешь получить результат - ничего не пропускай, ведь ЗДЕСЬ НАЧИНАЕТСЯ ТВОЙ ПУТЬ К ОСОЗНАННОМУ ТВОРЕНИЮ!
''', buttons=continue_button)

@client.on(events.CallbackQuery(data=b"first_podcast_intro"))
async def first_podcast_intro(event):
    print('2')
    channel_id = 2173040707
    message_id = 4
    await client.forward_messages(event.chat_id, message_id, channel_id, drop_author=True)
    
    continue_button = Button.inline("Продолжить", b"first_podcast")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"first_podcast"))
async def first_podcast(event):
    print('3')
    channel_id = 2173040707
    message_id = 5
    await client.forward_messages(event.chat_id, message_id, channel_id, drop_author=True)
    
    continue_button = Button.inline("Продолжить", b"feedback_request")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"feedback_request"))
async def feedback_request(event):
    print('4')
    chat = event.chat_id
    async with client.conversation(chat) as conv:
        await conv.send_message('''Поделись: 
1. Сколько баллов от 1 до 10 ты бы поставила этому подкасту?

2. Какое общее впечатление у тебя от пройденного материала? - поделись в одном предложении

3. Какие есть вопросы ко мне после прослушивания? 
Что непонятно? 
Есть ли сопротивление к информации? 

''')
        try:
            response = await conv.get_response()  # Set your desired timeout here
        except asyncio.TimeoutError:
            await conv.send_message("Время ожидания вышло.")
            response = None

    continue_button = Button.inline("Продолжить", b"practic_podcast_intro")
    await event.respond('''Твое первое задание:

Прослушай практику «Задаю намерение» и приступай к её выполнению. 
Выполняя её ты научишься с легкостью получать желаемое, а также наполнять себя энергией.''', buttons=continue_button)

@client.on(events.CallbackQuery(data=b"practic_podcast_intro"))
async def practic_podcast_intro(event):
    print('5')
    channel_id = 2173040707
    message_id = 8
    await client.forward_messages(event.chat_id, message_id, channel_id, drop_author=True)

    join_chat = Button.url("Присоединиться к чату", "https://t.me/+-5Hrf4ZGFcFmZjU6")
    continue_button = Button.inline("Продолжить", b"test_intro")
    await event.respond('''После зафиксируй и опиши свои ощущения: что чувствовала в момент, что изменилось в тебе, возможно было сопротивление. 

Здесь нет мелочей -  все важно для результата, поэтому фиксируй абсолютно всё!

Обязательно поделись в чате интенсива своими наблюдениями, результатами и эмоциями. 
Это важно - поможет зафиксировать в сознании твои ощущения. 🤍
''', buttons=[join_chat, continue_button])
    
@client.on(events.CallbackQuery(data=b"test_intro"))
async def test_intro(event):
    print('6')
    continue_button = Button.inline("Продолжить", b"start_test_two")
    
    await event.respond('''Кстати, милая 🤍 если ты еще не проходила мой тест на самоценность - то скорее сделай это и узнай свои баллы. 

После обязательно прослушай подкаст про разницу самооценки и самоценности - это поможет понять ключевую разницу и осознать, что всеми известными и популярными способами невозможно обрести самоценность.
''', buttons=continue_button)

@client.on(events.CallbackQuery(data=b"start_test_two"))
async def start_test(event):
    print('7')
    user = session.query(User).filter_by(telegram_id=event.sender_id).first()
    if user:
        user.test_counter = 0
        session.commit()

    text = '''Я подготовила для тебя мой самый надежный тест на самоценность. Тебя ждет 21 вопрос, тест занимает не более 3 минут. Долго не раздумывай над ответом. То, что первое приходит в голову, то и есть верный ответ;) Ну что приступаем к тесту?''' 
    await event.respond(text)
    
    async with client.conversation(event.sender_id) as conv:
        for question_number, question_data in questions.items():
            keyboard = [
                Button.inline("Да", f"answer_yes_{question_number}"),
                Button.inline("Нет", f"answer_no_{question_number}")
            ]
            
            try:
                await conv.send_message(question_data["text"], buttons=keyboard)
                response = await conv.get_response()
                answer = await response.text
                correct_answer = question_data["correct_answer"]
                user = session.query(User).filter_by(telegram_id=event.sender_id).first()
                if answer == correct_answer:
                    user.test_counter += 1
                    session.commit()
                await response.delete()
            except asyncio.TimeoutError:
                break



@client.on(events.CallbackQuery(data=b"ready"))
async def ready(event):
    print('7')
    await event.respond('''Моё пояснение:

Если мы находим в своей внешности или в своей личности изъяны, то это лишь для того чтобы увидеть, что-то внутри себя, что хочет быть исправленным в нас. 

Ведь мы подсознательно знаем, кто мы есть на самом деле и насколько мы бесценны. 
И именно поэтому мы все стремимся к внутреннему собственному идеалу, 
но ищем его совсем не там. 

Мы пытаемся увидеть некорректность и проблему глазами, ведь именно так мы на проявленном физическом плане познаем мир, поэтому мы оцениваем себя и других по внешности и по их проявлению и достижениям. 

Но на самом деле внешний мир - это лишь отражение нашего внутреннего. И если что-то не нравится вовне, то это лишь потому что что-то не нравится внутри, 
в подсознательном стремлении к собственной самоценности. 🤍''')
    
    continue_button = Button.inline("Продолжить", b"end_of_day_one")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"end_of_day_one"))
async def end_of_day_one(event):
    print('8')
    channel_id = 2173040707
    message_id = 9
    await client.forward_messages(event.chat_id, message_id, channel_id, drop_author=True)

    join_chat = Button.url("Присоединиться к чату", "https://t.me/+-5Hrf4ZGFcFmZjU6")
    continue_button = Button.inline("Продолжить", b"day_two_intro")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"day_two_intro"))
async def day_two_intro(event):
    print('9')
    channel_id = 2173040707
    message_id = 11
    await client.forward_messages(event.chat_id, message_id, channel_id, drop_author=True)
    
    continue_button = Button.inline("Продолжить", b"podcast_day_two")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"podcast_day_two"))
async def podcast_day_two(event):
    print('10')
    channel_id = 2173040707
    await client.forward_messages(event.chat_id, 12, channel_id, drop_author=True)
    await client.forward_messages(event.chat_id, 13, channel_id, drop_author=True)
    
    continue_button = Button.inline("Продолжить", b"post_podcast_day_two")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"post_podcast_day_two"))
async def post_podcast_day_two(event):
    print('11')
    channel_id = 2173040707
    join_chat = Button.url("Присоединиться к чату", "https://t.me/+-5Hrf4ZGFcFmZjU6")
    await client.forward_messages(event.chat_id, 14, channel_id, drop_author=True)
    await event.respond("Не забывай про наш чат ⬇️", buttons=join_chat)

    continue_button = Button.inline("Продолжить", b"day_three_intro")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)
    
@client.on(events.CallbackQuery(data=b"day_three_intro"))
async def day_three_intro(event):
    print('12')
    channel_id = 2173040707
    await client.forward_messages(event.chat_id, 15, channel_id, drop_author=True)
    
    continue_button = Button.inline("Продолжить", b"day_three_podcast")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"day_three_podcast"))
async def day_three_podcast(event):
    print('13')
    channel_id = 2173040707
    await client.forward_messages(event.chat_id, 16, channel_id, drop_author=True)
    await client.forward_messages(event.chat_id, 17, channel_id, drop_author=True)
    
    continue_button = Button.inline("Продолжить", b"three_next")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"three_next"))
async def three_next(event):
    print('14')
    channel_id = 2173040707
    await client.forward_messages(event.chat_id, 18, channel_id, drop_author=True)
    await client.forward_messages(event.chat_id, 19, channel_id, drop_author=True)
    
    continue_button = Button.inline("Продолжить", b"post_three_next")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"post_three_next"))
async def post_three_next(event):
    print('15')
    channel_id = 2173040707
    await client.forward_messages(event.chat_id, 20, channel_id, drop_author=True)
    await client.forward_messages(event.chat_id, 40, channel_id, drop_author=True)
    continue_button = Button.inline("Продолжить", b"post_three_next_two")
    await event.respond("Продолжить", buttons=[continue_button])

@client.on(events.CallbackQuery(data=b"post_three_next_two"))
async def post_three_next(event):
    print('16')
    channel_id = 2173040707
    await client.forward_messages(event.chat_id, 21, channel_id, drop_author=True)
    await client.forward_messages(event.chat_id, 41, channel_id, drop_author=True)
    
    join_chat = Button.url("Присоединиться к чату", "https://t.me/+-5Hrf4ZGFcFmZjU6")
    continue_button = Button.inline("Продолжить", b"day_four_intro")
    await event.respond("После выполнения задания - обязательно поделись своими мыслями и ощущениями ", buttons=[join_chat, continue_button])


@client.on(events.CallbackQuery(data=b"day_four_intro"))
async def day_four_intro(event):
    print('17')
    channel_id = 2173040707
    await client.forward_messages(event.chat_id, 22, channel_id, drop_author=True)
    
    continue_button = Button.inline("Продолжить", b"four_podcast")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"four_podcast"))
async def four_podcast(event):
    print('18')
    channel_id = 2173040707
    await client.forward_messages(event.chat_id, 23, channel_id, drop_author=True)
    await client.forward_messages(event.chat_id, 24, channel_id, drop_author=True)
    
    continue_button = Button.inline("Продолжить", b"post_four_podcast")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"post_four_podcast"))
async def post_four_podcast(event):
    print('19')
    channel_id = 2173040707
    await client.forward_messages(event.chat_id, 25, channel_id, drop_author=True)
    
    join_chat = Button.url("Наш чат 👇", "https://t.me/+-5Hrf4ZGFcFmZjU6")
    await event.respond("Присоединиться", buttons=join_chat)

    continue_button = Button.inline("Продолжить", b"continue_four")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"continue_four"))
async def continue_four(event):
    print('20')
    channel_id = 2173040707
    await client.forward_messages(event.chat_id, 26, channel_id, drop_author=True)
    await client.forward_messages(event.chat_id, 27, channel_id, drop_author=True)
    await client.forward_messages(event.chat_id, 42, channel_id, drop_author=True)
    continue_button = Button.inline("Продолжить", b"file_one")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

# @client.on(events.CallbackQuery(data=b"four_part_two"))
# async def four_part_two(event):
#     print('21')
#     channel_id = 2173040707
#     await client.forward_messages(event.chat_id, 29, channel_id, drop_author=True)
#     await client.forward_messages(event.chat_id, 38, channel_id, drop_author=True)
    
#     continue_button = Button.inline("Продолжить", b"file_one")
#     await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"file_one"))
async def four_part_two(event):
    print('22')
    await client.forward_messages(event.chat_id, 28, channel_id, drop_author=True)
    await client.forward_messages(event.chat_id, 43, channel_id, drop_author=True)
    continue_button = Button.inline("Продолжить", b"file_two")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"file_two"))
async def four_part_two(event):
    print('23')
    await client.forward_messages(event.chat_id, 30, channel_id, drop_author=True)
    await client.forward_messages(event.chat_id, 44, channel_id, drop_author=True)
    continue_button = Button.inline("Продолжить", b"file_three")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"file_three"))
async def four_part_two(event):
    print('24')
    await client.forward_messages(event.chat_id, 31, channel_id, drop_author=True)
    await client.forward_messages(event.chat_id, 45, channel_id, drop_author=True)
    continue_button = Button.inline("Продолжить", b"file_four")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"file_four"))
async def four_part_two(event):
    print('25')
    await event.respond("Памятка")
    await client.forward_messages(event.chat_id, 46, channel_id, drop_author=True)
    continue_button = Button.inline("Продолжить", b"day_five_intro")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"day_five_intro"))
async def day_five_intro(event):
    print('25')
    channel_id = 2173040707
    await client.forward_messages(event.chat_id, 32, channel_id, drop_author=True)
    await client.forward_messages(event.chat_id, 33, channel_id, drop_author=True)
    
    continue_button = Button.inline("Продолжить", b"day_five_part_two")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"day_five_part_two"))
async def day_five_part_two(event):
    print('26')
    await client.forward_messages(event.chat_id, 34, channel_id, drop_author=True)
    continue_button = Button.inline("Продолжить", b"day_five_part_three")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"day_five_part_three"))
async def day_five_part_three(event):
    print('27')
    await client.forward_messages(event.chat_id, 35, channel_id, drop_author=True)
    continue_button = Button.inline("Продолжить", b"day_five_part_four")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"day_five_part_four"))
async def day_five_part_four(event):
    print('28')
    await client.forward_messages(event.chat_id, 36, channel_id, drop_author=True)
    continue_button = Button.inline("Продолжить", b"day_five_part_five")
    await event.respond("Нажми что бы продолжить", buttons=continue_button)

@client.on(events.CallbackQuery(data=b"day_five_part_five"))
async def day_five_part_five(event):
    print('29')
    await client.forward_messages(event.chat_id, 37, channel_id, drop_author=True)

client.start()
client.run_until_disconnected()
