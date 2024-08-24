from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render, get_object_or_404

from .models import *
# Форма для создания пользователя
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser  # Модель, для которой создается форма
        fields = ('username', 'password1', 'password2', 'role')  # Поля формы

# Форма для линии
class LineForm(forms.ModelForm):
    class Meta:
        model = Line  # Модель, для которой создается форма
        fields = ['name', 'volume', 'number']  # Поля формы
        labels = {
            'name': 'Наименование:',  # Метка для поля 'name'
            'volume': 'Объем:',  # Метка для поля 'volume'
            'number': 'Номер линии:'  # Метка для поля 'number'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите наименование линии'}),  # Виджет для текстового поля с классом CSS и подсказкой
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите объем', 'step': '0.1'}),  # Виджет для числового поля с классом CSS, подсказкой и шагом
            'number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер линии'})  # Виджет для числового поля с классом CSS и подсказкой
        }

# Форма для продукта
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product  # Модель, для которой создается форма
        fields = ['line', 'name', 'gtin', 'volume']  # Поля формы
        labels = {
            'line': 'Выберите линию:',  # Метка для поля 'line'
            'name': 'Наименование продукта:',  # Метка для поля 'name'
            'gtin': 'GTIN:',  # Метка для поля 'gtin'
            'volume': 'Объем:'  # Метка для поля 'volume'
        }
        widgets = {
            'line': forms.Select(attrs={'class': 'form-control'}),  # Виджет для поля выбора с классом CSS
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите наименование продукта'}),  # Виджет для текстового поля с классом CSS и подсказкой
            'gtin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите GTIN'}),  # Виджет для текстового поля с классом CSS и подсказкой
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите объем', 'step': '0.1'})  # Виджет для числового поля с классом CSS, подсказкой и шагом
        }

    def clean(self):
        cleaned_data = super().clean()
        volume = cleaned_data.get('volume')  # Получаем значение объема из очищенных данных
        line = cleaned_data.get('line')  # Получаем выбранную линию из очищенных данных

        # Проверяем соответствие объема продукта объему линии
        if line and volume:
            if volume != line.volume:
                raise forms.ValidationError('Объем продукта должен точно соответствовать объему линии.')

# Форма для партии
class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch  # Модель, для которой создается форма
        fields = ['line', 'product', 'production_date', 'quantity']  # Поля формы
        labels = {
            'line': 'Выбрать линию',  # Метка для поля 'line'
            'product': 'Добавить продукт',  # Метка для поля 'product'
            'production_date': 'Дата',  # Метка для поля 'production_date'
            'quantity': 'Количество',  # Метка для поля 'quantity'
        }
        widgets = {
            'line': forms.Select(attrs={'class': 'form-control'}),  # Виджет для поля выбора с классом CSS
            'product': forms.Select(attrs={'class': 'form-control'}),  # Виджет для поля выбора с классом CSS
            'production_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),  # Виджет для поля даты с классом CSS
            'quantity': forms.NumberInput(attrs={'class': 'form-control'})  # Виджет для числового поля с классом CSS
        }

    def __init__(self, *args, **kwargs):
        line_id = kwargs.pop('line_id', None)  # Извлекаем 'line_id' из аргументов
        super().__init__(*args, **kwargs)
        if line_id:
            # Фильтруем продукты по выбранной линии
            self.fields['product'].queryset = Product.objects.filter(line_id=line_id).order_by('name')
        else:
            self.fields['product'].queryset = Product.objects.none()  # Если 'line_id' не передан, нет доступных продуктов

        # Устанавливаем текущую дату по умолчанию
        if not self.instance.pk:  # Если это новая запись
            self.fields['production_date'].initial = date.today()

# Форма для материала
class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material  # Модель, для которой создается форма
        fields = ['name', 'unit']  # Поля формы
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название материала'}),  # Виджет для текстового поля с классом CSS и подсказкой
            'unit': forms.Select(attrs={'class': 'form-control'})  # Виджет для поля выбора с классом CSS
        }
# Форма для связи продукта с материалом
class ProductMaterialForm(forms.ModelForm):
    class Meta:
        model = ProductMaterial  # Модель, для которой создается форма
        fields = ['product', 'material', 'quantity']  # Поля формы
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),  # Виджет для выбора продукта с классом CSS
            'material': forms.Select(attrs={'class': 'form-control'}),  # Виджет для выбора материала с классом CSS
            'quantity': forms.NumberInput(attrs={'class': 'form-control'})  # Виджет для ввода количества с классом CSS
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем список доступных продуктов
        self.fields['product'].queryset = Product.objects.all()
        # Устанавливаем список доступных материалов
        self.fields['material'].queryset = Material.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')  # Получаем выбранный продукт
        material = cleaned_data.get('material')  # Получаем выбранный материал

        # Проверяем, не добавлен ли уже этот материал к продукту
        if ProductMaterial.objects.filter(product=product, material=material).exists():
            raise forms.ValidationError('Этот материал уже добавлен к продукту.')

