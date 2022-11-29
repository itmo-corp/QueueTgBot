from telegram.ext import ConversationHandler

# states
END = ConversationHandler.END
RESTART = 0
DEFAULT = 1
CONFIRMING = 2


# local user fields
CONFIRM_CALLBACK_FIELD = 0
CONFIRM_NO_CALLBACK_FIELD = 1
