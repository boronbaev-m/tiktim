import logging

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Welcome to the Tiktim Bot! Use /register to start registration.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Use /register to register.')

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Sewer at home", callback_data='home_sewer')],
        [InlineKeyboardButton("Sewer in factory", callback_data='sewer')],
        [InlineKeyboardButton("Factory", callback_data='factory')],
        [InlineKeyboardButton("Technologist", callback_data='technologist')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data['registration_step'] = 1
    await update.message.reply_text('Кто вы?', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if context.user_data['registration_step'] == 1:
        role = query.data
        context.user_data['role'] = role
        context.user_data['registration_step'] = 2
        await context.bot.send_message(chat_id=query.from_user.id, text=f'You selected: {role.replace("_", " ").capitalize()}. Please provide your full name.')

    elif context.user_data['registration_step'] == 3:
        contact_type = query.data
        if contact_type == 'done':
            context.user_data['registration_step'] = 4
            await query.edit_message_text(text='Please provide the number of years you have been working.')
        elif contact_type == 'telegram':
            keyboard = [
                [InlineKeyboardButton("Use Current Telegram Account", callback_data='use_current_telegram')],
                [InlineKeyboardButton("Use Another Telegram Account", callback_data='use_other_telegram')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.user_data['current_contact'] = contact_type
            context.user_data['registration_step'] = 3.5
            await query.edit_message_text(text='Do you want to use your current Telegram account or provide another one?', reply_markup=reply_markup)
        else:
            context.user_data['current_contact'] = contact_type
            context.user_data['registration_step'] = 3.5
            await query.edit_message_text(text=f'Please provide your {contact_type.capitalize()} contact details.')

    elif context.user_data['registration_step'] == 3.5 and query.data in ['use_current_telegram', 'use_other_telegram']:
        telegram_choice = query.data
        if telegram_choice == 'use_current_telegram':
            context.user_data['telegram'] = query.from_user.username
            if 'contacts' not in context.user_data:
                context.user_data['contacts'] = []
            context.user_data['contacts'].append('telegram')
            keyboard = [
                [InlineKeyboardButton("Phone Number", callback_data='phone')],
                [InlineKeyboardButton("Telegram", callback_data='telegram')],
                [InlineKeyboardButton("WhatsApp", callback_data='whatsapp')],
                [InlineKeyboardButton("Email", callback_data='email')],
                [InlineKeyboardButton("Done", callback_data='done')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.user_data['registration_step'] = 3
            await query.edit_message_text(f'Using your current Telegram account: @{query.from_user.username}. You can add more contact details or press Done.', reply_markup=reply_markup)
        else:
            context.user_data['registration_step'] = 3.6
            await query.edit_message_text(text='Please provide your Telegram username.')

    elif context.user_data['registration_step'] == 4.5:
        text = query.data
        if text.lower() == 'yes':
            context.user_data['registration_step'] = 5
            await query.edit_message_text('Please provide your work experience details.')
        else:
            context.user_data['registration_step'] = 5.5
            keyboard = [
                [InlineKeyboardButton("Yes", callback_data='yes')],
                [InlineKeyboardButton("No", callback_data='no')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text('Do you want to name factories where you worked?', reply_markup=reply_markup)

    elif context.user_data['registration_step'] == 5.5:
        text = query.data
        if text.lower() == 'yes':
            context.user_data['registration_step'] = 6
            await query.edit_message_text('Please provide names of companies where you worked divided by comma.')
        else:
            context.user_data['factories'] = ''
            context.user_data['registration_step'] = 7
            keyboard = [
                [InlineKeyboardButton("Shirts", callback_data='shirts')],
                [InlineKeyboardButton("Pants", callback_data='pants')],
                [InlineKeyboardButton("Jackets", callback_data='jackets')],
                [InlineKeyboardButton("Sweaters", callback_data='sweaters')],
                [InlineKeyboardButton("Other", callback_data='other')],
                [InlineKeyboardButton("Done", callback_data='done_products')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text('Please select the things you can make.', reply_markup=reply_markup)

    elif context.user_data['registration_step'] == 7:
        if query.data == 'done_products':
            context.user_data['registration_step'] = 8
            keyboard = [
                [InlineKeyboardButton("Yes", callback_data='yes_orders')],
                [InlineKeyboardButton("No", callback_data='no_orders')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text('Do you want to provide details about completed orders?', reply_markup=reply_markup)
        elif query.data == 'other':
            context.user_data['registration_step'] = 7.5
            await query.edit_message_text('Please provide other products you can make, separated by commas.')
        else:
            if 'products' not in context.user_data:
                context.user_data['products'] = []
            if query.data not in context.user_data['products']:
                context.user_data['products'].append(query.data)
                if not query.message.text == 'Product added. You can add more or press Done.':
                    await query.edit_message_text('Product added. You can add more or press Done.', reply_markup=query.message.reply_markup)
            else:
                if not query.message.text == 'This product is already added. You can add more or press Done.':
                    await query.edit_message_text('This product is already added. You can add more or press Done.', reply_markup=query.message.reply_markup)

    elif context.user_data['registration_step'] == 8:
        if query.data == 'yes_orders':
            context.user_data['registration_step'] = 8.5
            await query.edit_message_text('Please provide details of completed orders.')
        else:
            context.user_data['completed_orders'] = ''
            context.user_data['registration_step'] = 9
            keyboard = [
                [InlineKeyboardButton("Yes", callback_data='yes_images')],
                [InlineKeyboardButton("No", callback_data='no_images')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text('Do you want to upload images of your works?', reply_markup=reply_markup)

    elif context.user_data['registration_step'] == 9:
        if query.data == 'yes_images':
            context.user_data['registration_step'] = 9.5
            await query.edit_message_text('Please upload images of your works.')
        else:
            context.user_data['images'] = []
            await complete_registration(query, context)

    elif query.data == 'done_images':
        await complete_registration(query, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('registration_step') == 2:
        context.user_data['full_name'] = update.message.text
        context.user_data['registration_step'] = 3
        keyboard = [
            [InlineKeyboardButton("Phone Number", callback_data='phone')],
            [InlineKeyboardButton("Telegram", callback_data='telegram')],
            [InlineKeyboardButton("WhatsApp", callback_data='whatsapp')],
            [InlineKeyboardButton("Email", callback_data='email')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Please provide your contact details:', reply_markup=reply_markup)

    elif context.user_data.get('registration_step') == 3.5:
        context.user_data[context.user_data['current_contact']] = update.message.text
        if 'contacts' not in context.user_data:
            context.user_data['contacts'] = []
        context.user_data['contacts'].append(context.user_data['current_contact'])
        keyboard = [
            [InlineKeyboardButton("Phone Number", callback_data='phone')],
            [InlineKeyboardButton("Telegram", callback_data='telegram')],
            [InlineKeyboardButton("WhatsApp", callback_data='whatsapp')],
            [InlineKeyboardButton("Email", callback_data='email')],
            [InlineKeyboardButton("Done", callback_data='done')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['registration_step'] = 3
        await update.message.reply_text('Contact details saved. You can add more or press Done.', reply_markup=reply_markup)

    elif context.user_data.get('registration_step') == 3.6:
        context.user_data['telegram'] = update.message.text
        if 'contacts' not in context.user_data:
            context.user_data['contacts'] = []
        context.user_data['contacts'].append('telegram')
        keyboard = [
            [InlineKeyboardButton("Phone Number", callback_data='phone')],
            [InlineKeyboardButton("Telegram", callback_data='telegram')],
            [InlineKeyboardButton("WhatsApp", callback_data='whatsapp')],
            [InlineKeyboardButton("Email", callback_data='email')],
            [InlineKeyboardButton("Done", callback_data='done')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['registration_step'] = 3
        await update.message.reply_text('Telegram contact saved. You can add more contact details or press Done.', reply_markup=reply_markup)

    elif context.user_data.get('registration_step') == 4:
        if not update.message.text.isdigit():
            await update.message.reply_text('Please answer only with numbers, try again. Please provide the number of years you have been working.')
        else:            
            context.user_data['years_of_experience'] = update.message.text
            keyboard = [
                [InlineKeyboardButton("Yes", callback_data='yes')],
                [InlineKeyboardButton("No", callback_data='no')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.user_data['registration_step'] = 4.5
            await update.message.reply_text('Do you want to provide your work experience?', reply_markup=reply_markup)

    elif context.user_data.get('registration_step') == 5:
        context.user_data['work_experience'] = update.message.text
        context.user_data['registration_step'] = 5.5
        keyboard = [
            [InlineKeyboardButton("Yes", callback_data='yes')],
            [InlineKeyboardButton("No", callback_data='no')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Do you want to name factories where you worked?', reply_markup=reply_markup)

    elif context.user_data.get('registration_step') == 6:
        processed_elements = [element.strip() for element in update.message.text.split(',')]
        context.user_data['factories'] = processed_elements
        context.user_data['registration_step'] = 7
        keyboard = [
            [InlineKeyboardButton("Shirts", callback_data='shirts')],
            [InlineKeyboardButton("Pants", callback_data='pants')],
            [InlineKeyboardButton("Jackets", callback_data='jackets')],
            [InlineKeyboardButton("Sweaters", callback_data='sweaters')],
            [InlineKeyboardButton("Other", callback_data='other')],
            [InlineKeyboardButton("Done", callback_data='done_products')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Please select the things you can make.', reply_markup=reply_markup)

    elif context.user_data.get('registration_step') == 7.5:
        context.user_data['products'].extend(element.strip() for element in update.message.text.split(','))
        context.user_data['registration_step'] = 7
        keyboard = [
            [InlineKeyboardButton("Shirts", callback_data='shirts')],
            [InlineKeyboardButton("Pants", callback_data='pants')],
            [InlineKeyboardButton("Jackets", callback_data='jackets')],
            [InlineKeyboardButton("Sweaters", callback_data='sweaters')],
            [InlineKeyboardButton("Other", callback_data='other')],
            [InlineKeyboardButton("Done", callback_data='done_products')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Other products received. Please select more or press Done.', reply_markup=reply_markup)

    elif context.user_data.get('registration_step') == 8.5:
        context.user_data['completed_orders'] = update.message.text
        context.user_data['registration_step'] = 9
        keyboard = [
            [InlineKeyboardButton("Yes", callback_data='yes_images')],
            [InlineKeyboardButton("No", callback_data='no_images')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Do you want to upload images of your works?', reply_markup=reply_markup)

    elif context.user_data.get('registration_step') == 9.5:
        if 'images' not in context.user_data:
            context.user_data['images'] = []
        if update.message.photo:
            photo_file_id = update.message.photo[-1].file_id
            context.user_data['images'].append(photo_file_id)
            await update.message.reply_text('Image received. You can add more images or press Done.')
        else:
            await update.message.reply_text('Please upload an image.')


async def complete_registration(update_or_query, context: ContextTypes.DEFAULT_TYPE) -> None:
    role = context.user_data['role']
    full_name = context.user_data['full_name']
    years_of_experience = context.user_data.get('years_of_experience', '')
    work_experience = context.user_data.get('work_experience', '')
    factories = ', '.join(context.user_data.get('factories', []))
    completed_orders = context.user_data.get('completed_orders', '')
    products = ', '.join(context.user_data.get('products', []))
    images = context.user_data.get('images', [])

    # Prepare the message for the group chat
    contact_details = '\n'.join([f"{contact.capitalize()}: {context.user_data.get(contact, '')}" for contact in context.user_data.get('contacts', [])])
    if 'telegram' in context.user_data:
        contact_details = contact_details.replace(f"Telegram: {context.user_data['telegram']}", f"Telegram: @{context.user_data['telegram']}")

    message = (f"Role: {role.replace('_', ' ').capitalize()}\n"
               f"Full Name: {full_name}\n"
               f"Years of Experience: {years_of_experience}\n"
               f"Work Experience: {work_experience}\n"
               f"Factories: {factories}\n"
               f"Completed Orders: {completed_orders}\n"
               f"Products: {products}\n"
               f"Contact Details:\n{contact_details}")

    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
    for image in images:
        await context.bot.send_photo(chat_id=GROUP_CHAT_ID, photo=image)

    await update_or_query.edit_message_text('Registration completed! Thank you.')

def main() -> None:
    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
