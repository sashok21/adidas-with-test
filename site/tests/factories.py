import factory
from app.core.models import Category, Brand, Product, User

class CategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Category
        sqlalchemy_session_persistence = "commit"

    # Використовуємо Sequence для унікальних імен, щоб не було помилки UNIQUE constraint
    name = factory.Sequence(lambda n: f"Category {n}")


class BrandFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Brand
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Brand {n}")
    description = factory.Faker("sentence")


class ProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Product
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("word")
    description = factory.Faker("sentence")
    # Генеруємо ціну від 10 до 1000 з 2 знаками після коми
    price = factory.Faker("pyfloat", positive=True, min_value=10, max_value=1000, right_digits=2)
    in_stock = True

    # Створюємо зв'язки автоматично
    category = factory.SubFactory(CategoryFactory)
    brand = factory.SubFactory(BrandFactory)


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    # Генеруємо унікальні email
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = "password123"  # Статичний пароль для тестів
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = factory.Sequence(lambda n: f"+38050{n:07d}")