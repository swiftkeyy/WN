from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.ai.gemini_client import GeminiClient
from app.ai.prompt_rewriter import PromptRewriter
from app.ai.prompt_router import PromptRouter
from app.database import crud
from app.database.session import AsyncSessionLocal
from app.handlers.states import BotStates
from app.keyboards.main_menu import MAIN_MENU
from app.services.history_service import HistoryService
from app.services.template_service import TemplateService
from app.services.user_service import UserService
from app.utils.constants import HistoryActions, TaskStatuses, TaskTypes

router = Router()
gemini_client = GeminiClient()
prompt_rewriter = PromptRewriter(gemini_client)
prompt_router = PromptRouter(gemini_client)
template_service = TemplateService()
user_service = UserService()
history_service = HistoryService()


@router.message(F.text == 'Улучшить промпт')
async def improve_prompt_entrypoint(message: Message, state: FSMContext) -> None:
    await state.set_state(BotStates.waiting_for_prompt_text)
    await message.answer('Пришли сырой запрос. Я верну 3 улучшенные версии.', reply_markup=MAIN_MENU)


@router.message(BotStates.waiting_for_prompt_text, F.text)
async def improve_prompt_handler(message: Message, state: FSMContext) -> None:
    user_text = message.text.strip()
    result = await prompt_rewriter.rewrite(user_text)

    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, message.from_user)
        await crud.create_task(
            session,
            user_id=user.id,
            task_type=TaskTypes.PROMPT_IMPROVE,
            input_text=user_text,
            status=TaskStatuses.DONE,
            provider='gemini',
        )
        await history_service.log(
            session,
            user_id=user.id,
            action_type=HistoryActions.PROMPT_IMPROVE_DONE,
            payload_json={'detected_goal': result.get('detected_goal', 'general')},
        )

    response = (
        'Готово.\n\n'
        f'Короткая версия:\n{result["short_version"]}\n\n'
        f'Сильная расширенная версия:\n{result["detailed_version"]}\n\n'
        f'Вариант для трендового визуала:\n{result["trend_version"]}'
    )
    await message.answer(response, reply_markup=MAIN_MENU)
    await state.clear()


@router.message(BotStates.waiting_for_template_input, F.text)
async def template_text_input_handler(message: Message, state: FSMContext) -> None:
    user_text = message.text.strip()
    data = await state.get_data()
    template_key = data.get('template_key', 'unknown_template')

    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, message.from_user)
        template = await template_service.get_by_key(session, template_key)
        final_prompt = await gemini_client.build_template_prompt(
            template_key=template_key,
            user_input=user_text,
            base_template=template.prompt_text if template else None,
        )
        await crud.create_task(
            session,
            user_id=user.id,
            task_type=TaskTypes.TEMPLATE_APPLY,
            input_text=user_text,
            status=TaskStatuses.DONE,
            provider='gemini',
        )
        await history_service.log(
            session,
            user_id=user.id,
            action_type=HistoryActions.TEMPLATE_APPLIED,
            payload_json={'template_key': template_key, 'input_text': user_text},
        )

    await message.answer(
        f'Финальный prompt:\n\n{final_prompt}\n\nМожешь сразу использовать его в image workflow.',
        reply_markup=MAIN_MENU,
    )
    await state.clear()


@router.message(F.text)
async def free_text_router_handler(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if text in {'Удалить фон', 'Улучшить промпт', 'Трендовые шаблоны', 'История', 'Помощь'}:
        return

    mode = await prompt_router.route(text)
    if mode == 'prompt_improve':
        result = await prompt_rewriter.rewrite(text)
        reply = (
            'Я определил это как задачу на улучшение промпта.\n\n'
            f'Короткая версия:\n{result["short_version"]}\n\n'
            f'Расширенная версия:\n{result["detailed_version"]}\n\n'
            f'Трендовая версия:\n{result["trend_version"]}'
        )
        task_type = TaskTypes.PROMPT_IMPROVE
    else:
        reply = await gemini_client.generate_helper_reply(mode, text)
        task_type = {
            'ai_caption': TaskTypes.AI_CAPTION,
            'poster_idea': TaskTypes.POSTER_IDEA,
            'avatar_makeover': TaskTypes.AVATAR_MAKEOVER,
            'product_photo': TaskTypes.PRODUCT_PHOTO,
            'sticker_pack': TaskTypes.STICKER_PACK,
            'template_apply': TaskTypes.TEMPLATE_APPLY,
            'general_help': TaskTypes.HELP,
        }.get(mode, TaskTypes.HELP)

    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, message.from_user)
        await crud.create_task(
            session,
            user_id=user.id,
            task_type=task_type,
            input_text=text,
            status=TaskStatuses.DONE,
            provider='gemini',
        )
        await history_service.log(
            session,
            user_id=user.id,
            action_type=HistoryActions.TEXT_ASSISTANT,
            payload_json={'mode': mode},
        )

    await message.answer(reply, reply_markup=MAIN_MENU)
