from django.contrib import messages
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.generic import ListView
from .forms import *
from .models import *

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.generic import ListView
from .forms import *
from .models import *


# Регистрация нового пользователя
def register(request):
    """Регистрация нового пользователя и автоматический вход в систему"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Сохраняем нового пользователя
            login(request, user)  # Входим в систему
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('production')  # Перенаправляем на страницу производства
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
            print(form.errors)  # Для отладки
    else:
        form = CustomUserCreationForm()  # Пустая форма для GET-запросов

    role_choices = CustomUser.ROLE_CHOICES  # Получаем варианты ролей для выбора
    return render(request, 'autentification/register.html', {'form': form, 'role_choices': role_choices})


# Вход пользователя в систему
def login_view(request):
    """Страница входа пользователя в систему"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get('remember')  # Получаем значение чекбокса "Запомнить меня"

        user = authenticate(request, username=username, password=password)  # Проверяем учетные данные
        if user is not None:
            login(request, user)  # Входим в систему

            # Устанавливаем время жизни сессии в зависимости от чекбокса "Запомнить меня"
            if remember_me:
                request.session.set_expiry(1209600)  # 2 недели в секундах
            else:
                request.session.set_expiry(0)  # До закрытия браузера

            return redirect('production')  # Перенаправляем на страницу производства
        else:
            # Передаем ошибку в контексте
            messages.success(request, 'Проверьте правильность ввода ')
            return render(request, 'autentification/login.html')

    return render(request, 'autentification/login.html')


# Главная страница
def home(request):
    """Отображает главную страницу."""
    return render(request, 'page_web/home.html')


# Представления для страниц склада и производства
@login_required
def warehouse_view(request):
    """Отображает страницу склада."""
    return render(request, 'warehause_page/warehouse.html')

@login_required
def production_view(request):
    """Отображает страницу производства."""
    return render(request, 'warehause_page/production.html')

@login_required
def finished_goods_warehouse_view(request):
    """Отображает страницу склада готовой продукции."""
    return render(request, 'warehause_page/finished_goods_warehouse.html')

@login_required
def finished_goods_stock(request):
    """Отображает список партий готовой продукции с ненулевым количеством."""
    batches = Batch.objects.filter(quantity__gt=0, is_used=False)
    return render(request, 'warehause_page/finished_goods_stock_list.html', {'batches': batches})

@login_required
def production_main(request):
    """Отображает главную страницу производства."""
    return render(request, 'warehause_page/production_main.html')


# Создание новой линии
@login_required
def create_line(request):
    """Обрабатывает создание новой производственной линии."""
    if request.method == 'POST':
        form = LineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Линия успешно создана!')
            return redirect('line_list')
        else:
            messages.error(request, 'Произошла ошибка при создании линии. Пожалуйста, проверьте форму.')
    else:
        form = LineForm()
    return render(request, 'lines/create_line.html', {'form': form})


# Список всех линий
class LineListView(ListView):
    """Отображает список всех производственных линий."""
    model = Line
    template_name = 'lines/line_list.html'
    context_object_name = 'lines'
    ordering = ['number']


