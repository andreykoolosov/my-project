from unittest.mock import Mock

import pytest

from app.repositories.category import CategoryRepository
from app.services.category import CategoryService


@pytest.fixture
def category_repository_mock() -> Mock:
    return Mock(spec=CategoryRepository)


@pytest.fixture
def category_service(db_mock: Mock, category_repository_mock) -> CategoryService:
    category_service = CategoryService(db_mock)
    category_service.category_repository = category_repository_mock
    return category_service
