class TaskStatuses:
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class TaskTypes:
    REMOVE_BG = "remove_bg"
    AVATAR = "avatar"
    POSTER = "poster"
    STICKERS = "stickers"
    PRODUCT = "product"
    HELP = "help"


class BotModes:
    REMOVE_BG = "remove_bg"
    AVATAR = "avatar"
    POSTER = "poster"
    STICKERS = "stickers"
    PRODUCT = "product"


class HistoryActions:
    START = "start"
    REMOVE_BG_REQUESTED = "remove_bg_requested"
    REMOVE_BG_DONE = "remove_bg_done"
    PROMPT_IMPROVE_DONE = "prompt_improve_done"
    TEMPLATE_APPLIED = "template_applied"
    TEXT_ASSISTANT = "text_assistant"
