from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.conf import settings
from django.urls import reverse

from .models import Post, Group, Follow
from .forms import PostForm, CommentForm


User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    data = {
        'page': page,
        'paginator': paginator,
        'is_index': True
    }
    return render(request, 'index.html', data)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    data = {
        'group': group,
        'page': page,
        'paginator': paginator,
    }

    return render(request, 'group.html', data)


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(reverse('posts:index'))
    return render(request, 'new.html', {'form': form, 'is_create': True})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user_posts = author.posts.all()

    paginator = Paginator(user_posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    followers_count = Follow.objects.filter(author=author).count()
    following_count = Follow.objects.filter(user=author).count()

    data = {
        'author': author,
        'page': page,
        'paginator': paginator,
        'following': following_count,
        'followers': followers_count
    }
    return render(request, 'profile.html', data)


def post_view(request, username, post_id):
    user_post = get_object_or_404(Post, pk=post_id, author__username=username)
    author = user_post.author
    post_comments = user_post.comments.all()
    form = CommentForm()

    followers_count = Follow.objects.filter(author=author).count()
    following_count = Follow.objects.filter(user=author).count()

    data = {
        'author': author,
        'post': user_post,
        'comments': post_comments,
        'form': form,
        'following': following_count,
        'followers': followers_count
    }
    return render(request, 'post.html', data)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    author = post.author

    if request.user != author:
        return redirect(reverse(
            'posts:post',
            kwargs={
                'username': username,
                'post_id': post_id
            }
        ))

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(reverse(
            'posts:post',
            kwargs={
                'username': username,
                'post_id': post_id
            }
        ))

    data = {
        'form': form,
        'is_create': False,
        'author': author,
        'post': post
    }

    return render(request, 'new.html', data)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    form = CommentForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        form.save()

        return redirect(reverse(
            'posts:post',
            kwargs={
                'username': username,
                'post_id': post_id}
        ))


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    data = {
        'paginator': paginator,
        'page': page,
        'is_index': False
    }
    return render(request, 'follow.html', data)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    cur_user = request.user

    if cur_user.username != author.username:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect(reverse('posts:profile', kwargs={'username': username}))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect(reverse('posts:profile', kwargs={'username': username}))


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
