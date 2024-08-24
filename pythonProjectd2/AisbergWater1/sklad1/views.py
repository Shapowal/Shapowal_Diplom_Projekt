from django.contrib import messages
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
            return redirect('production')  # Перенаправляем на страницу производства
    else:
        form = CustomUserCreationForm()  # Пустая форма для GET-запросов

    role_choices = CustomUser.ROLE_CHOICES  # Получаем варианты ролей для выбора
    return render(request, 'autentification/register.html', {'form': form, 'role_choices': role_choices})

# Вход пользователя в систему
def login_view(request):
    """Страница входа пользователя в систему"""
    error = None
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
            error = 'Неправильное имя пользователя или пароль'

    return render(request, 'autentification/login.html', {'error': error})

# Главная страница
def home(request):
    """Главная страница сайта"""
    return render(request, 'page_web/home.html')

# Представления для страниц склада и производства
def warehouse_view(request):
    """Страница склада"""
    return render(request, 'warehause_page/warehouse.html')

def production_view(request):
    """Страница производства"""
    return render(request, 'warehause_page/production.html')

def finished_goods_warehouse_view(request):
    """Страница склада готовой продукции"""
    return render(request, 'warehause_page/finished_goods_warehouse.html')

def finished_goods_stock(request):
    """Страница остатков готовой продукции на складе"""
    # Получаем все партии, у которых количество больше нуля и которые не были использованы
    batches = Batch.objects.filter(quantity__gt=0, is_used=False)
    return render(request, 'warehause_page/finished_goods_stock_list.html', {'batches': batches})

def production_main(request):
    """Основная страница производства"""
    return render(request, 'warehause_page/production_main.html')

# Создание новой линии
def create_line(request):
    """Создание новой производственной линии"""
    if request.method == 'POST':
        form = LineForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем новую линию
            messages.success(request, 'Линия успешно создана!')  # Сообщение об успехе
            return redirect('line_list')  # Перенаправляем на список линий
        else:
            messages.error(request, 'Произошла ошибка при создании линии. Пожалуйста, проверьте форму.')  # Сообщение об ошибке
    else:
        form = LineForm()  # Пустая форма для GET-запросов

    return render(request, 'lines/create_line.html', {'form': form})

# Список всех линий
class LineListView(ListView):
    """Список всех производственных линий"""
    model = Line
    template_name = 'lines/line_list.html'
    context_object_name = 'lines'
    ordering = ['number']

# Добавление продукта на линию
def add_product_to_line(request):
    """Добавление продукта на производственную линию"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем продукт
            messages.success(request, 'Продукт успешно добавлен на линию!')  # Сообщение об успехе
            return redirect('product_list')  # Перенаправляем на список продуктов
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')  # Сообщение об ошибке
    else:
        form = ProductForm()  # Пустая форма для GET-запросов

    return render(request, 'lines/add_product.html', {'form': form})

# Список всех продуктов и линий
def product_list(request):
    """Список всех продуктов и линий"""
    products = Product.objects.all()  # Получаем все продукты
    lines = Line.objects.all()  # Получаем все линии
    return render(request, 'lines/product_list.html', {'products': products, 'lines': lines})

# Создание новой партии
def create_batch(request):
    """Создание новой партии продукции"""
    if request.method == 'POST':
        line_id = request.POST.get('line')  # Получаем ID линии
        form = BatchForm(request.POST, line_id=line_id)

        if form.is_valid():
            batch = form.save(commit=False)  # Создаем партию без сохранения
            batch.is_used = False  # Устанавливаем значение по умолчанию
            batch.save()  # Сохраняем партию
            messages.success(request, 'Партия успешно создана!')  # Сообщение об успехе
            return redirect('batch_list')  # Перенаправляем на список партий
        else:
            print("Form is not valid")
            print(form.errors)  # Отладка: Печать ошибок формы
            print("POST data:", request.POST)  # Отладка: Печать данных POST-запроса
    else:
        line_id = request.GET.get('line')  # Получаем ID линии для GET-запросов
        form = BatchForm(line_id=line_id)

    lines = Line.objects.all()  # Получаем все линии
    return render(request, 'lines/create_batch.html', {'form': form, 'lines': lines, 'selected_line_id': line_id})

# Список всех партий с фильтрацией по дате
def batch_list(request):
    """Список всех партий с возможностью фильтрации по дате и продукту"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    product_id = request.GET.get('product_id')

    # Фильтрация по дате и продукту
    filters = {}
    if start_date and end_date:
        filters['production_date__range'] = [start_date, end_date]
    if product_id:
        filters['product_id'] = product_id

    batches = Batch.objects.filter(**filters)  # Применяем фильтры

    # Получаем список продуктов для фильтрации
    products = Product.objects.all()

    return render(request, 'lines/batch_list.html', {'batches': batches, 'products': products})

# Загрузка продуктов по линии
def load_products(request):
    """Загрузка продуктов, доступных на выбранной линии"""
    line_id = request.GET.get('line_id')
    products = Product.objects.filter(line_id=line_id).order_by('name')  # Получаем продукты по линии
    return JsonResponse({'products': list(products.values('id', 'name'))})  # Возвращаем продукты в формате JSON

# Добавление количества к партии
# Эту функцию необходимо реализовать, если требуется функциональность для добавления количества к партии

# Представления для страниц со складами и остатками
def warehouse(request):
    """Страница склада"""
    return render(request, 'warehause_page/warehouse.html')

