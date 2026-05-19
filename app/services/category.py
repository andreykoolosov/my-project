from sqlalchemy.orm import Session
from app.repositories.category import CategoryRepository
from app.schemas.category import CategorySchema, CategoryCreateSchema, CategoryUpdateSchema


class CategoryNotFoundError(Exception):
    """Категория не найдена"""


class CategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.category_repository = CategoryRepository(db=db)

    def list_category(self) -> list[CategorySchema]:
        categories_orm = self.category_repository.get_all()
        return [CategorySchema.model_validate(category) for category in categories_orm]

    def create_category(self, category_create: CategoryCreateSchema) -> CategorySchema:
        new_category_orm = self.category_repository.create_category(
            name=category_create.name)
        self.db.commit()
        return CategorySchema.model_validate(new_category_orm)

    def update_category(
            self, category_id: str,
            category_update: CategoryUpdateSchema
    ) -> CategorySchema:
        category_for_update = self.category_repository.get_by_id(
            category_id=category_id)
        if category_for_update is None:
            raise CategoryNotFoundError(
                f"Категория с id {category_id} не найдена!")
        if category_update.name is not None:
            category_for_update.name = category_update.name
        self.db.commit()
        return CategorySchema.model_validate(category_for_update)

    def delete_category(self, category_id: str) -> None:
        category_for_delete = self.category_repository.get_by_id(
            category_id=category_id)
        if category_for_delete is None:
            raise CategoryNotFoundError(
                f"Категория с id {category_id} не найдена!")
        self.category_repository.delete_category(category_for_delete)
        self.db.commit()
