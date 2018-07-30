from django.contrib import admin



from .models import Board, Post, Topic, PostVote,TopicVote,Contact

class BoardAdmin(admin.ModelAdmin):
	list_display = ('name','description')

class PostAdmin(admin.ModelAdmin):
	list_display = ('message','topic','created_at','updated_at','created_by','updated_by','votes')
	
class TopicAdmin(admin.ModelAdmin):
	list_display = ['subject','last_updated','board','starter','views','votes']

class PostVoteAdmin(admin.ModelAdmin):
	list_display = ['post_id','voted_by','vote']

class TopicVoteAdmin(admin.ModelAdmin):
	list_display = ['topic_id','voted_by','vote']

class ContactAdmin(admin.ModelAdmin):
	list_display = ['name','email','feedback']

admin.site.register(Board,BoardAdmin)
admin.site.register(Post,PostAdmin)
admin.site.register(Topic,TopicAdmin)
admin.site.register(PostVote,PostVoteAdmin)
admin.site.register(TopicVote,TopicVoteAdmin)
admin.site.register(Contact,ContactAdmin)