from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.utils import  timezone


User = get_user_model()


def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]


def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})

class CategoryManager(models.Manager):

    CATEGORY_NAME = {
        'Barber': 'barber__count',
        'Haircut': 'haircut__count',
        'Cosmetic': 'cosmetic__count'
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_category_for_leftsidebar(self):
        models = get_models_for_count('barber', 'haircut', 'cosmetic')
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME[c.name]))for c in qs
        ]
        return data


class LatestProductsManager:
    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models =ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:10]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True)


        return products




class LatestProducts:

    objects = LatestProductsManager()

class Category(models.Model):
    name = models.CharField(max_length=255,verbose_name='Имя категории')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

class Product(models.Model):

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Наименование')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')
    price = models.DecimalField(max_digits=9,decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return self.title

    def get_model_name(self):
        return self.__class__.__name__.lower()




class CartProduct(models.Model):

     user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
     cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
     object_id = models.PositiveIntegerField()
     content_object = GenericForeignKey('content_type','object_id')
     qty = models.PositiveIntegerField(default=1)
     final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')

     def __str__(self):
         return "Продукт: {}(для корзины)".format(self.content_object.title)

     def save(self,*args,**kwargs):
         self.final_price = self.qty * self.content_object.price
         super().save(*args,**kwargs)



class Cart(models.Model):

    owner = models.ForeignKey('Customer', null=True, verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_product = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)


    def __str__(self):
        return  str(self.id)

    def save(self, *args, **kwargs):
        cart_data= self.products.aggregate(models.Sum('final_price'), models.Count('id'))
        if cart_data.get('final_price__sum'):
            self.final_price = cart_data['final_price__sum']
        else:
            self.final_price = 0
        self.total_product = cart_data['id__count']
        super().save(*args, **kwargs)

class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20,verbose_name='Номер телефона',null=True,blank=True)
    address = models.CharField(max_length=255,verbose_name='Адрес',null=True,blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Заказы покупателя', related_name='related_customer')

    def __str__(self):
        return "Покупатель: {} {}".format(self.user.first_name, self.user.last_name)




class Cosmetic(Product):
    boxer = models.CharField(max_length=10, verbose_name='Дизайн бокса', default='box')

    type_of_hold = models.CharField(max_length=255, verbose_name='Тип укладки')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)


    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')




class Barber(Product):

    rank = models.CharField(max_length=255,verbose_name='Должность')
    vk = models.CharField(max_length=255,verbose_name='вк')
    inst = models.CharField(max_length=255,verbose_name='Инста')
    twitter = models.CharField(max_length=255,verbose_name='Твиттер')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')



class Haircut(Product):

    hair_type = models.CharField(max_length=255, verbose_name='Тип волос')

    type_of_hold = models.CharField(max_length=255, verbose_name='Тип укладки')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')

class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_DELIVERY,'Доставка'),
        (BUYING_TYPE_SELF,'Самовывоз')
    )

    STATUS_CHOICES = (
        (STATUS_NEW,'Новый заказ'),(STATUS_IN_PROGRESS,'Заказ в обработке'),(STATUS_READY,'Заказ готов'),
        (STATUS_COMPLETED,'Заказ выполнен')
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупатель',related_name='related_orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255,verbose_name='Имя')
    last_name = models.CharField(max_length=255,verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.CharField(max_length=255, verbose_name='Адрес', null=True, blank=True)
    status = models.CharField(max_length=100,verbose_name='Статус заказа', choices=STATUS_CHOICES,default=STATUS_NEW)
    buying_type = models.CharField(max_length=100,verbose_name='Тип заказа', choices=BUYING_TYPE_CHOICES,default=BUYING_TYPE_SELF)
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True,blank=True)

    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateField(verbose_name='Дата получения заказа', default=timezone.now)

    def __str__(self):
        return str(self.id)