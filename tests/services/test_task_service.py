from unittest.mock import Mock

import pytest

from app.models.tasks import TaskORM
from app.schemas.task import TaskCreateSchema, TaskSchema, TaskUpdateSchema
from app.services.task import TaskNotFoundError, TaskService


# Имитируем, что метод get_all репозитория вернет эти задачи
def test_list_tasks_returns_pydantic_models(
    task_service: TaskService, task_repository_mock: Mock
) -> None:
    task_repository_mock.get_all.return_value = [
        TaskORM(id="task-1", title="Изучить pytest", completed=False),
        TaskORM(id="task-2", title="Написать первый тест", completed=False),
    ]
    result = task_service.list_tasks()

    assert result == [
        TaskSchema(id="task-1", title="Изучить pytest", completed=False),
        TaskSchema(id="task-2", title="Написать первый тест", completed=False),
    ]


def test_create_task_commits_created_task(
    db_mock: Mock,
    task_service: TaskService,
    task_repository_mock: Mock,
) -> None:
    created_task = TaskORM(id="task-1", title="Новая задача", completed=False)
    task_repository_mock.create.return_value = created_task

    result = task_service.create_task(TaskCreateSchema(title="Новая задача"))

    task_repository_mock.create.assert_called_once_with(title="Новая задача")

    db_mock.commit.assert_called_once_with()

    assert result == TaskSchema(id="task-1", title="Новая задача", completed=False)


@pytest.mark.parametrize(
    ("payload", "expected_title", "expected_completed"),
    [
        pytest.param(
            TaskUpdateSchema(title="Обновить задачу"),  # payload
            "Обновить задачу",  # expected_title
            False,  # expected_completed
        ),
        pytest.param(
            TaskUpdateSchema(completed=True),  # payload
            "Старая задача",  # expected_title
            True,  # expected_completed
        ),
        pytest.param(
            TaskUpdateSchema(title="Готово", completed=True),  # payload
            "Готово",  # expected_title
            True,  # expected_completed
        ),
    ],
)
def test_update_task_updates_only_passed_fields(
    db_mock: Mock,
    task_service: TaskService,
    task_repository_mock: Mock,
    payload: TaskUpdateSchema,
    expected_title: str,
    expected_completed: bool,
) -> None:
    updated_task = TaskORM(id="task_1", title="Старая задача", completed=False)
    task_repository_mock.get_by_id.return_value = updated_task

    result = task_service.update_task("task_1", payload)

    task_repository_mock.get_by_id.assert_called_once_with(task_id="task_1")
    db_mock.commit.assert_called_once_with()
    assert result == TaskSchema(
        id="task_1", title=expected_title, completed=expected_completed
    )


def test_update_task_raises_when_task_not_found(
    db_mock: Mock, task_service: TaskService, task_repository_mock: Mock
) -> None:
    task_repository_mock.get_by_id.return_value = None

    with pytest.raises(TaskNotFoundError):
        task_service.update_task("missing-task", TaskUpdateSchema(title="Неважно"))

    db_mock.commit.assert_not_called()


def test_delete_task_commit_when_task_exist(
    db_mock: Mock,
    task_repository_mock: Mock,
    task_service: TaskService,
) -> None:
    deleted_task = TaskORM(id="task_1", title="Удалить", completed=False)
    task_repository_mock.get_by_id.return_value = deleted_task

    task_service.delete_task("task_1")

    task_repository_mock.get_by_id.assert_called_once_with(task_id="task_1")
    task_repository_mock.delete.assert_called_once_with(deleted_task)
    db_mock.commit.assert_called_once_with()


def test_delete_task_raises_when_task_not_found(
    db_mock: Mock, task_service: TaskService, task_repository_mock: Mock
) -> None:
    task_repository_mock.get_by_id.return_value = None

    with pytest.raises(TaskNotFoundError):
        task_service.delete_task("task_id - неважно")

    db_mock.commit.assert_not_called()
