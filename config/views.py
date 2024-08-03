from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.shortcuts import redirect
from .filters import AdvertFilter
from .forms import AdvertForm, ReviewForm
from .models import Advert
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.views.decorators.csrf import csrf_protect
from .models import Subscription, Category

class AdvertList(ListView):
    """Все объявления"""
    model = Advert
    context_object_name = 'advert'
    queryset = Advert.objects.all()
    template_name = 'board/advert-list.html'
    paginate_by = 3


    # Переопределяем функцию получения списка товаров
    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = AdvertFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        return context

class AdvertDetail(DetailView):
    """Подробно об объявлении"""
    model = Advert
    context_object_name = "advert"
    template_name = 'board/advert-detail.html'


# Добавляем новое представление для создания товаров.
class AdvertCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('config.add_advert',)
    raise_exception = True
    # Указываем нашу разработанную форму
    form_class = AdvertForm
    # модель товаров
    model = Advert
    # и новый шаблон, в котором используется форма.
    template_name = 'board/advert_edit.html'


class AdvertUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('config.change_advert',)
    raise_exception = True
    form_class = AdvertForm
    model = Advert
    template_name = 'board/advert_edit.html'



class AdvertDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('config.delete_advert', )
    raise_exception = True
    model = Advert
    template_name = 'board/advert_delete.html'
    success_url = reverse_lazy('advert-list')
   # success_url = 'http://127.0.0.1:8000'


class AddReview(View):
    """Отзывы"""
    def post(self, request, pk):
        form = ReviewForm(request.POST)
        advert = Advert.objects.get(id=pk)
        if form.is_valid():
            form = form.save(commit=False)
            form.advert = advert
            form.save()
        return redirect('/')


@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscription.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscription.objects.filter(
                user=request.user,
                category=category,
            ).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscription.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('name')
    return render(
        request,
        'subscriptions.html',
        {'categories': categories_with_subscriptions},
    )
