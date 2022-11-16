import logging
from telegram.ext import ApplicationBuilder, CommandHandler, Application
import configs
import commands.auth as auth_commands
import commands.queues as queues_commands
import commands.start as start_commands

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

application: Application


def main() -> None:
    global application
    application = ApplicationBuilder().token(configs.BOT_TOKEN).build()

    add_command('register', auth_commands.register)
    add_command('new_api_token', auth_commands.new_api_token)
    add_command('list_api_tokens', auth_commands.list_api_tokens)
    add_command('delete_api_token', auth_commands.delete_api_token)
    add_command('create', queues_commands.create)
    add_command('add', queues_commands.add)
    add_command('forget', queues_commands.forget)
    add_command('join', queues_commands.join)
    add_command('leave', queues_commands.leave)
    add_command('ready', queues_commands.ready)
    add_command('unready', queues_commands.unready)
    add_command('get_known_queues', queues_commands.get_known_queues)
    add_command('get_queue_name', queues_commands.get_queue_name)
    add_command('get_queue_info', queues_commands.get_queue_info)
    application.add_handler(start_commands.conv_handler)

    application.run_polling()


def add_command(name: str, callback):
    application.add_handler(CommandHandler(name, callback))


if __name__ == '__main__':
    main()
