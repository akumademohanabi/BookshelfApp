from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic, View
from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Avg
from django.core.paginator import Paginator
from .models import Shelf, Review, Favorite

# 本の一覧
class ListBookView(generic.ListView):
    template_name = 'book/book_list.html'
    model = Shelf
    context_object_name = 'Shelf'
    queryset = Shelf.objects.all().order_by('-id')  # 登録順（降順）に並べ替え

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # レビュー平均でソートして上位3冊を取得
        ranking_list = (
            Shelf.objects.annotate(avg_rating=Avg('review__rate')).order_by('-avg_rating')[:3]
        )
        context['ranking_list'] = ranking_list
        return context


# 本の詳細
class DetailBookView(generic.DetailView):
    template_name = 'book/book_detail.html'
    model = Shelf
    context_object_name = 'Shelf'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 本に関連するレビューを取得
        reviews = Review.objects.filter(book=self.object).order_by('-id')  # 最新のレビュー順
        paginator = Paginator(reviews, 3)  # 1ページに3件表示
        page_number = self.request.GET.get('page')
        context['reviews'] = paginator.get_page(page_number)

        # お気に入り状態を追加（ログインユーザーのみ）
        if self.request.user.is_authenticated:
            context['is_favorited'] = Favorite.objects.filter(user=self.request.user, book=self.object).exists()

        return context


# 本の追加
class CreateBookView(LoginRequiredMixin, generic.CreateView):
    template_name = 'book/book_create.html'
    model = Shelf
    context_object_name = 'Shelf'
    fields = ('title', 'text', 'category', 'thumbnail')
    success_url = reverse_lazy('list-book')

    def form_valid(self, form):
        form.instance.user = self.request.user  # ログイン中のユーザーを設定
        return super().form_valid(form)


# 本の削除
class DeleteBookView(LoginRequiredMixin, generic.DeleteView):
    template_name = 'book/book_confirm_delete.html'
    model = Shelf
    context_object_name = 'Shelf'
    success_url = reverse_lazy('list-book')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise PermissionDenied('削除権限がありません。')
        return super().dispatch(request, *args, **kwargs)


# 本の編集
class UpdateBookView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'book/book_update.html'
    model = Shelf
    context_object_name = 'Shelf'
    fields = ('title', 'text', 'category', 'thumbnail')
    success_url = reverse_lazy('list-book')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise PermissionDenied('編集権限がありません。')
        return super().dispatch(request, *args, **kwargs)


# レビュー機能
class CreateReviewView(LoginRequiredMixin, generic.CreateView):
    model = Review
    fields = ('book', 'title', 'text', 'rate')
    template_name = 'book/review_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = Shelf.objects.get(pk=self.kwargs['book_id'])
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('detail-book', kwargs={'pk': self.object.book.id})


# お気に入り登録・解除
class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        book = get_object_or_404(Shelf, id=self.kwargs['book_id'])
        favorite, created = Favorite.objects.get_or_create(user=request.user, book=book)

        if created:
            messages.success(request, f"『{book.title}』をお気に入りに追加しました！")
        else:
            favorite.delete()
            messages.success(request, f"『{book.title}』をお気に入りから削除しました！")

        return redirect('detail-book', pk=book.id)


# お気に入り一覧ページ
class FavoriteListView(LoginRequiredMixin, generic.ListView):
    template_name = 'book/favorite_list.html'
    context_object_name = 'favorites_books'

    def get_queryset(self):
        return Shelf.objects.filter(favorite__user=self.request.user).distinct()
