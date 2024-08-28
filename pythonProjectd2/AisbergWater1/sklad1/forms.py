from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render, get_object_or_404

from .models import *
# Форма для создания пользователя
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser  # Используем кастомную модель пользователя
        fields = ('username', 'password1', 'password2', 'role')  # Поля формы

# Форма для линии
class LineForm(forms.ModelForm):
    class Meta:
        model = Line  # Используем модель Line
        fields = ['name', 'volume', 'number']  # Поля формы
        labels = {
            'name': 'Наименование:',  # Метка для поля имени
            'volume': 'Объем:',  # Метка для поля объема
            'number': 'Номер линии:'  # Метка для поля номера линии
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите наименование линии'}),  # Виджет для ввода имени
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите объем', 'step': '0.1'}),  # Виджет для ввода объема
            'number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер линии'}),  # Виджет для ввода номера линии
        }

# Форма для продукта
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product  # Используем модель Product
        fields = ['line', 'name', 'gtin', 'volume']  # Поля формы
        labels = {
            'line': 'Выберите линию:',  # Метка для выбора линии
            'name': 'Наименование продукта:',  # Метка для имени продукта
            'gtin': 'GTIN:',  # Метка для кода GTIN
            'volume': 'Объем:'  # Метка для объема продукта
        }
        widgets = {
            'line': forms.Select(attrs={'class': 'form-control'}),  # Виджет для выбора линии
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите наименование продукта'}),  # Виджет для имени продукта
            'gtin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите GTIN'}),  # Виджет для кода GTIN
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите объем', 'step': '0.1'}),  # Виджет для объема
        }

    def clean(self):
        cleaned_data = super().clean()
        volume = cleaned_data.get('volume')  # Получаем объем
        line = cleaned_data.get('line')  # Получаем линию

        # Проверка соответствия объема продукта и объема линии
        if line and volume:
            if volume != line.volume:
                raise forms.ValidationError('Объем продукта должен точно соответствовать объему линии.')

# Форма для партии
class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch  # Используем модель Batch
        fields = ['line', 'product', 'production_date', 'quantity']  # Поля формы
        labels = {
            'line': 'Выбрать линию',  # Метка для выбора линии
            'product': 'Добавить продукт',  # Метка для выбора продукта
            'production_date': 'Дата',  # Метка для даты производства
            'quantity': 'Количество',  # Метка для количества
        }
        widgets = {
            'line': forms.Select(attrs={'class': 'form-control'}),  # Виджет для выбора линии
            'product': forms.Select(attrs={'class': 'form-control'}),  # Виджет для выбора продукта
            'production_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),  # Виджет для выбора даты
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),  # Виджет для ввода количества
        }

    def __init__(self, *args, **kwargs):
        line_id = kwargs.pop('line_id', None)  # Получаем ID линии, если он указан
        super().__init__(*args, **kwargs)
        # Фильтруем продукты по выбранной линии
        if line_id:
            self.fields['product'].queryset = Product.objects.filter(line_id=line_id).order_by('name')
        else:
            self.fields['product'].queryset = Product.objects.none()

        # Устанавливаем текущую дату по умолчанию для новой записи
        if not self.instance.pk:  # Если это новая запись
            self.fields['production_date'].initial = date.today()

# Форма для материала
class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material  # Используем модель Material
        fields = ['name', 'unit']  # Поля формы
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название материала'}),  # Виджет для имени материала
            'unit': forms.Select(attrs={'class': 'form-control'}),  # Виджет для выбора единицы измерения
        }

# Форма для связи продукта с материалом
class ProductMaterialForm(forms.ModelForm):
    class Meta:
        model = ProductMaterial  # Используем модель ProductMaterial
        fields = ['product', 'material', 'quantity']  # Поля формы
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),  # Виджет для выбора продукта
            'material': forms.Select(attrs={'class': 'form-control'}),  # Виджет для выбора материала
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),  # Виджет для ввода количества
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Инициализация выборок для продуктов и материалов
        self.fields['product'].queryset = Product.objects.all()
        self.fields['material'].queryset = Material.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')  # Получаем продукт
        material = cleaned_data.get('material')  # Получаем материал

        # Проверка на уникальность комбинации продукта и материала
        if ProductMaterial.objects.filter(product=product, material=material).exists():
            raise forms.ValidationError('Этот материал уже добавлен к продукту.')

