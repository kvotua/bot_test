import asyncpg
from typing import Dict, Any, Optional
from datetime import datetime
from aiogram import Bot 
from typing import List, Dict, Optional

class NotificationService:
    def __init__(self):
        """
        Инициализация сервиса уведомлений
        
        :param pool: пул подключений asyncpg
        :param bot: экземпляр бота для отправки сообщений
        """
        self._pool = None
        self._bot = None
        self._is_configured = False
        
        self.supported_events = {
            'new_order': {
                'required_fields': ['company', 'order_id', 'username' ],
                'template': (
                    "🛒 Новая заявка #{order_id} от {company}\n"
                    "👤 Создал заявку: @{username}\n"
                    "📝 Детали:\n{details}\n"
                ),
                'description': 'Создание нового заказа'
            },
            'update_beer': {
                'required_fields': ['beer_name', 'username','move'],
                'template': (
                    "🍺 Обновление данных о пиве\n"
                    "🍻 Пиво {beer_name} {move}\n"
                    "👤 Инициатор: @{username}"
                ),
                'description': 'Обновление информации о пиве'
            },
            'add_company': {
                'required_fields': ['company', 'username_creater'],
                'template': (
                    "🏢 Добавлена новая компания\n"
                    "🆔 {company}\n"
                    "👤 Создал: @{username_creater}\n"
                ),
                'description': 'Добавление новой компании'
            },
            'contragent_create_point': {
                'required_fields': ['company', 'username', 'name', 'address'],
                'template': (
                    "📍 Создана новая торговая точка {name}\n"
                    "🏢 Компания: {company}\n"
                    "👤 Создатель: @{username}\n"
                    "📌 Адрес: {address}\n"
                ),
                'description': 'Создание точки контрагента'
            },
            'company_add_employee': {
                'required_fields': [ 'company', 'point', 'username_added'],
                'template': (
                    "👥 Новый сотрудник \n"
                    "🏢 Компания: {company}\n"
                    "🏢 Точка: {point}\n"
                    "👤 Добавил: @{username_added}\n"
                ),
                'description': 'Добавление сотрудника в компанию'
            },
            'company_add_partner': {
                'required_fields': ['company','username_added'],
                'template': (
                    "🤝 Новый партнер компании\n"
                    "🏢 Компания: {company}\n"
                    "👤 Добавил: @{username_added}\n"
                ),
                'description': 'Добавление партнера компании'
            }
        }   

    def inject_dependencies(self, pool: asyncpg.Pool, bot: Bot) -> None:
        """
        Внедрение зависимостей
        :param pool: Пул подключений к PostgreSQL
        :param bot: Экземпляр бота для отправки сообщений
        """
        self._pool = pool
        self._bot = bot
        self._is_configured = True

    @property
    def is_ready(self) -> bool:
        """Проверка, что сервис готов к работе"""
        return self._is_configured and self._pool is not None and self._bot is not None

    @property
    def pool(self) -> asyncpg.Pool:
        if not self._pool:
            raise RuntimeError("Pool connection not injected")
        return self._pool

    @property
    def bot(self) -> Bot:
        if not self._bot:
            raise RuntimeError("Bot instance not injected")
        return self._bot
    
    async def _validate_event(self, event_type: str, data: Dict[str, Any]):
        """Валидация типа события и данных"""
        if event_type not in self.supported_events:
            raise ValueError(f"Unsupported event type: {event_type}")
        
        required = self.supported_events[event_type]['required_fields']
        missing = [field for field in required if field not in data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

    async def _save_event(self, event_type: str, initiator_id: int, data: Dict[str, Any]):
        """Сохранение события в историю (текстовый формат)"""
        async with self.pool.acquire() as conn:
            # Преобразуем словарь в читаемую строку
            event_text = "\n".join(
                f"{k}: {v}" 
                for k, v in data.items()
                if k not in ['company_id', 'user_id']
            )
            
            await conn.execute(
                """
                INSERT INTO event_history 
                (event_type, initiator_id, company_id, event_data)
                VALUES ($1, $2, $3, $4)
                """,
                event_type,
                initiator_id,
                data.get('company_id'),
                event_text  
            )

    async def _get_recipients(self, initiator_id: int, event_type: str, data: Dict[str, Any]) -> List[int]:
        """Получает список user_id для отправки уведомления"""
        async with self.pool.acquire() as conn:
            company_id = data.get('company_id')
            
            # Ищем:
            # 1. Пользователей с подпиской на конкретное событие + компанию (если указана)
            # 2. Пользователей с подпиской на все события ('all')
            query = """
                SELECT user_id FROM notification_settings
                WHERE (event_type = $1 AND (company_id IS NULL OR company_id = $2))
                OR event_type = 'all'
                AND user_id != $3
                GROUP BY user_id  -- Исключаем дубликаты
            """
            return [r['user_id'] for r in await conn.fetch(query, event_type, company_id, initiator_id)]

    async def _send_notification(self, user_id: int, message: str):
        """Отправка сообщения через бота"""
        try:
            await self.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")
            # Можно добавить повторные попытки или логирование

    async def call(self, event_type: str, initiator_id: int, data: Dict[str, Any]):
        """
        Основной метод для обработки и отправки уведомлений
        
        :param event_type: тип события (new_order, update_beer и т.д.)
        :param initiator_id: ID пользователя, инициировавшего событие
        :param data: данные события (должны содержать обязательные поля)
        """
        # Валидация
        await self._validate_event(event_type, data)
        
        # Сохранение в историю
        await self._save_event(event_type, initiator_id, data)
        
        # Получение получателей
        recipients = await self._get_recipients(initiator_id, event_type, data)
        if not recipients:
            return
        
        # Формирование и отправка сообщений
        template = self.supported_events[event_type].get('template', "{event_type}: {data}")
        message = template.format(event_type=event_type, **data)
        
        for user_id in recipients:
            await self._send_notification(user_id, message)

    async def add_subscription(
        self, 
        user_id: int, 
        event_type: str, 
        company_id: Optional[int] = None,
    ):
        """
        Добавляет или обновляет подписку пользователя.
        Использует ON CONFLICT для обновления существующей записи.
        """
        if event_type not in self.supported_events and event_type != 'all':
            raise ValueError(f"Неподдерживаемый тип события: {event_type}")
        
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO notification_settings 
                (user_id, event_type, company_id)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    event_type = EXCLUDED.event_type,
                    company_id = EXCLUDED.company_id
                """,
                user_id, event_type, company_id
            )
            
notification_service = NotificationService()