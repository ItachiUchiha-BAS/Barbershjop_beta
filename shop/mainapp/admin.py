from django.contrib import admin
from .models import *
from django.forms import ModelChoiceField

# Register your models here.







class BarberAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='barber'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)







class CosmeticAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='cosmetic'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)






class HaircutAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='haircut'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Category)
admin.site.register(Barber, BarberAdmin)
admin.site.register(Cosmetic, CosmeticAdmin)
admin.site.register(Haircut, HaircutAdmin)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(CartProduct)
admin.site.register(Order)