# Добавление продукта на линию
@login_required
def add_product_to_line(request):
    """Обрабатывает добавление продукта на производственную линию."""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Продукт успешно добавлен на линию!')
            return redirect('product_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
    else:
        form = ProductForm()
    return render(request, 'lines/add_product.html', {'form': form})


# Список всех продуктов и линий
@login_required
def product_list(request):
    """Отображает список всех продуктов и линий."""
    products = Product.objects.all()
    lines = Line.objects.all()
    return render(request, 'lines/product_list.html', {'products': products, 'lines': lines})


# Создание новой партии
@login_required
def create_batch(request):
    if request.method == 'POST':
        line_id = request.POST.get('line')
        form = BatchForm(request.POST, line_id=line_id)

        if form.is_valid():
            form.save()
            messages.success(request, 'Партия успешно создана!')
            return redirect('batch_list')
        else:
            print("Form is not valid")
            print(form.errors)  # Отладка: Печать ошибок формы
            print("POST data:", request.POST)  # Отладка: Печать данных POST-запроса
    else:
        line_id = request.GET.get('line')
        form = BatchForm(line_id=line_id)

    lines = Line.objects.all()
    return render(request, 'lines/create_batch.html', {'form': form, 'lines': lines, 'selected_line_id': line_id})



# Список всех партий с фильтрацией по дате
@login_required
def batch_list(request):
    """Отображает список партий продукции с возможностью фильтрации по дате и продукту."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    product_id = request.GET.get('product_id')

    # Фильтрация по дате и продукту
    filters = {}
    if start_date and end_date:
        filters['production_date__range'] = [start_date, end_date]
    if product_id:
        filters['product_id'] = product_id

    batches = Batch.objects.filter(**filters)

    # Получаем список продуктов для фильтрации
    products = Product.objects.all()

    return render(request, 'lines/batch_list.html', {'batches': batches, 'products': products})


# Загрузка продуктов по линии
@login_required
def load_products(request):
    """Возвращает список продуктов для выбранной линии в формате JSON."""
    line_id = request.GET.get('line_id')
    products = Product.objects.filter(line_id=line_id).order_by('name')
    return JsonResponse({'products': list(products.values('id', 'name'))})


# Добавление количества к партии
# (Функция не реализована в текущем коде)

# Представления для страниц со складами и остатками
@login_required
def warehouse(request):
    """Отображает страницу склада."""
    return render(request, 'warehause_page/warehouse.html')

@login_required
def view_stock(request):
    """Отображает список всех материалов на складе."""
    materials = Material.objects.all()
    return render(request, 'materials/view_stock.html', {'materials': materials})

@login_required
def view_finished_goods_stock(request):
    """Отображает список всех партий готовой продукции с ненулевым количеством."""
    batches = Batch.objects.filter(quantity__gt=0, is_used=False)
    return render(request, 'warehause_page/finished_goods_stock_list.html', {'batches': batches})


# Создание нового материала
@login_required
def create_material(request):
    """Обрабатывает создание нового материала."""
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Материал успешно создан!')
            return redirect('material_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
    else:
        form = MaterialForm()
    return render(request, 'materials/create_material.html', {'form': form})


# Добавление материала к продукту
@login_required
def create_product_material(request):
    """Обрабатывает добавление материала к продукту."""
    if request.method == 'POST':
        form = ProductMaterialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Материал успешно добавлен к продукту!')
            return redirect('product_material_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
    else:
        form = ProductMaterialForm()
    return render(request, 'materials/create_product_material.html', {'form': form})


# Список всех материалов
@login_required
def material_list(request):
    """Отображает список всех материалов."""
    materials = Material.objects.all()
    return render(request, 'materials/material_list.html', {'materials': materials})


# Список всех связей продуктов и материалов
@login_required
def product_material_list(request):
    """Отображает список всех связей продуктов и материалов."""
    product_materials = ProductMaterial.objects.all()
    return render(request, 'materials/product_material_list.html', {'product_materials': product_materials})


# Выпуск продукции и списание материалов
@login_required
def release_products(request):
    """Обрабатывает выпуск продукции и списание материалов со склада."""
    if request.method == 'POST':
        form = ReleaseProductsForm(request.POST)
        if form.is_valid():
            batch = form.cleaned_data['batch']
            quantity = Decimal(form.cleaned_data['quantity'])  # Конвертируем в Decimal

            # Получаем партию по её ID
            batch_instance = get_object_or_404(Batch, id=batch.id)

            # Проверяем, достаточно ли материала на складе
            product_materials = ProductMaterial.objects.filter(product=batch_instance.product)
            for pm in product_materials:
                total_needed = pm.quantity * quantity
                stock_item = get_object_or_404(Stock, material=pm.material)

                if stock_item.quantity < total_needed:
                    return render(request, 'materials/release_products.html', {
                        'form': form,
                        'error': f'Недостаточно {pm.material.name} на складе.'
                    })

            # Если проверка пройдена, обновляем количество на складе
            for pm in product_materials:
                total_needed = pm.quantity * quantity
                stock_item = get_object_or_404(Stock, material=pm.material)
                stock_item.quantity -= total_needed
                stock_item.save()

            # Обновляем количество в партии
            batch_instance.quantity = quantity
            batch_instance.save()

            # Если количество в партии стало 0, отметить её как использованную
            if batch_instance.quantity == 0:
                batch_instance.is_used = True
                batch_instance.save()

            # Создаем запись в складе готовой продукции
            finished_goods, created = FinishedGoodsStock.objects.get_or_create(
                product=batch_instance.product,
                batch_number=batch_instance.batch_number,
                production_date=batch_instance.production_date,
            )
            finished_goods.update_quantity(quantity)  # Обновляем количество на складе готовой продукции

            messages.success(request, 'Продукция успешно выпущена.')
            return redirect('finished_goods_warehouse')
    else:
        form = ReleaseProductsForm()

    return render(request, 'materials/release_products.html', {'form': form})


# Создание новой отгрузки
@login_required
def create_shipment(request):
    """Обрабатывает создание новой отгрузки продукции."""
    if request.method == 'POST':
        form = ShipmentForm(request.POST)
        if form.is_valid():
            shipment = form.save(commit=False)
            product = shipment.product
            batch = shipment.batch
            quantity = shipment.quantity

            try:
                # Получаем запись о складе для продукта
                stock = FinishedGoodsStock.objects.get(
                    product=product,
                    batch_number=batch.batch_number,
                    production_date=batch.production_date,
                    is_used=False
                )

                # Обновляем количество на складе
                stock.update_quantity(-quantity)

                # Создаем запись об отгрузке
                shipment.save()
                messages.success(request, 'Отгрузка успешно создана.')
                return redirect('view_shipments')

            except FinishedGoodsStock.DoesNotExist:
                messages.error(request, 'Продукт не найден на складе или партия уже использована.')
                return render(request, 'warehause_page/create_shipment.html', {'form': form})

    else:
        form = ShipmentForm()

    # Обновите форму с отфильтрованными партиями
    form.fields['batch'].queryset = FinishedGoodsStock.objects.filter(quantity__gt=0, is_used=False)
    return render(request, 'warehause_page/create_shipment.html', {'form': form})


# Просмотр всех отгрузок
@login_required
def view_shipments(request):
    """Отображает список всех отгрузок с возможностью фильтрации по дате."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        shipments = Shipment.objects.filter(shipment_date__range=[start_date, end_date])
    else:
        shipments = Shipment.objects.all()

    return render(request, 'warehause_page/view_shipments.html', {'shipments': shipments})

@login_required
def check_incoming(request):
    """Отображает страницу проверки поступлений товаров на склад."""
    batches = Batch.objects.filter(quantity__gt=0, is_used=False)
    return render(request, 'warehause_page/check_incoming.html', {'batches': batches})

@login_required
def edit_finished_goods(request, batch_id):
    """Обрабатывает редактирование данных о готовой продукции."""
    batch = get_object_or_404(Batch, id=batch_id)
    if request.method == 'POST':
        form = BatchForm(request.POST, instance=batch)
        if form.is_valid():
            form.save()
            return redirect('list_stock')
    else:
        form = BatchForm(instance=batch)
    return render(request, 'warehause_page/edit_finished_goods.html', {'form': form})

@login_required
def create_counterparty(request):
    """Обрабатывает создание нового контрагента."""
    if request.method == 'POST':
        form = CounterpartyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('counterparty_list')
    else:
        form = CounterpartyForm()

    return render(request, 'warehause_page/create_counterparty.html', {'form': form})

@login_required
def counterparty_list(request):
    """Отображает список всех контрагентов."""
    counterparties = Counterparty.objects.all()
    return render(request, 'warehause_page/counterparty_list.html', {'counterparties': counterparties})


# Представление для добавления остатка
@login_required
def add_stock(request):
    """Обрабатывает добавление нового остатка на склад."""
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_stock')
    else:
        form = StockForm()

    return render(request, 'materials/add_stock.html', {'form': form})


# Представление для редактирования остатка
@login_required
def edit_stock(request, stock_id):
    """Обрабатывает редактирование остатка на складе."""
    stock = get_object_or_404(Stock, id=stock_id)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            return redirect('view_stock')
    else:
        form = StockForm(instance=stock)

    return render(request, 'materials/edit_stock.html', {'form': form})


# Представление для просмотра и редактирования остатков
@login_required
def view_and_edit_stock(request):
    """Отображает список всех остатков и позволяет редактировать их."""
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock_id = form.cleaned_data.get('id')
            stock_item = get_object_or_404(Stock, id=stock_id)
            stock_item.quantity = form.cleaned_data['quantity']
            stock_item.save()
            return redirect('view_and_edit_stock')
    else:
        form = StockForm()

    stocks = Stock.objects.all()
    return render(request, 'materials/view_and_edit_stock.html', {'stocks': stocks, 'form': form})


# Обновление функции для использования нового шаблона
@login_required
def finished_goods_stock_list(request):
    """Отображает список всех остатков готовой продукции."""
    stock = FinishedGoodsStock.objects.all()
    return render(request, 'warehause_page/finished_goods_stock_list.html', {'stock': stock})
