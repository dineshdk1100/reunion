

from django.urls import path

from . import views
from .views import Authenticate, FollowUser,UnFollowUser,UserDetails,Posts,PostLike,PostUnLike,Comment,AllPost

urlpatterns = [
    path('',views.home,name='home'),
    path('create',views.create,name='create'),
    path('api/authenticate', Authenticate.as_view()),
    path('api/follow', FollowUser.as_view()),
    path('api/unfollow', UnFollowUser.as_view()),
    path('api/user', UserDetails.as_view()),
    path('api/posts', Posts.as_view()),
    path('api/like', PostLike.as_view()),
    path('api/unlike', PostUnLike.as_view()),
    path('api/comment', Comment.as_view()),
    path('api/all_posts', AllPost.as_view())


]