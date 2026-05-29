from unittest.mock import Mock

import pytest

from app.repositories.task import TaskRepository
from app.services.task import TaskService


@pytest.fixture
def task_repository_mock() -> Mock:
    """Создаём мок TaskRepository один раз и переиспользуем в тестах"""
    return Mock(spec=TaskRepository)


@pytest.fixture
def task_service(db_mock: Mock, task_repository_mock: Mock) -> TaskService:
    """Создаём TaskService один раз, чтобы переиспользовать в тестах"""
    task_service = TaskService(db_mock)
    task_service.task_repository = task_repository_mock
    return task_service
