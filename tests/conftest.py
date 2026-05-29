from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

pytest_plugins = ["tests.services.task_fixtures", "tests.services.category_fixtures"]


@pytest.fixture
def db_mock() -> Mock:
    """Создаём мок сессии БД один раз и переиспользуем в тестах"""
    return Mock(spec=Session)
