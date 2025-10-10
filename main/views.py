from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.http import HttpResponse
from django.template.response import TemplateResponse
from .models import Category, Product, Size
from django.db.models import Q

class IndexView(TemplateView):
    template_name = 'main/base.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_catregory'] = None
        return context


    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/home_content.html',
                                    context)
        return TemplateResponse(request, self.template_name, context)
    

class CatalogView(TemplateView):
    template = 'main/base.html'

    FILTER_MAPPING = {
        'color': lambda queryset, value: queryset.filter(color__iexact=value),
        'min_price': lambda queryset, value: queryset.filter(price__gte=value),
        'max_price': lambda queryset, value: queryset.filter(price__lte=value),
        'size': lambda queryset, value: queryset.filter(product_size__size__name=value),
    }


    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        category_slug = kwargs.get('category_slug')
        categories = Category.objects.all()
        products = Product.objects.all().order_by('-created_at')
        current_category = None

        if category_slug:
            current_category = get_object_or_404(Category, slug = category_slug)
            products = products.filter(category = current_category)

        query = self.request.GET.get('q')
        if query:
            products = products.filter(
                Q(name__icontains = query) | Q(description__icontains = query)
            )

        filter_params = {}
        for param, filter_func in self.FILTER_MAPPING.items():
            value = self.request.GET.get(param)
            if value:
                products = filter_func(products, value)
        return