from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

with open("token.txt", "r") as f:
    API_TOKEN = f.read()
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
            context.user_data['products'].append(query.data)
            await query.edit_message_text('Product added. You can add more or press Done.', reply_markup=query.message.reply_markup)

    elif context.user_data['registration_step'] == 7.5:
        context.user_data['other_products'] = text.split(',')
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

async def complete_registration(update_or_query, context: ContextTypes.DEFAULT_TYPE) -> None:
    role = context.user_data['role']
    full_name = context.user_data['full_name']
    years_of_experience = context.user_data.get('years_of_experience', '')
    work_experience = context.user_data.get('work_experience', '')
    factories = context.user_data.get('factories', '')
    completed_orders = context.user_data.get('completed_orders', '')
    products = ', '.join(context.user_data.get('products', []))
    other_products = ', '.join(context.user_data.get('other_products', []))
    images = context.user_data.get('images', [])

    # Prepare the message for the group chat
    contact_details = '\n'.join([f"{contact.capitalize()}: {context.user_data[contact]}" for contact in context.user_data['contacts']])

    group_message = f"New {role.replace('_', ' ').capitalize()} Registration:\nFull Name: {full_name}\n\n"
    if years_of_experience:
        group_message += f"Years of Experience: {years_of_experience}\n"
    if work_experience:
        group_message += f"Work Experience: {work_experience}\n"
    if factories:
        group_message += f"Factories: {factories}\n"
    if completed_orders:
        group_message += f"Completed Orders: {completed_orders}\n"
    if products:
        group_message += f"Products: {products}\n"
    if other_products:
        group_message += f"Other Products: {other_products}\n"
    group_message += f"\nContact Details:\n{contact_details}"

    # Send the gathered information to the group chat
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=group_message)

    # Send images if any
    for image in images:
        await context.bot.send_photo(chat_id=GROUP_CHAT_ID, photo=image)

    # Confirm to the user that their information was sent
    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_text(f'Thank you for registering as a {role.replace("_", " ")}. Your information has been sent to the group.')
    else:
        await update_or_query.edit_message_text(f'Thank you for registering as a {role.replace("_", " ")}. Your information has been sent to the group.')

    context.user_data.clear()

async def registration_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        if 'images' not in context.user_data:
            context.user_data['images'] = []
        context.user_data['images'].append(photo_file_id)
        await update.message.reply_text('Image received. You can add more images or type "done" to finish.')
        context.user_data['registration_step'] = 9.5
    else:
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
            if text.isdigit():
                context.user_data['years_of_experience'] = text
                context.user_data['registration_step'] = 4.5
                keyboard = [
                    [InlineKeyboardButton("Yes", callback_data='yes')],
                    [InlineKeyboardButton("No", callback_data='no')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text('Do you want to provide details about your work experience?', reply_markup=reply_markup)
            else:
                await update.message.reply_text('Please provide a valid number for the years of experience.')

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

        elif step == 7.5:
            context.user_data['other_products'] = text.split(',')
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

        elif step == 8.5:
            context.user_data['completed_orders'] = text
            context.user_data['registration_step'] = 9
            keyboard = [
                [InlineKeyboardButton("Yes", callback_data='yes_images')],
                [InlineKeyboardButton("No", callback_data='no_images')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text('Do you want to upload images of your works?', reply_markup=reply_markup)

        elif step == 9.5:
            if text.lower() == "done":
                await complete_registration(update, context)
            else:
                await update.message.reply_text('Please upload images or type "done" to finish.')

def main():
    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registration_conversation))
    application.add_handler(MessageHandler(filters.PHOTO, registration_conversation))

    application.run_polling()

if __name__ == '__main__':
    main()