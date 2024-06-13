import logging
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

with open('messages.json', 'r', encoding='utf-8') as file:
    messages = json.load(file)

def get_message(key: str, language: str = 'lang_en') -> str:
    return messages.get(key, {}).get(language, '')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Кыргызча", callback_data='lang_ky')],
        [InlineKeyboardButton("Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("English", callback_data='lang_en')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data['registration_step'] = 'language_selection'
    await update.message.reply_text(messages['choose_language'], reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    language = context.user_data.get('language', 'lang_ru')
    await update.message.reply_text(get_message('help', language))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    language = context.user_data.get('language', 'lang_ru')

    if context.user_data['registration_step'] == 'language_selection':
        lang_choice = query.data
        context.user_data['language'] = lang_choice
        language = context.user_data.get('language', 'lang_ru')
        keyboard = [
            [InlineKeyboardButton(get_message('home_sewer', language), callback_data='home_sewer')],
            [InlineKeyboardButton(get_message('sewer_in_factory', language), callback_data='sewer_in_factory')],
            [InlineKeyboardButton(get_message('factory', language), callback_data='factory')],
            [InlineKeyboardButton(get_message('technologist', language), callback_data='technologist')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['registration_step'] = 1
        await query.edit_message_text(get_message('choose_role', language), reply_markup=reply_markup)

    elif context.user_data['registration_step'] == 1:
        role = query.data
        context.user_data['role'] = role
        context.user_data['registration_step'] = 2
        await context.bot.send_message(chat_id=query.from_user.id, text=get_message('role_selected', language).format(get_message(role, language)))

    elif context.user_data['registration_step'] == 3:
        contact_type = query.data
        if contact_type == 'done':
            context.user_data['registration_step'] = 4
            await query.edit_message_text(text=get_message('provide_experience_years', language))
        elif contact_type == 'telegram':
            keyboard = [
                [InlineKeyboardButton(get_message('use_current_telegram', language), callback_data='use_current_telegram')],
                [InlineKeyboardButton(get_message('use_other_telegram', language), callback_data='use_other_telegram')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.user_data['current_contact'] = contact_type
            context.user_data['registration_step'] = 3.5
            await query.edit_message_text(text=get_message('telegram_choice', language), reply_markup=reply_markup)
        else:
            context.user_data['current_contact'] = contact_type
            context.user_data['registration_step'] = 3.5
            await query.edit_message_text(text=get_message('provide_contact_details', language))

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
                [InlineKeyboardButton(get_message('phone_number', language), callback_data='phone')],
                [InlineKeyboardButton('Telegram', callback_data='telegram')],
                [InlineKeyboardButton('WhatsApp', callback_data='whatsapp')],
                [InlineKeyboardButton('Email', callback_data='email')],
                [InlineKeyboardButton(get_message('done', language), callback_data='done')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.user_data['registration_step'] = 3
            await query.edit_message_text(text=get_message('using_current_telegram', language).format(query.from_user.username), reply_markup=reply_markup)
        else:
            context.user_data['registration_step'] = 3.6
            await query.edit_message_text(text=get_message('provide_telegram_username', language))

    elif context.user_data['registration_step'] == 4.5:
        text = query.data
        if text.lower() == 'yes':
            context.user_data['registration_step'] = 5
            await query.edit_message_text(get_message('provide_work_experience', language))
        else:
            context.user_data['registration_step'] = 5.5
            keyboard = [
                [InlineKeyboardButton(get_message('yes', language), callback_data='yes')],
                [InlineKeyboardButton(get_message('no', language), callback_data='no')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(get_message('provide_factories', language), reply_markup=reply_markup)

    elif context.user_data['registration_step'] == 5.5:
        text = query.data
        if text.lower() == 'yes':
            context.user_data['registration_step'] = 6
            await query.edit_message_text(get_message('factories_list', language))
        else:
            context.user_data['factories'] = ''
            context.user_data['registration_step'] = 7
            keyboard = [
                [InlineKeyboardButton(get_message('shirts', language), callback_data='shirts')],
                [InlineKeyboardButton(get_message('pants', language), callback_data='pants')],
                [InlineKeyboardButton(get_message('jackets', language), callback_data='jackets')],
                [InlineKeyboardButton(get_message('sweaters', language), callback_data='sweaters')],
                [InlineKeyboardButton(get_message('other', language), callback_data='other')],
                [InlineKeyboardButton(get_message('done', language), callback_data='done_products')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(get_message('provide_products', language), reply_markup=reply_markup)

    elif context.user_data['registration_step'] == 7:
        if query.data == 'done_products':
            context.user_data['registration_step'] = 8
            keyboard = [
                [InlineKeyboardButton(get_message('yes', language), callback_data='yes_orders')],
                [InlineKeyboardButton(get_message('no', language), callback_data='no_orders')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(get_message('provide_orders', language), reply_markup=reply_markup)
        elif query.data == 'other':
            context.user_data['registration_step'] = 7.5
            await query.edit_message_text(get_message('provide_other_products', language))
        else:
            if 'products' not in context.user_data:
                context.user_data['products'] = []
            if query.data not in context.user_data['products']:
                context.user_data['products'].append(query.data)
                if not query.message.text == get_message('product_added', language):
                    await query.edit_message_text(get_message('product_added', language), reply_markup=query.message.reply_markup)
            else:
                if not query.message.text == get_message('product_already_added', language):
                    await query.edit_message_text(get_message('product_already_added', language), reply_markup=query.message.reply_markup)

    elif context.user_data['registration_step'] == 8:
        if query.data == 'yes_orders':
            context.user_data['registration_step'] = 8.5
            await query.edit_message_text(get_message('provide_orders_details', language))
        else:
            context.user_data['completed_orders'] = ''
            context.user_data['registration_step'] = 9
            keyboard = [
                [InlineKeyboardButton(get_message('yes', language), callback_data='yes_images')],
                [InlineKeyboardButton(get_message('no', language), callback_data='no_images')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(get_message('provide_images', language), reply_markup=reply_markup)

    elif context.user_data['registration_step'] == 9:
        if query.data == 'yes_images':
            context.user_data['registration_step'] = 9.5
            await query.edit_message_text(get_message('upload_images', language))
        else:
            context.user_data['images'] = []
            await complete_registration(query, context)

    elif query.data == 'done_images':
        await complete_registration(query, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    language = context.user_data.get('language', 'lang_ru')

    if context.user_data.get('registration_step') == 2:
        context.user_data['full_name'] = update.message.text
        context.user_data['registration_step'] = 3
        keyboard = [
            [InlineKeyboardButton(get_message('phone_number', language), callback_data='phone')],
            [InlineKeyboardButton('Telegram', callback_data='telegram')],
            [InlineKeyboardButton('WhatsApp', callback_data='whatsapp')],
            [InlineKeyboardButton('Email', callback_data='email')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(get_message('provide_contact_details', language), reply_markup=reply_markup)

    elif context.user_data.get('registration_step') == 3.5:
        if 'contacts' not in context.user_data:
            context.user_data['contacts'] = {}
        if context.user_data['current_contact'] not in context.user_data['contacts']:
            context.user_data['contacts'][context.user_data['current_contact']] = []
        if update.message.text not in  context.user_data['contacts'][context.user_data['current_contact']]:
            context.user_data['contacts'][context.user_data['current_contact']].append(update.message.text)
        keyboard = [
            [InlineKeyboardButton(get_message('phone_number', language), callback_data='phone')],
            [InlineKeyboardButton('Telegram', callback_data='telegram')],
            [InlineKeyboardButton('WhatsApp', callback_data='whatsapp')],
            [InlineKeyboardButton('Email', callback_data='email')],
            [InlineKeyboardButton(get_message('done', language), callback_data='done')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['registration_step'] = 3
        await update.message.reply_text(get_message('contact_details_saved', language), reply_markup=reply_markup)

    elif context.user_data.get('registration_step') == 3.6:
        context.user_data['telegram'] = update.message.text
        if 'contacts' not in context.user_data:
            context.user_data['contacts'] = {}
        if 'telegram' not in context.user_data['contacts']:
            context.user_data['contacts']['telegram'] = []
        if update.message.text not in context.user_data['contacts']['telegram']:
            context.user_data['contacts']['telegram'].append(update.message.text)
        keyboard = [
            [InlineKeyboardButton(get_message('phone_number', language), callback_data='phone')],
            [InlineKeyboardButton('Telegram', callback_data='telegram')],
            [InlineKeyboardButton('WhatsApp', callback_data='whatsapp')],
            [InlineKeyboardButton('Email', callback_data='email')],
            [InlineKeyboardButton(get_message('done', language), callback_data='done')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['registration_step'] = 3
        await update.message.reply_text(get_message('telegram_contact_saved', language), reply_markup=reply_markup)

    elif context.user_data.get('registration_step') == 4:
        if not update.message.text.isdigit():
            await update.message.reply_text(get_message('provide_numbers_only', language))
        else:
            context.user_data['years_of_experience'] = update.message.text
            keyboard = [
                [InlineKeyboardButton(get_message('yes', language), callback_data='yes')],
                [InlineKeyboardButton(get_message('no', language), callback_data='no')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.user_data['registration_step'] = 4.5
            await update.message.reply_text(get_message('provide_work_experience', language), reply_markup=reply_markup)

    elif context.user_data.get('registration_step') == 5:
        context.user_data['work_experience'] = update.message.text
        context.user_data['registration_step'] = 5.5
        keyboard = [
            [InlineKeyboardButton(get_message('yes', language), callback_data='yes')],
            [InlineKeyboardButton(get_message('no', language), callback_data='no')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(get_message('provide_factories', language), reply_markup=reply_markup)

    elif context.user_data.get('registration_step') == 6:
        processed_elements = [element.strip() for element in update.message.text.split(',')]
        context.user_data['factories'] = processed_elements
        context.user_data['registration_step'] = 7
        keyboard = [
            [InlineKeyboardButton(get_message('shirts', language), callback_data='shirts')],
            [InlineKeyboardButton(get_message('pants', language), callback_data='pants')],
            [InlineKeyboardButton(get_message('jackets', language), callback_data='jackets')],
            [InlineKeyboardButton(get_message('sweaters', language), callback_data='sweaters')],
            [InlineKeyboardButton(get_message('other', language), callback_data='other')],
            [InlineKeyboardButton(get_message('done', language), callback_data='done_products')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(get_message('provide_products', language), reply_markup=reply_markup)

    elif context.user_data.get('registration_step') == 7.5:
        context.user_data['products'].extend(element.strip() for element in update.message.text.split(','))
        context.user_data['registration_step'] = 7
        keyboard = [
            [InlineKeyboardButton(get_message('shirts', language), callback_data='shirts')],
            [InlineKeyboardButton(get_message('pants', language), callback_data='pants')],
            [InlineKeyboardButton(get_message('jackets', language), callback_data='jackets')],
            [InlineKeyboardButton(get_message('sweaters', language), callback_data='sweaters')],
            [InlineKeyboardButton(get_message('other', language), callback_data='other')],
            [InlineKeyboardButton(get_message('done', language), callback_data='done_products')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(get_message('other_products_received', language), reply_markup=reply_markup)

    elif context.user_data.get('registration_step') == 8.5:
        context.user_data['completed_orders'] = update.message.text
        context.user_data['registration_step'] = 9
        keyboard = [
            [InlineKeyboardButton(get_message('yes', language), callback_data='yes_images')],
            [InlineKeyboardButton(get_message('no', language), callback_data='no_images')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(get_message('provide_images', language), reply_markup=reply_markup)

    elif context.user_data.get('registration_step') == 9.5:
        keyboard = [
            [InlineKeyboardButton(get_message('done', language), callback_data='done_images')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if 'images' not in context.user_data:
            context.user_data['images'] = []
        if update.message.photo:
            photo_file_id = update.message.photo[-1].file_id
            context.user_data['images'].append(photo_file_id)
            await update.message.reply_text(get_message('image_received', language), reply_markup=reply_markup)
        else:
            await update.message.reply_text(get_message('upload_image', language), reply_markup=reply_markup)

async def complete_registration(update_or_query, context: ContextTypes.DEFAULT_TYPE) -> None:
    language = context.user_data.get('language', 'lang_ru')

    role = context.user_data['role']
    full_name = context.user_data['full_name']
    years_of_experience = context.user_data.get('years_of_experience', '')
    work_experience = context.user_data.get('work_experience', '')
    factories = ', '.join(context.user_data.get('factories', []))
    completed_orders = context.user_data.get('completed_orders', '')
    products = ', '.join(context.user_data.get('products', []))
    images = context.user_data.get('images', [])

    # Prepare the message for the group chat
    contact_details = ''
    for contact_type, contacts in context.user_data.get('contacts', {}).items():
        contact_details += f"{contact_type.capitalize()}:\n"
        for contact in contacts:
            if contact_type == 'telegram':
                contact_details += f"@{contact}\n"
            else:
                contact_details += f"{contact}\n"
        
    message = (f"{get_message('role', language)}: {get_message(role, language)}\n"
               f"{get_message('full_name', language)}: {full_name}\n"
               f"{get_message('years_of_experience', language)}: {years_of_experience}\n"
               f"{get_message('work_experience', language)}: {work_experience}\n"
               f"{get_message('factories', language)}: {factories}\n"
               f"{get_message('completed_orders', language)}: {completed_orders}\n"
               f"{get_message('products', language)}: {products}\n"
               f"{get_message('contact_details', language)}:\n{contact_details}")

    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
    for image in images:
        await context.bot.send_photo(chat_id=GROUP_CHAT_ID, photo=image)

    await update_or_query.edit_message_text(get_message('registration_completed', language))


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