# Форма для создания/редактирования остатков на складе
class StockForm(forms.ModelForm):
    class Meta:
        model = Stock  # Модель, для которой создается форма
        fields = ['material', 'quantity']  # Поля формы
        widgets = {
            'material': forms.Select(attrs={'class': 'form-control'}),  # Виджет для выбора материала с классом CSS
            'quantity': forms.NumberInput(attrs={'class': 'form-control'})  # Виджет для ввода количества с классом CSS
        }

# Форма для выпуска продукции
class ReleaseProductsForm(forms.Form):
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.filter(is_used=False).order_by('batch_number'),
        label="Выберите партию",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.DecimalField(
        label="Количество для выпуска",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

# Форма для отгрузки
class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment  # Модель, для которой создается форма
        fields = ['product', 'batch', 'quantity', 'shipment_date', 'counterparty']  # Поля формы
        labels = {
            'product': 'Продукт',  # Метка для поля 'product'
            'batch': 'Партия',  # Метка для поля 'batch'
            'quantity': 'Количество',  # Метка для поля 'quantity'
            'shipment_date': 'Дата отгрузки',  # Метка для поля 'shipment_date'
            'counterparty': 'Контрагент',  # Метка для поля 'counterparty'
        }
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control', 'onchange': 'this.form.submit()'}),  # Виджет для выбора продукта с классом CSS и автоматическим обновлением формы при изменении выбора
            'batch': forms.Select(attrs={'class': 'form-control'}),  # Виджет для выбора партии с классом CSS
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),  # Виджет для ввода количества с классом CSS и минимальным значением 1
            'shipment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),  # Виджет для выбора даты с классом CSS
            'counterparty': forms.Select(attrs={'class': 'form-control'})  # Виджет для выбора контрагента с классом CSS
        }
        error_messages = {
            'product': {
                'required': 'Это поле обязательно.',  # Сообщение об ошибке, если поле 'product' не заполнено
            },
            'batch': {
                'required': 'Это поле обязательно.',  # Сообщение об ошибке, если поле 'batch' не заполнено
            },
            'quantity': {
                'required': 'Это поле обязательно.',  # Сообщение об ошибке, если поле 'quantity' не заполнено
            },
            'shipment_date': {
                'required': 'Это поле обязательно.',  # Сообщение об ошибке, если поле 'shipment_date' не заполнено
                'invalid': 'Введите правильную дату.',  # Сообщение об ошибке, если введена неправильная дата
            },
            'counterparty': {
                'required': 'Это поле обязательно.',  # Сообщение об ошибке, если поле 'counterparty' не заполнено
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем список доступных продуктов и контрагентов
        self.fields['product'].queryset = Product.objects.all()
        self.fields['counterparty'].queryset = Counterparty.objects.all()

        # Обновляем список партий в зависимости от выбранного продукта
        if 'product' in self.data:
            try:
                product_id = int(self.data.get('product'))  # Получаем ID выбранного продукта
                self.fields['batch'].queryset = Batch.objects.filter(product_id=product_id, quantity__gt=0, is_used=False)  # Фильтруем партии по продукту
            except (ValueError, TypeError):
                self.fields['batch'].queryset = Batch.objects.none()  # Если возникла ошибка, нет доступных партий
        else:
            self.fields['batch'].queryset = Batch.objects.none()  # Если продукт не выбран, нет доступных партий

        # Устанавливаем текущую дату по умолчанию
        if not self.instance.pk:  # Если это новая запись
            self.fields['shipment_date'].initial = date.today()

# Форма для контрагента
class CounterpartyForm(forms.ModelForm):
    class Meta:
        model = Counterparty  # Модель, для которой создается форма
        fields = ['name', 'address', 'contact_number']  # Поля формы
        labels = {
            'name': 'Наименование',  # Метка для поля 'name'
            'address': 'Адрес',  # Метка для поля 'address'
            'contact_number': 'Контактный номер'  # Метка для поля 'contact_number'
        }
        help_texts = {
            'name': 'Введите наименование контрагента',  # Подсказка для поля 'name'
            'address': 'Введите адрес контрагента',  # Подсказка для поля 'address'
            'contact_number': 'Введите контактный номер'  # Подсказка для поля 'contact_number'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),  # Виджет для текстового поля с классом CSS
            'address': forms.TextInput(attrs={'class': 'form-control'}),  # Виджет для текстового поля с классом CSS
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),  # Виджет для текстового поля с классом CSS
        }