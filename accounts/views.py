from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from boards.models import Post,Topic,TopicVote
from operator import itemgetter, attrgetter, methodcaller

from .forms import SignUpForm, UserInformationUpdateForm


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email' )
    template_name = 'my_account.html'
    success_url = reverse_lazy('my_account')

    def get_object(self):
        return self.request.user


def ProfileView(request,user_id,value):
    user1 = User.objects.get(id=user_id)
    topic = Topic.objects.filter(starter_id = user_id)
    post = Post.objects.filter(created_by_id = user_id).values_list('topic_id',flat=True)
    topic_post = Post.objects.all()
    upvote = TopicVote.objects.filter(voted_by_id = user_id).values_list('topic_id',flat = True)
    topic2=[]
    for i in upvote:
        topicx = Topic.objects.get(id = i)
        topic2.append(topicx)

    post2 = []
    for i in post:
        postx = Topic.objects.get(id = i)
        post2.append(postx)
    content           = {   
        "user1":user1,
        "value":value,
        "topic":topic,
        "post":post,
        "topic_post":topic_post,
        "upvote":upvote,
        "topic2":topic2,
        "post2":post2,
    }
    return render(request,'profile.html',content)