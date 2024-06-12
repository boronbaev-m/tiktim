from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Replace 'YOUR_API_TOKEN' with the API token you got from BotFather
with open("token.txt", "r") as f:
    API_TOKEN = f.read()

# GROUP_CHAT_ID = -1002210391229
GROUP_CHAT_ID = -4124409854

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
            await query.edit_message_text(f'Using your current Telegram account: @{query.from_user.username}. You can add more contact details or press Done.', reply_markup=reply_markup)
            context.user_data['registration_step'] = 3
        else:
            context.user_data['registration_step'] = 3.6
            await query.edit_message_text(text='Please provide your Telegram username.')

    elif context.user_data['registration_step'] == 4.5:
        text = query.data
        if text.lower() == 'yes':
            context.user_data['registration_step'] = 5
            await query.edit_message_text('Please provide your work experience details.')
        else:
            context.user_data['work_experience'] = ''
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
            await query.edit_message_text('Please provide details of completed orders.')
            
async def registration_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    step = context.user_data.get('registration_step', 0)

    if step == 2:
        context.user_data['full_name'] = text
        context.user_data['registration_step'] = 3
        
        keyboard = [
            [InlineKeyboardButton("Phone Number", callback_data='phone')],
            [InlineKeyboardButton("Telegram", callback_data='telegram')],
            [InlineKeyboardButton("WhatsApp", callback_data='whatsapp')],
            [InlineKeyboardButton("Email", callback_data='email')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Please provide your contact details (select at least one).', reply_markup=reply_markup)

    elif step == 3.5:
        contact_type = context.user_data['current_contact']
        context.user_data[contact_type] = text
        
        if 'contacts' not in context.user_data:
            context.user_data['contacts'] = []
        context.user_data['contacts'].append(contact_type)
        
        keyboard = [
            [InlineKeyboardButton("Phone Number", callback_data='phone')],
            [InlineKeyboardButton("Telegram", callback_data='telegram')],
            [InlineKeyboardButton("WhatsApp", callback_data='whatsapp')],
            [InlineKeyboardButton("Email", callback_data='email')],
            [InlineKeyboardButton("Done", callback_data='done')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(f'Contact details for {contact_type.capitalize()} received. You can add more or press Done.', reply_markup=reply_markup)
        context.user_data['registration_step'] = 3

    elif step == 3.6:
        context.user_data['telegram'] = text
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
        await update.message.reply_text(f'Telegram contact details received. You can add more or press Done.', reply_markup=reply_markup)
        context.user_data['registration_step'] = 3

    elif step == 4:
        context.user_data['years_of_experience'] = text
        context.user_data['registration_step'] = 4.5
        
        keyboard = [
            [InlineKeyboardButton("Yes", callback_data='yes')],
            [InlineKeyboardButton("No", callback_data='no')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Do you want to provide details about your work experience?', reply_markup=reply_markup)

    elif step == 5:
        context.user_data['work_experience'] = text
        context.user_data['registration_step'] = 5.5
        keyboard = [
            [InlineKeyboardButton("Yes", callback_data='yes')],
            [InlineKeyboardButton("No", callback_data='no')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Do you want to name factories where you worked?', reply_markup=reply_markup)

    elif step == 6:
        context.user_data['factories'] = text
        context.user_data['registration_step'] = 7
        await update.message.reply_text('Please provide details of completed orders.')

    elif step == 7:
        context.user_data['completed_orders'] = text
        role = context.user_data['role']
        full_name = context.user_data['full_name']
        work_experience = context.user_data.get('work_experience', '')
        years_of_experience = context.user_data['years_of_experience']
        factories = context.user_data['factories']
        completed_orders = context.user_data['completed_orders']

        # Prepare the message for the group chat
        contact_details = '\n'.join([f"{contact.capitalize()}: {context.user_data[contact]}" for contact in context.user_data['contacts']])
        group_message = (
            f"New {role.replace('_', ' ').capitalize()} Registration:\n"
            f"Full Name: {full_name}\n\n"
            f"Years of Experience: {years_of_experience}\n"
            f"Work Experience: {work_experience}\n"
            f"Factories: {factories}\n"
            f"Completed Orders: {completed_orders}\n\n"
            f"Contact Details:\n{contact_details}"
        )

        # Send the gathered information to the group chat
        # TOPIC_ID = 2 if role == 'home_sewer' else 1
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=group_message)
        # await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=group_message, message_thread_id=TOPIC_ID)

        # Confirm to the user that their information was sent
        await update.message.reply_text(f'Thank you for registering as a {role.replace("_", " ")}. Your information has been sent to the group.')
        context.user_data.clear()

def main():
    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registration_conversation))

    application.run_polling()

if __name__ == '__main__':
    main()