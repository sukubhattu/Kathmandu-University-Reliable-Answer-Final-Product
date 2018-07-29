from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.urls import reverse

from .forms import NewTopicForm, PostForm
from .models import Board, Post, Topic,PostVote,TopicVote


class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

            topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )

            return redirect(topic_post_url)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})

@login_required
def PostUpvote(request,post_id):
    votes = PostVote.objects.all()
    voted_by = request.user
    new_vote = PostVote(post_id=post_id,vote=1,voted_by=voted_by)
    if votes.filter(post_id=post_id,vote=1,voted_by=voted_by).exists():
        PostVote.objects.filter(post_id=post_id,vote=1,voted_by=voted_by).delete()
        post = Post.objects.get(id=post_id)
        post.votes -= 1
        post.save()
    elif votes.filter(post_id=post_id,vote=-1,voted_by=voted_by):
        PostVote.objects.filter(post_id=post_id,vote=-1,voted_by=voted_by).delete()
        new_vote.save()
        post = Post.objects.get(id=post_id)
        post.votes += 2
        post.save()    
    else:
        new_vote.save()
        post = Post.objects.get(id=post_id)
        post.votes += 1
        post.save()
    p = Post.objects.all()
    post = p.filter(id = post_id);
    topic_id = post.values_list('topic_id',flat = True)
    topic1 = Topic.objects.filter(id=topic_id)
    topic = Topic.objects.get(id = topic_id)
    board_id = topic1.values_list('board_id',flat=True)
    board = Board.objects.get(id=board_id)
    return redirect('topic_posts', pk=board.id, topic_pk=topic.id)

@login_required
def PostDownvote(request,post_id):
    post = Post.objects.filter(id=post_id)
    votes = PostVote.objects.all()
    voted_by = request.user
    new_vote = PostVote(post_id=post_id,vote=-1,voted_by=voted_by)
    if votes.filter(post_id=post_id,vote=-1,voted_by=voted_by).exists():
        PostVote.objects.filter(post_id=post_id,vote=-1,voted_by=voted_by).delete()
        post = Post.objects.get(id=post_id)
        post.votes += 1
        post.save()
    elif votes.filter(post_id=post_id,vote=1,voted_by=voted_by):
        PostVote.objects.filter(post_id=post_id,vote=1,voted_by=voted_by).delete()
        new_vote.save()   
        post = Post.objects.get(id=post_id)
        post.votes -= 2
        post.save() 
    else:
        new_vote.save()
        post = Post.objects.get(id=post_id)
        post.votes -= 1
        post.save()
    p = Post.objects.all()
    post = p.filter(id = post_id);
    topic_id = post.values_list('topic_id',flat = True)
    topic1 = Topic.objects.filter(id=topic_id)
    topic = Topic.objects.get(id = topic_id)
    board_id = topic1.values_list('board_id',flat=True)
    board = Board.objects.get(id=board_id)
    return redirect('topic_posts', pk=board.id, topic_pk=topic.id)


@login_required
def TopicUpvote(request,topic_id):
    votes = TopicVote.objects.all()
    voted_by = request.user
    new_vote = TopicVote(topic_id=topic_id,vote=1,voted_by=voted_by)
    if votes.filter(topic_id=topic_id,vote=1,voted_by=voted_by).exists():
        TopicVote.objects.filter(topic_id=topic_id,vote=1,voted_by=voted_by).delete()
        topic = Topic.objects.get(id=topic_id)
        topic.votes -= 1
        topic.save()
    elif votes.filter(topic_id=topic_id,vote=-1,voted_by=voted_by):
        TopicVote.objects.filter(topic_id=topic_id,vote=-1,voted_by=voted_by).delete()
        new_vote.save()
        topic = Topic.objects.get(id=topic_id)
        topic.votes += 2
        topic.save()    
    else:
        new_vote.save()
        topic = Topic.objects.get(id=topic_id)
        topic.votes += 1
        topic.save()
    topic1 = Topic.objects.filter(id=topic_id)
    topic = Topic.objects.get(id = topic_id)
    board_id = topic1.values_list('board_id',flat=True)
    board = Board.objects.get(id=board_id)
    return redirect('topic_posts', pk=board.id, topic_pk=topic.id)


@login_required
def TopicDownvote(request,topic_id):
    votes = TopicVote.objects.all()
    voted_by = request.user
    new_vote = TopicVote(topic_id=topic_id,vote=-1,voted_by=voted_by)
    if votes.filter(topic_id=topic_id,vote=-1,voted_by=voted_by).exists():
        TopicVote.objects.filter(topic_id=topic_id,vote=-1,voted_by=voted_by).delete()
        topic = Topic.objects.get(id=topic_id)
        topic.votes += 1
        topic.save()
    elif votes.filter(topic_id=topic_id,vote=1,voted_by=voted_by):
        TopicVote.objects.filter(topic_id=topic_id,vote=1,voted_by=voted_by).delete()
        new_vote.save()
        topic = Topic.objects.get(id=topic_id)
        topic.votes -= 2
        topic.save()    
    else:
        new_vote.save()
        topic = Topic.objects.get(id=topic_id)
        topic.votes -= 1
        topic.save()
    topic1 = Topic.objects.filter(id=topic_id)
    topic = Topic.objects.get(id = topic_id)
    board_id = topic1.values_list('board_id',flat=True)
    board = Board.objects.get(id=board_id)
    return redirect('topic_posts', pk=board.id, topic_pk=topic.id)


def DeletePost(request,post_pk):
    p = Post.objects.all();
    post = p.filter(id = post_pk);
    topic_id = post.values_list('topic_id',flat = True)
    topic1 = Topic.objects.filter(id=topic_id)
    topic = Topic.objects.get(id = topic_id)
    board_id = topic1.values_list('board_id',flat=True)
    board = Board.objects.get(id=board_id)
    post.delete();
    return redirect('topic_posts', pk=board.id, topic_pk=topic.id)


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)


