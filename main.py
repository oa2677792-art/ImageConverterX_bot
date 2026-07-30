import os
import io
import sys
import logging
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# ============================
# LOGGING SETUP
# ============================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================
# TOKEN VALIDATION
# ============================

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

if not TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN environment variable is not set!")
    logger.error("📌 Please set it in Railway Variables or .env file")
    logger.error("💡 Example: TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
    sys.exit(1)

TOKEN = TOKEN.strip()

if len(TOKEN) < 20:
    logger.error(f"❌ Invalid token format. Token is too short: {len(TOKEN)} characters")
    logger.error("📌 Token should be at least 20 characters long")
    sys.exit(1)

if ':' not in TOKEN:
    logger.error("❌ Invalid token format. Token must contain a colon ':'")
    logger.error("📌 Format: numbers:letters_and_numbers")
    sys.exit(1)

logger.info(f"✅ Token loaded successfully! (Length: {len(TOKEN)} characters)")

# ============================
# USER STATE MANAGEMENT
# ============================

user_states = {}

# ============================
# COMMAND HANDLERS
# ============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message with inline keyboard."""
    user = update.effective_user
    logger.info(f"User {user.id} (@{user.username}) started the bot")
    
    keyboard = [
        [
            InlineKeyboardButton("🖼️ Convert Image", callback_data="convert"),
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🖼️ **Welcome to ImageConverterX Bot!**\n\n"
        "I can convert images between different formats.\n\n"
        "📸 **How to use:**\n"
        "1. Send me an image (as photo or document)\n"
        "2. Select the output format you want\n"
        "3. I'll convert and send it back!\n\n"
        "**Supported formats:** JPG, PNG, WEBP, BMP, GIF, TIFF\n\n"
        "🔧 **Commands:**\n"
        "/start - Show this menu\n"
        "/convert - Convert an image\n"
        "/help - Show help\n"
        "/about - About this bot",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message."""
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "❓ **Help - ImageConverterX Bot**\n\n"
        "📸 **How to convert an image:**\n"
        "1. Send me an image (photo or document)\n"
        "2. I'll show you format options\n"
        "3. Click on your desired format\n"
        "4. I'll convert and send it back!\n\n"
        "🖼️ **Supported Formats:**\n"
        "• JPG - Best for photos (small file size)\n"
        "• PNG - Best for graphics with transparency\n"
        "• WEBP - Modern format (small size, good quality)\n"
        "• BMP - Uncompressed (large file size)\n"
        "• GIF - Best for animations\n"
        "• TIFF - High quality (large file size)\n\n"
        "⚡ **Tips:**\n"
        "• Send high-quality images for best results\n"
        "• Images with transparent backgrounds work best with PNG\n"
        "• Use JPG for smaller file sizes\n\n"
        "🔧 **Commands:**\n"
        "/start - Main menu\n"
        "/convert - Start conversion\n"
        "/help - This help message\n"
        "/about - About this bot",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send about information."""
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🖼️ **About ImageConverterX Bot**\n\n"
        "**Version:** 1.0.0\n"
        "**Developer:** PixelPirate\n\n"
        "🏴‍☠️ **Features:**\n"
        "• Convert images between multiple formats\n"
        "• Supports JPG, PNG, WEBP, BMP, GIF, TIFF\n"
        "• Fast and reliable conversion\n"
        "• No file size limits\n"
        "• Privacy-focused: images are processed in real-time\n\n"
        "💡 **Built with:**\n"
        "• Python 3.11\n"
        "• python-telegram-bot\n"
        "• Pillow (PIL) library\n\n"
        "🔗 **Source Code:**\n"
        "Available on GitHub\n\n"
        "Made with ❤️ by PixelPirate",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def convert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /convert command."""
    user_id = update.effective_user.id
    user_states[user_id] = {"mode": "converter"}
    
    await update.message.reply_text(
        "🖼️ **Image Converter**\n\n"
        "Please send me an image you want to convert.\n"
        "You can send it as a photo or as a document.\n\n"
        "**Supported formats:** JPG, PNG, WEBP, BMP, GIF, TIFF",
        parse_mode="Markdown"
    )

# ============================
# BUTTON CALLBACK HANDLER
# ============================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    
    if action == "menu":
        keyboard = [
            [
                InlineKeyboardButton("🖼️ Convert Image", callback_data="convert"),
                InlineKeyboardButton("ℹ️ About", callback_data="about"),
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data="help"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🖼️ **Welcome to ImageConverterX Bot!**\n\n"
            "I can convert images between different formats.\n\n"
            "📸 **How to use:**\n"
            "1. Send me an image (as photo or document)\n"
            "2. Select the output format you want\n"
            "3. I'll convert and send it back!\n\n"
            "**Supported formats:** JPG, PNG, WEBP, BMP, GIF, TIFF\n\n"
            "🔧 **Commands:**\n"
            "/start - Show this menu\n"
            "/convert - Convert an image\n"
            "/help - Show help\n"
            "/about - About this bot",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    elif action == "convert":
        user_id = update.effective_user.id
        user_states[user_id] = {"mode": "converter"}
        await query.edit_message_text(
            "🖼️ **Image Converter**\n\n"
            "Please send me an image you want to convert.\n"
            "You can send it as a photo or as a document.\n\n"
            "**Supported formats:** JPG, PNG, WEBP, BMP, GIF, TIFF",
            parse_mode="Markdown"
        )
    
    elif action == "help":
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "❓ **Help - ImageConverterX Bot**\n\n"
            "📸 **How to convert an image:**\n"
            "1. Send me an image (photo or document)\n"
            "2. I'll show you format options\n"
            "3. Click on your desired format\n"
            "4. I'll convert and send it back!\n\n"
            "🖼️ **Supported Formats:**\n"
            "• JPG - Best for photos (small file size)\n"
            "• PNG - Best for graphics with transparency\n"
            "• WEBP - Modern format (small size, good quality)\n"
            "• BMP - Uncompressed (large file size)\n"
            "• GIF - Best for animations\n"
            "• TIFF - High quality (large file size)\n\n"
            "⚡ **Tips:**\n"
            "• Send high-quality images for best results\n"
            "• Images with transparent backgrounds work best with PNG\n"
            "• Use JPG for smaller file sizes\n\n"
            "🔧 **Commands:**\n"
            "/start - Main menu\n"
            "/convert - Start conversion\n"
            "/help - This help message\n"
            "/about - About this bot",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    elif action == "about":
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🖼️ **About ImageConverterX Bot**\n\n"
            "**Version:** 1.0.0\n"
            "**Developer:** PixelPirate\n\n"
            "🏴‍☠️ **Features:**\n"
            "• Convert images between multiple formats\n"
            "• Supports JPG, PNG, WEBP, BMP, GIF, TIFF\n"
            "• Fast and reliable conversion\n"
            "• No file size limits\n"
            "• Privacy-focused: images are processed in real-time\n\n"
            "💡 **Built with:**\n"
            "• Python 3.11\n"
            "• python-telegram-bot\n"
            "• Pillow (PIL) library\n\n"
            "🔗 **Source Code:**\n"
            "Available on GitHub\n\n"
            "Made with ❤️ by PixelPirate",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

# ============================
# MESSAGE HANDLERS
# ============================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages based on their current mode."""
    user_id = update.effective_user.id
    
    # If user hasn't set a mode, prompt them to use /start
    if user_id not in user_states:
        keyboard = [
            [InlineKeyboardButton("🏠 Start", callback_data="menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "👋 Please use /start to see available options first! 🖼️",
            reply_markup=reply_markup
        )
        return
    
    mode = user_states[user_id].get("mode")
    
    if mode == "converter":
        await handle_converter(update, context)
    else:
        await update.message.reply_text(
            "I'm not sure what you want to do. Please use /start to begin."
        )

# ============================
# IMAGE CONVERTER
# ============================

async def handle_converter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image conversion."""
    # Check if user sent a photo
    if update.message.photo:
        # Get the largest photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        
        # Download the image
        image_bytes = await file.download_as_bytearray()
        
        # Store the image in context for later use
        context.user_data['image_data'] = image_bytes
        context.user_data['image_format'] = 'jpg'
        
        # Ask for output format
        keyboard = [
            [
                InlineKeyboardButton("JPG", callback_data="fmt_jpg"),
                InlineKeyboardButton("PNG", callback_data="fmt_png"),
                InlineKeyboardButton("WEBP", callback_data="fmt_webp"),
            ],
            [
                InlineKeyboardButton("BMP", callback_data="fmt_bmp"),
                InlineKeyboardButton("GIF", callback_data="fmt_gif"),
                InlineKeyboardButton("TIFF", callback_data="fmt_tiff"),
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data="menu"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📸 **Image received!**\n\n"
            "Select the output format you want:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    elif update.message.document:
        # Handle document uploads
        document = update.message.document
        if document.mime_type and document.mime_type.startswith('image/'):
            file = await context.bot.get_file(document.file_id)
            image_bytes = await file.download_as_bytearray()
            
            context.user_data['image_data'] = image_bytes
            context.user_data['image_format'] = document.mime_type.split('/')[-1]
            
            # Ask for output format
            keyboard = [
                [
                    InlineKeyboardButton("JPG", callback_data="fmt_jpg"),
                    InlineKeyboardButton("PNG", callback_data="fmt_png"),
                    InlineKeyboardButton("WEBP", callback_data="fmt_webp"),
                ],
                [
                    InlineKeyboardButton("BMP", callback_data="fmt_bmp"),
                    InlineKeyboardButton("GIF", callback_data="fmt_gif"),
                    InlineKeyboardButton("TIFF", callback_data="fmt_tiff"),
                ],
                [
                    InlineKeyboardButton("❌ Cancel", callback_data="menu"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "📄 **Image received!**\n\n"
                f"📦 Original format: {document.mime_type.split('/')[-1].upper()}\n\n"
                "Select the output format you want:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "❌ Please send a valid image file (JPG, PNG, etc.)\n\n"
                "Supported formats: JPG, PNG, WEBP, BMP, GIF, TIFF"
            )
    else:
        await update.message.reply_text(
            "❌ Please send an image (as a photo or document).\n\n"
            "Supported formats: JPG, PNG, WEBP, BMP, GIF, TIFF"
        )

async def handle_format_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle format selection for image conversion."""
    query = update.callback_query
    await query.answer()
    
    # Extract format from callback data
    output_format = query.data.replace('fmt_', '')
    
    # Get the stored image
    image_data = context.user_data.get('image_data')
    if not image_data:
        await query.edit_message_text(
            "❌ Image not found. Please start over with /convert."
        )
        return
    
    try:
        # Send processing message
        await query.edit_message_text(
            f"🔄 **Converting to {output_format.upper()}...**\n\n"
            "⏳ Please wait, this may take a few seconds.",
            parse_mode="Markdown"
        )
        
        # Convert the image
        input_image = Image.open(io.BytesIO(image_data))
        
        # Handle RGBA to RGB for JPG
        if output_format == 'jpg' and input_image.mode == 'RGBA':
            background = Image.new('RGB', input_image.size, (255, 255, 255))
            background.paste(input_image, mask=input_image.split()[3])
            input_image = background
        elif output_format == 'jpg' and input_image.mode == 'P':
            input_image = input_image.convert('RGB')
        elif output_format == 'png' and input_image.mode != 'RGBA':
            input_image = input_image.convert('RGBA')
        elif output_format == 'gif' and input_image.mode != 'P':
            input_image = input_image.convert('P')
        
        # Save to bytes
        output = io.BytesIO()
        input_image.save(output, format=output_format.upper())
        output.seek(0)
        
        # Get file size
        size_kb = len(output.getvalue()) / 1024
        size_mb = size_kb / 1024
        
        # Format size string
        if size_mb > 1:
            size_str = f"{size_mb:.2f} MB"
        else:
            size_str = f"{size_kb:.1f} KB"
        
        # Send the converted image
        await query.edit_message_text(
            f"✅ **Conversion complete!**\n\n"
            f"📦 **Format:** {output_format.upper()}\n"
            f"📊 **Size:** {size_str}\n\n"
            f"Sending your image now...",
            parse_mode="Markdown"
        )
        
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=output,
            filename=f"converted.{output_format}",
            caption=f"🖼️ **Converted to {output_format.upper()}**\n\n"
                    f"🏴‍☠️ ImageConverterX Bot\n"
                    f"🔧 /convert - Convert another image",
            parse_mode="Markdown"
        )
        
        # Clean up
        if 'image_data' in context.user_data:
            del context.user_data['image_data']
        if 'image_format' in context.user_data:
            del context.user_data['image_format']
        
        # Reset user state
        user_id = update.effective_user.id
        if user_id in user_states:
            del user_states[user_id]
        
    except Exception as e:
        await query.edit_message_text(
            f"❌ **Error converting image:**\n\n"
            f"`{str(e)}`\n\n"
            "Please try again with /convert",
            parse_mode="Markdown"
        )

# ============================
# MAIN APPLICATION
# ============================

def main():
    """Start the bot."""
    logger.info("🖼️ ImageConverterX Bot is starting...")
    logger.info("🤖 Bot username: @ImageConverterX_bot")
    logger.info(f"🔑 Token loaded: Yes (Length: {len(TOKEN)})")
    
    try:
        # Create the Application
        application = ApplicationBuilder().token(TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('help', help_command))
        application.add_handler(CommandHandler('about', about_command))
        application.add_handler(CommandHandler('convert', convert_command))
        
        # Add callback query handlers (for buttons)
        application.add_handler(CallbackQueryHandler(button_callback, pattern='^(menu|convert|help|about)$'))
        application.add_handler(CallbackQueryHandler(handle_format_selection, pattern='^fmt_'))
        
        # Add message handler for all other messages
        application.add_handler(MessageHandler(filters.ALL, handle_message))
        
        logger.info("✅ Bot is running and ready to convert images!")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
