from datetime import timezone
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone  # Добавляем правильный импорт
from psycopg import logger
# Кастомная модель пользователя
class CustomUser(AbstractUser):
    # Определяем варианты ролей для пользователя
    ROLE_CHOICES = (
        ('admin', 'Admin'),  # Администратор
        ('material_warehouse_manager', 'Начальник склада материалов'),  # Начальник склада материалов
        ('finished_goods_warehouse_manager', 'Начальник склада готовой продукции'),  # Начальник склада готовой продукции
        ('sales_director', 'Директор по продажам'),  # Директор по продажам
    )
    role = models.CharField(max_length=40, choices=ROLE_CHOICES)  # Роль пользователя

    def __str__(self):
        return self.username  # Представление имени пользователя

# Модель линии производства
class Line(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Название линии должно быть уникальным
    volume = models.DecimalField(max_digits=10, decimal_places=2)  # Объем линии
    number = models.IntegerField()  # Номер линии

    def __str__(self):
        return self.name  # Представление названия линии

    def can_add_product(self, product_volume):
        """Проверяет соответствие объема продукта объему линии"""
        return Decimal(product_volume) == self.volume

    def clean(self):
        """Проверка уникальности линии"""
        if Line.objects.filter(name=self.name).exclude(pk=self.pk).exists():
            raise ValidationError(f"Линия с названием '{self.name}' уже существует.")

# Модель продукта
class Product(models.Model):
    name = models.CharField(max_length=100)  # Название продукта
    gtin = models.CharField(max_length=50)  # Код GTIN
    volume = models.DecimalField(max_digits=10, decimal_places=2)  # Объем продукта
    line = models.ForeignKey(Line, on_delete=models.CASCADE)  # Связь с линией

    class Meta:
        unique_together = ('name', 'line')  # Уникальность имени продукта на линии

    def __str__(self):
        return self.name  # Представление названия продукта

# Модель партии продукции
class Batch(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Продукт
    line = models.ForeignKey(Line, on_delete=models.CASCADE)  # Линия
    batch_number = models.CharField(max_length=50, unique=True, editable=False)  # Номер партии
    production_date = models.DateField()  # Дата производства
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Количество
    is_used = models.BooleanField(default=False)  # Статус использования

    def __str__(self):
        return f'Партия {self.batch_number} продукта {self.product.name} на линии {self.line.name}'

    def save(self, *args, **kwargs):
        """Сохраняем партию и генерируем номер партии, если он не установлен"""
        if not self.batch_number:
            self.batch_number = self.generate_batch_number()
        super().save(*args, **kwargs)

    def generate_batch_number(self):
        """Генерация номера партии на основе текущей даты и последнего номера"""
        today = timezone.now().date()
        date_str = today.strftime('%d.%m.%Y')

        with transaction.atomic():
            last_batch = Batch.objects.filter(production_date=today).order_by('-id').first()
            if last_batch:
                try:
                    last_number = int(last_batch.batch_number.split()[0])
                except (ValueError, IndexError):
                    last_number = 0
            else:
                last_number = 0

            next_number = last_number + 1
            new_batch_number = f'{next_number} {date_str}'

            if Batch.objects.filter(batch_number=new_batch_number).exists():
                raise ValidationError(f'Номер партии "{new_batch_number}" уже существует.')

            return new_batch_number

    def clean(self):
        """Проверка уникальности номера партии и статуса использования"""
        if Batch.objects.filter(batch_number=self.batch_number).exclude(pk=self.pk).exists():
            raise ValidationError(f'Номер партии "{self.batch_number}" уже существует.')
        if self.is_used:
            raise ValidationError('Эта партия уже была использована.')

    def can_release(self, quantity):
        """Проверяет, достаточно ли количества в партии для выпуска"""
        return not self.is_used and self.quantity >= quantity

    def release(self, quantity):
        """Выпускает указанное количество из партии"""
        if not self.can_release(quantity):
            raise ValidationError('Невозможно выпустить указанное количество из этой партии.')
        self.quantity -= quantity
        if self.quantity == 0:
            self.is_used = True
        self.save()
# Модель единицы измерения
class MeasurementUnit(models.Model):
    UNIT_CHOICES = [
        ('gram', 'Грамм'),
        ('piece', 'Штука'),
        ('liter', 'Литр'),
    ]

    name = models.CharField(max_length=20, choices=UNIT_CHOICES, unique=True)  # Уникальность единицы измерения

    def __str__(self):
        return self.get_name_display()  # Отображение наименования единицы измерения

# Модель материала
class Material(models.Model):
    name = models.CharField(max_length=100)  # Название материала
    unit = models.CharField(max_length=50, choices=[('g', 'Граммы'), ('pcs', 'Штуки'), ('l', 'Литры')])  # Единица измерения

    def __str__(self):
        return self.name  # Отображение названия материала

# Модель остатка на складе
class Stock(models.Model):
    material = models.OneToOneField(Material, on_delete=models.CASCADE)  # Связь с материалом
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))  # Количество материала

    def __str__(self):
        return f'{self.material.name}: {self.quantity} {self.material.get_unit_display()}'  # Отображение остатка на складе