# Форма для создания/редактирования остатков на складе
class StockForm(forms.ModelForm):
    class Meta:
        model = Stock  # Используем модель Stock
        fields = ['material', 'quantity']  # Поля формы
        widgets = {
            'material': forms.Select(attrs={'class': 'form-control'}),  # Виджет для выбора материала
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),  # Виджет для ввода количества
        }

# Форма для выпуска продукции
class ReleaseProductsForm(forms.Form):
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.filter(quantity=0, is_used=False).order_by('batch_number'),
        label="Выберите партию",  # Метка для выбора партии
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.DecimalField(
        label="Количество для выпуска",  # Метка для ввода количества
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

# Форма для отгрузки
class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment  # Используем модель Shipment
        fields = ['product', 'batch', 'quantity', 'shipment_date', 'counterparty']  # Поля формы
        labels = {
            'product': 'Продукт',  # Метка для продукта
            'batch': 'Партия',  # Метка для партии
            'quantity': 'Количество',  # Метка для количества
            'shipment_date': 'Дата отгрузки',  # Метка для даты отгрузки
            'counterparty': 'Контрагент',  # Метка для контрагента
        }
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control', 'onchange': 'this.form.submit()'}),  # Виджет для выбора продукта с автоматической отправкой формы
            'batch': forms.Select(attrs={'class': 'form-control'}),  # Виджет для выбора партии
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),  # Виджет для ввода количества
            'shipment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),  # Виджет для выбора даты
            'counterparty': forms.Select(attrs={'class': 'form-control'}),  # Виджет для выбора контрагента
        }
        error_messages = {
            'product': {
                'required': 'Это поле обязательно.',  # Сообщение об ошибке для продукта
            },
            'batch': {
                'required': 'Это поле обязательно.',  # Сообщение об ошибке для партии
            },
            'quantity': {
                'required': 'Это поле обязательно.',  # Сообщение об ошибке для количества
            },
            'shipment_date': {
                'required': 'Это поле обязательно.',  # Сообщение об ошибке для даты отгрузки
                'invalid': 'Введите правильную дату.',  # Сообщение об ошибке для неправильного формата даты
            },
            'counterparty': {
                'required': 'Это поле обязательно.',  # Сообщение об ошибке для контрагента
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Инициализация выборок для продуктов и контрагентов
        self.fields['product'].queryset = Product.objects.all()
        self.fields['counterparty'].queryset = Counterparty.objects.all()

        # Обновление списка партий в зависимости от выбранного продукта
        if 'product' in self.data:
            try:
                product_id = int(self.data.get('product'))
                self.fields['batch'].queryset = Batch.objects.filter(product_id=product_id, quantity__gt=0, is_used=False)
            except (ValueError, TypeError):
                self.fields['batch'].queryset = Batch.objects.none()
        else:
            self.fields['batch'].queryset = Batch.objects.none()

        # Устанавливаем текущую дату по умолчанию для новой записи
        if not self.instance.pk:  # Если это новая запись
            self.fields['shipment_date'].initial = date.today()

# Форма для контрагента
class CounterpartyForm(forms.ModelForm):
    class Meta:
        model = Counterparty  # Используем модель Counterparty
        fields = ['name', 'address', 'contact_number']  # Поля формы
        labels = {
            'name': 'Наименование',  # Метка для имени контрагента
            'address': 'Адрес',  # Метка для адреса контрагента
            'contact_number': 'Контактный номер'  # Метка для контактного номера
        }
        help_texts = {
            'name': 'Введите наименование контрагента',  # Текст подсказки для имени
            'address': 'Введите адрес контрагента',  # Текст подсказки для адреса
            'contact_number': 'Введите контактный номер'  # Текст подсказки для контактного номера
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),  # Виджет для имени контрагента
            'address': forms.TextInput(attrs={'class': 'form-control'}),  # Виджет для адреса контрагента
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),  # Виджет для контактного номера
        }