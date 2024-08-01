from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TOKEN
from handlers import start, handle_image, send_horiz_collage, send_vert_collage


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(CommandHandler('horiz', send_horiz_collage))
    application.add_handler(CommandHandler('vert', send_vert_collage))

    application.run_polling()


if __name__ == '__main__':
    main()
