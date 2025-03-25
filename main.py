import logging
import json

from telegram import InputMediaPhoto, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

with open("token.txt", "r") as f:
    API_TOKEN = f.read()
GROUP_CHAT_ID = -1002247296794
EVAL_CHAT_ID = -1002220082696

with open('message_texts.json', 'r', encoding='utf-8') as file:
    message_texts = json.load(file)

def get_message_text(key: str, language: str = 'lang_ru') -> str:
    return message_texts.get(key, {}).get(language, '')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    keyboard = [
        [InlineKeyboardButton("Кыргызча", callback_data='lang_ky')],
        [InlineKeyboardButton("Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("English", callback_data='lang_en')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data['registration_step'] = 'language_selection'
    await update.message.reply_text(message_texts['choose_language'], reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    language = context.user_data.get('language', 'lang_ru')
    await update.message.reply_text(get_message_text('help', language))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    language = context.user_data.get('language', 'lang_ru')

    if context.user_data.get('registration_step', '') == '':
        context.user_data['registration_step'] = 'start'
        keyboard = [
            [InlineKeyboardButton(get_message_text('Баштоо/Начать/Start', language), callback_data='start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message_texts['start_message'])

    elif context.user_data['registration_step'] == 'start':
        if query.data == 'start':
            context.user_data.clear()
            keyboard = [
                [InlineKeyboardButton("Кыргызча", callback_data='lang_ky')],
                [InlineKeyboardButton("Русский", callback_data='lang_ru')],
                [InlineKeyboardButton("English", callback_data='lang_en')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.user_data['registration_step'] = 'language_selection'
            await query.edit_message_text(message_texts['choose_language'], reply_markup=reply_markup)

    elif context.user_data['registration_step'] == 'evaluation_rating':
        rating = query.data
        context.user_data['rating'] = rating
        context.user_data['registration_step'] = 'provide_evaluation'
        keyboard = [
                    [InlineKeyboardButton(get_message_text('yes', language), callback_data='yes_eval')],
                    [InlineKeyboardButton(get_message_text('no', language), callback_data='no_eval')]
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)   
        await query.edit_message_text(get_message_text('provide_evaluation', language), reply_markup=reply_markup)
        
    elif context.user_data['registration_step'] == 'provide_evaluation':
        if query.data == 'yes_eval':
            context.user_data['registration_step'] = 'evaluation_details'
            await query.edit_message_text(get_message_text('evaluation_details', language))
        else:
            rating = context.user_data['rating']
            await context.bot.send_message(chat_id=EVAL_CHAT_ID, text=f'Rating: {rating}')
            await query.edit_message_text(get_message_text('complete_evaluation', language))
            context.user_data.clear()
    
    elif context.user_data['registration_step'] == 'language_selection':
        language = query.data
        context.user_data['language'] = language
        keyboard = [
            [InlineKeyboardButton(get_message_text('home_sewer', language), callback_data='home_sewer')],
            [InlineKeyboardButton(get_message_text('sewer_in_factory', language), callback_data='sewer_in_factory')],
            [InlineKeyboardButton(get_message_text('factory', language), callback_data='factory')],
            [InlineKeyboardButton(get_message_text('technologist', language), callback_data='technologist')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['registration_step'] = 1
        await query.edit_message_text(get_message_text('choose_role', language), reply_markup=reply_markup)
            
    elif context.user_data['registration_step'] == 1:
        role = query.data
        context.user_data['role'] = role
        context.user_data['registration_step'] = 2
        if role == 'factory':
            message = 'role_selected_factory'
        else:
            message = 'role_selected'
        await query.edit_message_text(text=get_message_text(message, language).format(get_message_text(role, language)))
    
    elif context.user_data['role'] == 'factory':
        if context.user_data['registration_step'] == 2.5:
            role = query.data
            context.user_data['factory_searching_role'] = role
            keyboard = [
                [InlineKeyboardButton(get_message_text('phone_number', language), callback_data='phone')],
                [InlineKeyboardButton('Telegram', callback_data='telegram')],
                [InlineKeyboardButton('WhatsApp', callback_data='whatsapp')],
                [InlineKeyboardButton('Email', callback_data='email')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.user_data['registration_step'] = 3
            await query.edit_message_text(get_message_text('provide_contact_details', language), reply_markup=reply_markup)
            
        elif context.user_data['registration_step'] == 3:
            contact_type = query.data
            if contact_type == 'done':
                context.user_data['registration_step'] = 4
                await query.edit_message_text(text=get_message_text('provide_address', language))
            elif contact_type == 'telegram':
                keyboard = [
                    [InlineKeyboardButton(get_message_text('use_current_telegram', language), callback_data='use_current_telegram')],
                    [InlineKeyboardButton(get_message_text('use_other_telegram', language), callback_data='use_other_telegram')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.user_data['current_contact'] = contact_type
                context.user_data['registration_step'] = 3.5
                await query.edit_message_text(text=get_message_text('telegram_choice', language), reply_markup=reply_markup)
            else:
                context.user_data['current_contact'] = contact_type
                context.user_data['registration_step'] = 3.5
                await query.edit_message_text(text=get_message_text('provide_contact_details', language))

        elif context.user_data['registration_step'] == 3.5 and query.data in ['use_current_telegram', 'use_other_telegram']:
            telegram_choice = query.data
            if telegram_choice == 'use_current_telegram':
                if 'contacts' not in context.user_data:
                    context.user_data['contacts'] = {}
                if 'telegram' not in context.user_data['contacts']:
                    context.user_data['contacts']['telegram'] = []
                if query.from_user.username and query.from_user.username not in context.user_data['contacts']['telegram']:
                    context.user_data['contacts']['telegram'].append(query.from_user.username)
                keyboard = [
                    [InlineKeyboardButton(get_message_text('phone_number', language), callback_data='phone')],
                    [InlineKeyboardButton('Telegram', callback_data='telegram')],
                    [InlineKeyboardButton('WhatsApp', callback_data='whatsapp')],
                    [InlineKeyboardButton('Email', callback_data='email')],
                    [InlineKeyboardButton(get_message_text('done', language), callback_data='done')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.user_data['registration_step'] = 3
                await query.edit_message_text(text=get_message_text('using_current_telegram', language).format(query.from_user.username), reply_markup=reply_markup)
            else:
                context.user_data['registration_step'] = 3.6
                await query.edit_message_text(text=get_message_text('provide_telegram_username', language))
        
        elif context.user_data['registration_step'] == 5.5:
            text = query.data
            if text.lower() == 'yes':
                context.user_data['registration_step'] = 6
                await query.edit_message_text(get_message_text('salary_details', language))
            else:
                context.user_data['registration_step'] = 6.5
                keyboard = [
                    [InlineKeyboardButton(get_message_text('yes', language), callback_data='yes_images')],
                    [InlineKeyboardButton(get_message_text('no', language), callback_data='no_images')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(get_message_text('provide_images_factory', language), reply_markup=reply_markup)

        elif context.user_data['registration_step'] == 6.5:
            if query.data == 'yes_images':
                context.user_data['registration_step'] = 7
                await query.edit_message_text(get_message_text('upload_images', language))
            else:
                context.user_data['images'] = []
                await complete_registration(query, context)

        elif query.data == 'done_images':
            await complete_registration(query, context)
            
    elif context.user_data['role'] in ['home_sewer', 'sewer_in_factory', 'technologist']:
        if context.user_data['registration_step'] == 3:
            contact_type = query.data
            if contact_type == 'done':
                context.user_data['registration_step'] = 4
                await query.edit_message_text(text=get_message_text('provide_experience_years', language))
            elif contact_type == 'telegram':
                keyboard = [
                    [InlineKeyboardButton(get_message_text('use_current_telegram', language), callback_data='use_current_telegram')],
                    [InlineKeyboardButton(get_message_text('use_other_telegram', language), callback_data='use_other_telegram')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.user_data['current_contact'] = contact_type
                context.user_data['registration_step'] = 3.5
                await query.edit_message_text(text=get_message_text('telegram_choice', language), reply_markup=reply_markup)
            else:
                context.user_data['current_contact'] = contact_type
                context.user_data['registration_step'] = 3.5
                await query.edit_message_text(text=get_message_text('provide_contact_details', language))

        elif context.user_data['registration_step'] == 3.5 and query.data in ['use_current_telegram', 'use_other_telegram']:
            telegram_choice = query.data
            if telegram_choice == 'use_current_telegram':
                if 'contacts' not in context.user_data:
                    context.user_data['contacts'] = {}
                if 'telegram' not in context.user_data['contacts']:
                    context.user_data['contacts']['telegram'] = []
                if query.from_user.username and query.from_user.username not in context.user_data['contacts']['telegram']:
                    context.user_data['contacts']['telegram'].append(query.from_user.username)
                keyboard = [
                    [InlineKeyboardButton(get_message_text('phone_number', language), callback_data='phone')],
                    [InlineKeyboardButton('Telegram', callback_data='telegram')],
                    [InlineKeyboardButton('WhatsApp', callback_data='whatsapp')],
                    [InlineKeyboardButton('Email', callback_data='email')],
                    [InlineKeyboardButton(get_message_text('done', language), callback_data='done')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.user_data['registration_step'] = 3
                await query.edit_message_text(text=get_message_text('using_current_telegram', language).format(query.from_user.username), reply_markup=reply_markup)
            else:
                context.user_data['registration_step'] = 3.6
                await query.edit_message_text(text=get_message_text('provide_telegram_username', language))

        elif context.user_data['registration_step'] == 4.5:
            text = query.data
            if text.lower() == 'yes':
                context.user_data['registration_step'] = 5
                await query.edit_message_text(get_message_text('work_experience_details', language))
            else:
                context.user_data['registration_step'] = 5.5
                keyboard = [
                    [InlineKeyboardButton(get_message_text('yes', language), callback_data='yes')],
                    [InlineKeyboardButton(get_message_text('no', language), callback_data='no')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(get_message_text('provide_factories', language), reply_markup=reply_markup)

        elif context.user_data['registration_step'] == 5.5:
            text = query.data
            if text.lower() == 'yes':
                context.user_data['registration_step'] = 6
                await query.edit_message_text(get_message_text('factories_list', language))
            else:
                context.user_data['factories'] = ''
                context.user_data['registration_step'] = 7
                keyboard = [
                    [InlineKeyboardButton(get_message_text('shirts', language), callback_data='shirts')],
                    [InlineKeyboardButton(get_message_text('pants', language), callback_data='pants')],
                    [InlineKeyboardButton(get_message_text('jackets', language), callback_data='jackets')],
                    [InlineKeyboardButton(get_message_text('sweaters', language), callback_data='sweaters')],
                    [InlineKeyboardButton(get_message_text('other', language), callback_data='other')],
                    [InlineKeyboardButton(get_message_text('done', language), callback_data='done_products')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(get_message_text('provide_products', language), reply_markup=reply_markup)

        elif context.user_data['registration_step'] == 7:
            if query.data == 'done_products':
                context.user_data['registration_step'] = 8
                keyboard = [
                    [InlineKeyboardButton(get_message_text('yes', language), callback_data='yes_orders')],
                    [InlineKeyboardButton(get_message_text('no', language), callback_data='no_orders')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(get_message_text('provide_orders', language), reply_markup=reply_markup)
            elif query.data == 'other':
                context.user_data['registration_step'] = 7.5
                await query.edit_message_text(get_message_text('provide_other_products', language))
            else:
                if 'products' not in context.user_data:
                    context.user_data['products'] = []
                if query.data not in context.user_data['products']:
                    context.user_data['products'].append(query.data)
                    if not query.message.text == get_message_text('product_added', language):
                        await query.edit_message_text(get_message_text('product_added', language), reply_markup=query.message.reply_markup)
                else:
                    if not query.message.text == get_message_text('product_already_added', language):
                        await query.edit_message_text(get_message_text('product_already_added', language), reply_markup=query.message.reply_markup)

        elif context.user_data['registration_step'] == 8:
            if query.data == 'yes_orders':
                context.user_data['registration_step'] = 8.5
                await query.edit_message_text(get_message_text('provide_orders_details', language))
            else:
                context.user_data['completed_orders'] = ''
                context.user_data['registration_step'] = 9
                keyboard = [
                    [InlineKeyboardButton(get_message_text('yes', language), callback_data='yes_images')],
                    [InlineKeyboardButton(get_message_text('no', language), callback_data='no_images')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(get_message_text('provide_images', language), reply_markup=reply_markup)

        elif context.user_data['registration_step'] == 9:
            if query.data == 'yes_images':
                context.user_data['registration_step'] = 9.5
                await query.edit_message_text(get_message_text('upload_images', language))
            else:
                context.user_data['images'] = []
                await complete_registration(query, context)

        elif query.data == 'done_images':
            await complete_registration(query, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    language = context.user_data.get('language', 'lang_ru')

    if context.user_data.get('registration_step', '') == '' or context.user_data.get('registration_step', '') == 'start':
        context.user_data['registration_step'] = 'start'
        keyboard = [
            [InlineKeyboardButton('Баштоо/Начать/Start', callback_data='start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message_texts['start_message'], reply_markup=reply_markup)

    elif context.user_data['registration_step'] == 'evaluation_details':
        context.user_data['evaluation_details'] = update.message.text
        rating = context.user_data['rating']
        await update.message.reply_text(get_message_text('complete_evaluation', language))
        await context.bot.send_message(chat_id=EVAL_CHAT_ID, text=f'Rating: {rating}\nFeedback: {update.message.text}')

        context.user_data.clear()

    elif context.user_data['role'] == 'factory':
        if context.user_data.get('registration_step') == 2:
            context.user_data['factory_name'] = update.message.text
            context.user_data['registration_step'] = 2.5
            keyboard = [
                [InlineKeyboardButton(get_message_text('home_sewer', language), callback_data='home_sewer')],
                [InlineKeyboardButton(get_message_text('sewer_in_factory', language), callback_data='sewer_in_factory')],
                [InlineKeyboardButton(get_message_text('technologist', language), callback_data='technologist')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(get_message_text('factory_searching_role', language), reply_markup=reply_markup)
        
        elif context.user_data.get('registration_step') == 3.5:
            if 'contacts' not in context.user_data:
                context.user_data['contacts'] = {}
            if context.user_data['current_contact'] not in context.user_data['contacts']:
                context.user_data['contacts'][context.user_data['current_contact']] = []
            if update.message.text not in  context.user_data['contacts'][context.user_data['current_contact']]:
                context.user_data['contacts'][context.user_data['current_contact']].append(update.message.text)
            keyboard = [
                [InlineKeyboardButton(get_message_text('phone_number', language), callback_data='phone')],
                [InlineKeyboardButton('Telegram', callback_data='telegram')],
                [InlineKeyboardButton('WhatsApp', callback_data='whatsapp')],
                [InlineKeyboardButton('Email', callback_data='email')],
                [InlineKeyboardButton(get_message_text('done', language), callback_data='done')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.user_data['registration_step'] = 3
            await update.message.reply_text(get_message_text('contact_details_saved', language), reply_markup=reply_markup)

        elif context.user_data.get('registration_step') == 3.6:
            context.user_data['telegram'] = update.message.text
            if 'contacts' not in context.user_data:
                context.user_data['contacts'] = {}
            if 'telegram' not in context.user_data['contacts']:
                context.user_data['contacts']['telegram'] = []
            if update.message.text not in context.user_data['contacts']['telegram']:
                context.user_data['contacts']['telegram'].append(update.message.text)
            keyboard = [
                [InlineKeyboardButton(get_message_text('phone_number', language), callback_data='phone')],
                [InlineKeyboardButton('Telegram', callback_data='telegram')],
                [InlineKeyboardButton('WhatsApp', callback_data='whatsapp')],
                [InlineKeyboardButton('Email', callback_data='email')],
                [InlineKeyboardButton(get_message_text('done', language), callback_data='done')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.user_data['registration_step'] = 3
            await update.message.reply_text(get_message_text('telegram_contact_saved', language), reply_markup=reply_markup)

        elif context.user_data.get('registration_step') == 4:
            context.user_data['address'] = update.message.text
            context.user_data['registration_step'] = 5
            await update.message.reply_text(get_message_text('provide_order_details', language))

        elif context.user_data.get('registration_step') == 5:
            context.user_data['order_details'] = update.message.text
            keyboard = [
                [InlineKeyboardButton(get_message_text('yes', language), callback_data='yes')],
                [InlineKeyboardButton(get_message_text('no', language), callback_data='no')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.user_data['registration_step'] = 5.5
            await update.message.reply_text(get_message_text('provide_salary', language), reply_markup=reply_markup)
        
        elif context.user_data.get('registration_step') == 6:
            context.user_data['salary'] = update.message.text
            context.user_data['registration_step'] = 6.5
            keyboard = [
                [InlineKeyboardButton(get_message_text('yes', language), callback_data='yes_images')],
                [InlineKeyboardButton(get_message_text('no', language), callback_data='no_images')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(get_message_text('provide_images', language), reply_markup=reply_markup)

        elif context.user_data.get('registration_step') == 7:
            keyboard = [
                [InlineKeyboardButton(get_message_text('done', language), callback_data='done_images')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if 'images' not in context.user_data:
                context.user_data['images'] = []
            if update.message.photo:
                photo_file_id = update.message.photo[-1].file_id
                context.user_data['images'].append(photo_file_id)
                await update.message.reply_text(get_message_text('image_received', language), reply_markup=reply_markup)
            else:
                await update.message.reply_text(get_message_text('upload_image', language), reply_markup=reply_markup)

    elif context.user_data['role'] in ['home_sewer', 'sewer_in_factory', 'technologist']:
        if context.user_data.get('registration_step') == 2:
            context.user_data['full_name'] = update.message.text
            context.user_data['registration_step'] = 3
            keyboard = [
                [InlineKeyboardButton(get_message_text('phone_number', language), callback_data='phone')],
                [InlineKeyboardButton('Telegram', callback_data='telegram')],
                [InlineKeyboardButton('WhatsApp', callback_data='whatsapp')],
                [InlineKeyboardButton('Email', callback_data='email')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(get_message_text('provide_contact_details', language), reply_markup=reply_markup)

        elif context.user_data.get('registration_step') == 3.5:
            if 'contacts' not in context.user_data:
                context.user_data['contacts'] = {}
            if context.user_data['current_contact'] not in context.user_data['contacts']:
                context.user_data['contacts'][context.user_data['current_contact']] = []
            if update.message.text not in  context.user_data['contacts'][context.user_data['current_contact']]:
                context.user_data['contacts'][context.user_data['current_contact']].append(update.message.text)
            keyboard = [
                [InlineKeyboardButton(get_message_text('phone_number', language), callback_data='phone')],
                [InlineKeyboardButton('Telegram', callback_data='telegram')],
                [InlineKeyboardButton('WhatsApp', callback_data='whatsapp')],
                [InlineKeyboardButton('Email', callback_data='email')],
                [InlineKeyboardButton(get_message_text('done', language), callback_data='done')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.user_data['registration_step'] = 3
            await update.message.reply_text(get_message_text('contact_details_saved', language), reply_markup=reply_markup)

        elif context.user_data.get('registration_step') == 3.6:
            context.user_data['telegram'] = update.message.text
            if 'contacts' not in context.user_data:
                context.user_data['contacts'] = {}
            if 'telegram' not in context.user_data['contacts']:
                context.user_data['contacts']['telegram'] = []
            if update.message.text not in context.user_data['contacts']['telegram']:
                context.user_data['contacts']['telegram'].append(update.message.text)
            keyboard = [
                [InlineKeyboardButton(get_message_text('phone_number', language), callback_data='phone')],
                [InlineKeyboardButton('Telegram', callback_data='telegram')],
                [InlineKeyboardButton('WhatsApp', callback_data='whatsapp')],
                [InlineKeyboardButton('Email', callback_data='email')],
                [InlineKeyboardButton(get_message_text('done', language), callback_data='done')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.user_data['registration_step'] = 3
            await update.message.reply_text(get_message_text('telegram_contact_saved', language), reply_markup=reply_markup)

        elif context.user_data.get('registration_step') == 4:
            context.user_data['years_of_experience'] = update.message.text
            keyboard = [
                [InlineKeyboardButton(get_message_text('yes', language), callback_data='yes')],
                [InlineKeyboardButton(get_message_text('no', language), callback_data='no')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.user_data['registration_step'] = 4.5
            await update.message.reply_text(get_message_text('provide_work_experience', language), reply_markup=reply_markup)

        elif context.user_data.get('registration_step') == 5:
            context.user_data['work_experience'] = update.message.text
            context.user_data['registration_step'] = 5.5
            keyboard = [
                [InlineKeyboardButton(get_message_text('yes', language), callback_data='yes')],
                [InlineKeyboardButton(get_message_text('no', language), callback_data='no')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(get_message_text('provide_factories', language), reply_markup=reply_markup)

        elif context.user_data.get('registration_step') == 6:
            processed_elements = [element.strip() for element in update.message.text.split(',')]
            context.user_data['factories'] = processed_elements
            context.user_data['registration_step'] = 7
            keyboard = [
                [InlineKeyboardButton(get_message_text('shirts', language), callback_data='shirts')],
                [InlineKeyboardButton(get_message_text('pants', language), callback_data='pants')],
                [InlineKeyboardButton(get_message_text('jackets', language), callback_data='jackets')],
                [InlineKeyboardButton(get_message_text('sweaters', language), callback_data='sweaters')],
                [InlineKeyboardButton(get_message_text('other', language), callback_data='other')],
                [InlineKeyboardButton(get_message_text('done', language), callback_data='done_products')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(get_message_text('provide_products', language), reply_markup=reply_markup)

        elif context.user_data.get('registration_step') == 7.5:
            context.user_data['products'].extend(element.strip() for element in update.message.text.split(','))
            context.user_data['registration_step'] = 7
            keyboard = [
                [InlineKeyboardButton(get_message_text('shirts', language), callback_data='shirts')],
                [InlineKeyboardButton(get_message_text('pants', language), callback_data='pants')],
                [InlineKeyboardButton(get_message_text('jackets', language), callback_data='jackets')],
                [InlineKeyboardButton(get_message_text('sweaters', language), callback_data='sweaters')],
                [InlineKeyboardButton(get_message_text('other', language), callback_data='other')],
                [InlineKeyboardButton(get_message_text('done', language), callback_data='done_products')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(get_message_text('other_products_received', language), reply_markup=reply_markup)

        elif context.user_data.get('registration_step') == 8.5:
            context.user_data['completed_orders'] = update.message.text
            context.user_data['registration_step'] = 9
            keyboard = [
                [InlineKeyboardButton(get_message_text('yes', language), callback_data='yes_images')],
                [InlineKeyboardButton(get_message_text('no', language), callback_data='no_images')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(get_message_text('provide_images', language), reply_markup=reply_markup)

        elif context.user_data.get('registration_step') == 9.5:
            keyboard = [
                [InlineKeyboardButton(get_message_text('done', language), callback_data='done_images')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if 'images' not in context.user_data:
                context.user_data['images'] = []
            if update.message.photo:
                photo_file_id = update.message.photo[-1].file_id
                context.user_data['images'].append(photo_file_id)
                await update.message.reply_text(get_message_text('image_received', language), reply_markup=reply_markup)
            else:
                await update.message.reply_text(get_message_text('upload_image', language), reply_markup=reply_markup)

async def complete_registration(update_or_query, context: ContextTypes.DEFAULT_TYPE) -> None:
    language = context.user_data.get('language', 'lang_ru')
    role = context.user_data['role']
    contact_details = ''
    images = context.user_data.get('images', [])

    # Construct contact details
    for contact_type, contacts in context.user_data.get('contacts', {}).items():
        contact_details += f"{contact_type.capitalize()}:\n"
        for contact in contacts:
            if contact_type == 'telegram':
                contact_details += f"@{contact}\n"
            else:
                contact_details += f"{contact}\n"

    # Dynamically construct the message based on non-empty fields
    message_parts = [
        f"{get_message_text('role', language)}: {get_message_text(role, language)}"
    ]

    if role == 'factory':
        fields = {
            'factory_name': context.user_data.get('factory_name', ''),
            'factory_searching_for': get_message_text(context.user_data.get('factory_searching_role', ''), language),
            'address': context.user_data.get('address', ''),
            'order_details': context.user_data.get('order_details', ''),
            'salary': context.user_data.get('salary', '')
        }
    else:
        fields = {
            'full_name': context.user_data.get('full_name', ''),
            'years_of_experience': context.user_data.get('years_of_experience', ''),
            'work_experience': context.user_data.get('work_experience', ''),
            'factories': ', '.join(context.user_data.get('factories', [])),
            'completed_orders': context.user_data.get('completed_orders', ''),
            'products': ', '.join(context.user_data.get('products', []))
        }

    for key, value in fields.items():
        if value:
            message_parts.append(f"{get_message_text(key, language)}: {value}")

    if contact_details:
        message_parts.append(f"{get_message_text('contact_details', language)}:\n{contact_details}")

    message = '\n'.join(message_parts)

    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
    if images:
        media_group = [InputMediaPhoto(media=image) for image in images]
        await context.bot.send_media_group(chat_id=GROUP_CHAT_ID, media=media_group)
    
    context.user_data['registration_step'] = 'evaluation_rating'
    keyboard = [
                [InlineKeyboardButton(1, callback_data=1)],
                [InlineKeyboardButton(2, callback_data=2)],
                [InlineKeyboardButton(3, callback_data=3)],
                [InlineKeyboardButton(4, callback_data=4)],
                [InlineKeyboardButton(5, callback_data=5)],
            ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update_or_query.edit_message_text(get_message_text('registration_completed', language), reply_markup=reply_markup)


def main() -> None:
    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
