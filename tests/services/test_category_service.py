from unittest.mock import Mock

import pytest

from app.models.category import CategoryORM
from app.schemas.category import (
    CategoryCreateSchema,
    CategorySchema,
    CategoryUpdateSchema,
)
from app.services.category import CategoryNotFoundError, CategoryService


def test_list_category_return_pydantic_model(
    category_repository_mock: Mock, category_service: CategoryService
) -> None:
    list_categories = [
        CategoryORM(id="category_1", name="Товары"),
        CategoryORM(id="category_2", name="Игрушки"),
    ]
    category_repository_mock.get_all.return_value = list_categories

    result = category_service.list_category()

    assert result == [
        CategorySchema(id="category_1", name="Товары"),
        CategorySchema(id="category_2", name="Игрушки"),
    ]


def test_create_category_commit_created_category(
    db_mock: Mock, category_repository_mock: Mock, category_service: CategoryService
) -> None:
    created_category = CategoryORM(id="category_1", name="Товары")

    category_repository_mock.create_category.return_value = created_category

    result = category_service.create_category(CategoryCreateSchema(name="Товары"))

    assert result == CategorySchema.model_validate(created_category)

    db_mock.commit.assert_called_once_with()


def test_update_category_update_success(
    db_mock: Mock, category_repository_mock: Mock, category_service: CategoryService
) -> None:
    category = CategoryORM(id="category_1", name="Товары")
    category_repository_mock.get_by_id.return_value = category

    result = category_service.update_category(
        "category_1", CategoryUpdateSchema(name="Новая категория")
    )
    expected_name = "Новая категория"

    assert result == CategorySchema(id="category_1", name=expected_name)
    category_repository_mock.get_by_id.assert_called_once_with(category_id="category_1")
    db_mock.commit.assert_called_once_with()


def test_update_category_raises_when_category_not_found(
    db_mock: Mock, category_repository_mock: Mock, category_service: CategoryService
) -> None:
    category_repository_mock.get_by_id.return_value = None

    with pytest.raises(CategoryNotFoundError):
        category_service.update_category(
            "category_1", CategoryUpdateSchema(name="ОШИБКА")
        )

    db_mock.commit.assert_not_called()


def test_category_delete_category_commit_when_category_exist(
    db_mock: Mock, category_repository_mock: Mock, category_service: CategoryService
) -> None:
    category = CategoryORM(id="category_1", name="Товары")
    category_repository_mock.get_by_id.return_value = category

    category_service.delete_category("category_1")
    category_repository_mock.get_by_id.assert_called_once_with(category_id="category_1")
    category_repository_mock.delete_category.assert_called_once_with(category)
    db_mock.commit.assert_called_once_with()


def test_category_delete_category_commit_when_category_not_found(
    db_mock: Mock, category_repository_mock: Mock, category_service: CategoryService
) -> None:
    category_repository_mock.get_by_id.return_value = None

    with pytest.raises(CategoryNotFoundError):
        category_service.delete_category("category_1")

    db_mock.commit.assert_not_called()
