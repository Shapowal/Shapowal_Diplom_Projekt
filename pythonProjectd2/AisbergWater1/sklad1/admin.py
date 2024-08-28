from django.contrib import admin
from .models import CustomUser, Line, Product, Batch, FinishedGoodsStock

admin.site.register(CustomUser)
admin.site.register(Line)
admin.site.register(Product)
admin.site.register(Batch)
@admin.register(FinishedGoodsStock)
class FinishedGoodsStockAdmin(admin.ModelAdmin):
    list_display = ('product', 'batch_number', 'production_date', 'quantity')
    search_fields = ('product__name', 'batch_number')
    list_filter = ('product', 'production_date')