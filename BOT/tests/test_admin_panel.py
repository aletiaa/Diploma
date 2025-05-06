import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from BOT.handlers.admin.admin_panel import (
    get_admin_access_level,
    user_exists_by_phone,
    format_user_list,
    super_admin_only
)

class TestAdminPanelFunctions(unittest.TestCase):

    @patch("BOT.handlers.admin.admin_panel.get_connection")
    def test_get_admin_access_level_found(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("admin_super",)
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        result = get_admin_access_level("12345")
        self.assertEqual(result, "admin_super")

    @patch("BOT.handlers.admin.admin_panel.get_connection")
    def test_get_admin_access_level_not_found(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        result = get_admin_access_level("99999")
        self.assertIsNone(result)

    @patch("BOT.handlers.admin.admin_panel.sqlite3.connect")
    def test_user_exists_by_phone_true(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        self.assertTrue(user_exists_by_phone("1234567890"))

    @patch("BOT.handlers.admin.admin_panel.sqlite3.connect")
    def test_user_exists_by_phone_false(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        self.assertFalse(user_exists_by_phone("0000000000"))

    def test_format_user_list_with_data(self):
        users = [("Іван Петренко", "+380123456789", "ТВ-21", "user")]
        title = "Список користувачів"
        result = format_user_list(users, title)

        self.assertIn("Іван Петренко", result)
        self.assertIn("+380123456789", result)
        self.assertIn("ТВ-21", result)
        self.assertIn("Список користувачів", result)

    def test_format_user_list_empty(self):
        result = format_user_list([], "Порожній список")
        self.assertEqual(result, "❌ Жодного користувача не знайдено.")

    @patch("BOT.handlers.admin.admin_panel.get_admin_access_level")
    def test_super_admin_only_allows_execution(self, mock_access):
        mock_access.return_value = "admin_super"

        mock_callback = MagicMock()
        mock_callback.from_user.id = "12345"
        mock_callback.message.answer = AsyncMock()

        @super_admin_only
        async def mock_function(callback):
            return "✅ Done"

        result = asyncio.run(mock_function(mock_callback))
        self.assertEqual(result, "✅ Done")

    @patch("BOT.handlers.admin.admin_panel.get_admin_access_level")
    def test_super_admin_only_blocks_non_super_admin(self, mock_access):
        mock_access.return_value = "admin_limited"

        mock_callback = MagicMock()
        mock_callback.from_user.id = "12345"
        mock_callback.message.answer = AsyncMock()

        @super_admin_only
        async def mock_function(callback):
            return "Should not run"

        asyncio.run(mock_function(mock_callback))
        mock_callback.message.answer.assert_called_once_with("🚫 У вас немає прав для цієї дії.")


if __name__ == "__main__":
    unittest.main()