# Модель связи продукта с материалом
class ProductMaterial(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Продукт
    material = models.ForeignKey(Material, on_delete=models.CASCADE)  # Материал
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Количество материала для продукта

    class Meta:
        unique_together = ('product', 'material')  # Уникальность комбинации продукта и материала

    def __str__(self):
        return f'{self.product} - {self.material}'  # Отображение связи продукта с материалом

# Модель контрагента
class Counterparty(models.Model):
    name = models.CharField(max_length=100)  # Название контрагента
    address = models.CharField(max_length=255)  # Адрес контрагента
    contact_number = models.CharField(max_length=15)  # Контактный номер контрагента

    def __str__(self):
        return self.name  # Отображение названия контрагента

# Модель отгрузки
class Shipment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Продукт
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)  # Партия
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Количество
    shipment_date = models.DateField()  # Дата отгрузки
    counterparty = models.ForeignKey(Counterparty, on_delete=models.CASCADE)  # Контрагент

    def __str__(self):
        return f'{self.product.name} - {self.quantity} (Дата: {self.shipment_date})'  # Отображение информации об отгрузке

# Модель остатков готовой продукции
class FinishedGoodsStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Продукт
    batch_number = models.CharField(max_length=50)  # Номер партии
    production_date = models.DateField()  # Дата производства
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))  # Количество
    is_used = models.BooleanField(default=False)  # Статус использования

    def __str__(self):
        return f'{self.product.name} - {self.batch_number} - {self.quantity}'  # Отображение остатков готовой продукции

    def update_quantity(self, quantity):
        """Обновляет количество на складе готовой продукции"""
        if quantity < 0 and abs(quantity) > self.quantity:
            raise ValidationError("Количество для списания превышает доступное на складе.")

        self.quantity += quantity

        if self.quantity <= 0:
            self.quantity = 0
            self.is_used = True

        self.save()

# Модель элемента отгрузки
class ShipmentItem(models.Model):
    shipment = models.ForeignKey('Shipment', on_delete=models.CASCADE, related_name='items')  # Отгрузка
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Продукт
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)  # Партия
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Количество

    def save(self, *args, **kwargs):
        """Проверяет наличие товара на складе готовой продукции и обновляет количество"""
        finished_goods = FinishedGoodsStock.objects.filter(
            product=self.product,
            batch_number=self.batch.batch_number,
            production_date=self.batch.production_date
        ).first()

        if not finished_goods or finished_goods.quantity < self.quantity:
            raise ValidationError('Количество отгрузки превышает доступное количество на складе готовой продукции.')

        # Используем транзакцию для обеспечения целостности данных
        with transaction.atomic():
            super().save(*args, **kwargs)

            # Обновляем количество на складе готовой продукции
            finished_goods.update_quantity(-self.quantity)