# Просмотр остатков материалов на складе
def view_stock(request):
    # Получаем все материалы
    materials = Material.objects.all()
    return render(request, 'materials/view_stock.html', {'materials': materials})

# Прием материалов на склад (временная страница)
def receive_materials(request):
    return render(request, 'stub.html', {'message': 'Прием материалов на склад'})

# Списание остатков (временная страница)
def write_off_stock(request):
    return render(request, 'stub.html', {'message': 'Списание остатков'})

# Проверка расхода за период (временная страница)
def check_expenses(request):
    return render(request, 'stub.html', {'message': 'Проверка расхода за период'})

# Просмотр остатков готовой продукции
def view_finished_goods_stock(request):
    # Получаем все партии, у которых количество больше нуля и которые не были использованы
    batches = Batch.objects.filter(quantity__gt=0, is_used=False)
    return render(request, 'warehause_page/finished_goods_stock_list.html', {'batches': batches})

# Поступление готовой продукции за период (временная страница)
def receive_finished_goods(request):
    return render(request, 'stub.html', {'message': 'Поступление готовой продукции за период'})

# Отгрузка готовой продукции (временная страница)
def ship_finished_goods(request):
    return render(request, 'stub.html', {'message': 'Отгрузка готовой продукции'})

# Создание нового материала
def create_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Материал успешно создан!')
            return redirect('material_list')  # Перенаправление на список материалов
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
    else:
        form = MaterialForm()
    return render(request, 'materials/create_material.html', {'form': form})

# Добавление материала к продукту
def create_product_material(request):
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
def material_list(request):
    materials = Material.objects.all()
    return render(request, 'materials/material_list.html', {'materials': materials})

# Список всех связей продуктов и материалов
def product_material_list(request):
    product_materials = ProductMaterial.objects.all()
    return render(request, 'materials/product_material_list.html', {'product_materials': product_materials})

# Выпуск продукции и списание материалов
def release_products(request):
    if request.method == 'POST':
        form = ReleaseProductsForm(request.POST)
        if form.is_valid():
            batch = form.cleaned_data['batch']
            quantity = Decimal(form.cleaned_data['quantity'])  # Конвертируем количество в Decimal

            # Получаем партию по её ID
            batch_instance = get_object_or_404(Batch, id=batch.id)

            # Проверяем наличие достаточного количества материала на складе
            product_materials = ProductMaterial.objects.filter(product=batch_instance.product)
            for pm in product_materials:
                total_needed = pm.quantity * quantity
                stock_item = get_object_or_404(Stock, material=pm.material)

                if stock_item.quantity < total_needed:
                    return render(request, 'materials/release_products.html', {
                        'form': form,
                        'error': f'Недостаточно {pm.material.name} на складе.'
                    })

            # Если все проверки пройдены, обновляем количество на складе
            for pm in product_materials:
                total_needed = pm.quantity * quantity
                stock_item = get_object_or_404(Stock, material=pm.material)
                stock_item.quantity -= total_needed
                stock_item.save()

            # Обновляем количество в партии
            batch_instance.quantity = quantity
            batch_instance.save()

            # Если количество в партии стало 0, отмечаем её как использованную
            if batch_instance.quantity == 0:
                batch_instance.is_used = True
                batch_instance.save()

            # Создаем или обновляем запись в складе готовой продукции
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
def create_shipment(request):
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

    # Обновляем форму с отфильтрованными партиями
    form.fields['batch'].queryset = FinishedGoodsStock.objects.filter(quantity__gt=0, is_used=False)
    return render(request, 'warehause_page/create_shipment.html', {'form': form})

# Просмотр всех отгрузок
def view_shipments(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        shipments = Shipment.objects.filter(shipment_date__range=[start_date, end_date])
    else:
        shipments = Shipment.objects.all()

    return render(request, 'warehause_page/view_shipments.html', {'shipments': shipments})

# Проверка поступлений
def check_incoming(request):
    batches = Batch.objects.filter(quantity__gt=0, is_used=False)
    return render(request, 'warehause_page/check_incoming.html', {'batches': batches})

# Редактирование информации о готовой продукции
def edit_finished_goods(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    if request.method == 'POST':
        form = BatchForm(request.POST, instance=batch)
        if form.is_valid():
            form.save()
            return redirect('list_stock')
    else:
        form = BatchForm(instance=batch)
    return render(request, 'warehause_page/edit_finished_goods.html', {'form': form})

# Создание нового контрагента
def create_counterparty(request):
    if request.method == 'POST':
        form = CounterpartyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('counterparty_list')  # Перенаправление на список контрагентов
    else:
        form = CounterpartyForm()

    return render(request, 'warehause_page/create_counterparty.html', {'form': form})

# Список всех контрагентов
def counterparty_list(request):
    counterparties = Counterparty.objects.all()
    return render(request, 'warehause_page/counterparty_list.html', {'counterparties': counterparties})

# Добавление нового остатка
def add_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_stock')
    else:
        form = StockForm()

    return render(request, 'materials/add_stock.html', {'form': form})

# Редактирование остатка
def edit_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            return redirect('view_stock')
    else:
        form = StockForm(instance=stock)

    return render(request, 'materials/edit_stock.html', {'form': form})

# Просмотр и редактирование остатков
def view_and_edit_stock(request):
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
def finished_goods_stock_list(request):
    # Получаем все записи на складе готовой продукции
    stock = FinishedGoodsStock.objects.all()
    return render(request, 'warehause_page/finished_goods_stock_list.html', {'stock': stock})