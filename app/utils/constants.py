class TaskTypes:
    REMOVE_BG = 'remove_bg'
    AVATAR = 'avatar'
    POSTER = 'poster'
    STICKERS = 'stickers'
    PRODUCT = 'product'
    HELP = 'help'


class TaskStatuses:
    PENDING = 'pending'
    PROCESSING = 'processing'
    DONE = 'done'
    FAILED = 'failed'


class HistoryActions:
    START = 'start'
    HELP = 'help'
    MENU_OPENED = 'menu_opened'
    MODE_SELECTED = 'mode_selected'
    REMOVE_BG_REQUESTED = 'remove_bg_requested'
    REMOVE_BG_DONE = 'remove_bg_done'
    IMAGE_TASK_REQUESTED = 'image_task_requested'
    IMAGE_TASK_DONE = 'image_task_done'
    IMAGE_TASK_FAILED = 'image_task_failed'
    HISTORY_OPENED = 'history_opened'


class BotModes:
    REMOVE_BG = 'remove_bg'
    AVATAR = 'avatar'
    POSTER = 'poster'
    STICKERS = 'stickers'
    PRODUCT = 'product'


MODE_TITLES = {
    BotModes.REMOVE_BG: 'Удалить фон',
    BotModes.AVATAR: 'Аватар',
    BotModes.POSTER: 'Постер',
    BotModes.STICKERS: 'Стикеры',
    BotModes.PRODUCT: 'Товарное фото',
}


STYLE_PRESETS = {
    BotModes.AVATAR: [
        ('old_money', 'Old Money'),
        ('cyberpunk', 'Cyberpunk'),
        ('anime', 'Anime'),
        ('fashion', 'Fashion'),
    ],
    BotModes.POSTER: [
        ('movie', 'Кино-постер'),
        ('brand', 'Рекламный постер'),
        ('youtube', 'YouTube превью'),
        ('dramatic', 'Драматичный постер'),
    ],
    BotModes.STICKERS: [
        ('cute', 'Милые'),
        ('meme', 'Мемные'),
        ('anime', 'Anime'),
        ('emoji', 'Emoji pack'),
    ],
    BotModes.PRODUCT: [
        ('luxury', 'Luxury'),
        ('marketplace', 'Marketplace'),
        ('dark', 'Тёмный фон'),
        ('minimal', 'Минимализм'),
    ],
}
