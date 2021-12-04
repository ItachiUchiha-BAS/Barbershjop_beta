from django.shortcuts import render
from django.views.generic import DetailView, View
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages

from .models import Barber, Cosmetic, Haircut, Category, LatestProducts, Customer, Cart, CartProduct
from .mixins import CategoryDetailMixin, CartMixin


class BaseView(CartMixin, View):
    def get(self,request,*args,**kwargs):

        categories = Category.objects.get_category_for_leftsidebar()
        cosmetics = LatestProducts.objects.get_products_for_main_page('cosmetic')
        haircuts = LatestProducts.objects.get_products_for_main_page('haircut')
        barbers = LatestProducts.objects.get_products_for_main_page('barber')
        context = {
            'categories': categories,
            'cosmetics' : cosmetics,

            'haircuts': haircuts,

            'barbers': barbers,
            'cart' : self.cart

        }

        return render(request, 'base.html', context)



class ProductDetailView(CartMixin, CategoryDetailMixin, DetailView):

    CT_MODEL_MODEL_CLASS = {
        'barber': Barber,
        'cosmetic': Cosmetic,
        'haircut': Haircut

    }

    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request,*args,**kwargs)

    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        return context



class CategoryDetalView(CartMixin, CategoryDetailMixin, DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detal.html'
    slug_url_kwarg = 'slug'

class AddToCartView(CartMixin, View):


    def get(self,request,*args,**kwargs):
        ct_model, products_slug = kwargs.get('ct_model'), kwargs.get('slug')

        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=products_slug)
        cart_product, created = CartProduct.objects.get_or_create(user=self.cart.owner, cart=self.cart, content_type=content_type,
                                                           object_id=product.id)
        if created:
             self.cart.products.add(cart_product)
        self.cart.save()
        messages.add_message(request, messages.INFO, "Товар успешно добавлен")
        return HttpResponseRedirect('/cart/')



class ChangeQTYView(CartMixin, View):
    def post(self,request,*args,**kwargs):
        ct_model, products_slug = kwargs.get('ct_model'), kwargs.get('slug')

        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=products_slug)
        cart_product, created = CartProduct.objects.get_or_create(user=self.cart.owner, cart=self.cart,
                                                                  content_type=content_type,
                                                                  object_id=product.id)
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        self.cart.save()
        messages.add_message(request, messages.INFO, "Кол-во  успешно изменено")
        return HttpResponseRedirect('/cart/')




class DeleteFromCartView(CartMixin, View):


    def get(self, request, *args,  **kwargs):

        ct_model, products_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=products_slug)
        cart_product = CartProduct.objects.get(user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id)
        self.cart.products.remove(cart_product)
        cart_product.delete()
        self.cart.save()
        messages.add_message(request, messages.INFO, "Товар успешно удален")
        return HttpResponseRedirect('/cart/')


class CartView(CartMixin, View):

    def get(self,request,*args,**kwargs):

        categories = Category.objects.get_category_for_leftsidebar()
        context = {
            'cart' : self.cart,
            'categories' : categories
        }
        return render(request, 'cart.html', context)

