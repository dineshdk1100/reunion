from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.
import psycopg2
import jwt, datetime

conn = psycopg2.connect(database="reunion1", user="postgres", password="dinesh1100", host="localhost", port="5432")
cur = conn.cursor()


def home(request):
    return HttpResponse("bdhb")


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        query = "select id from authenticate where email = %s and password = %s;"
        cur.execute(query, (email, password,))

        Id = cur.fetchone()
        print(Id)

        if Id == None:
            return HttpResponse('Invalid email or password')

        payload = {
            'id': Id[0],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response


class FollowUser(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')
        followingUserId = request.data['userid']
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Error")

        userId = payload['id']

        query = "insert into followings (following,follower) values (%s, %s);"
        cur.execute(query, (userId, followingUserId,))

        conn.commit()

        return HttpResponse('done')


class UnFollowUser(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')
        followingUserId = request.data['userid']
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Error")

        userId = payload['id']

        query = "delete from followings where following = %s and follower = %s;"
        cur.execute(query, (userId, followingUserId,))

        conn.commit()

        return HttpResponse('unfollowed')


class UserDetails(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Error")

        userId = payload['id']

        query = "select email from authenticate where id = %s;"
        cur.execute(query, (userId,))
        email = cur.fetchone()[0]

        query = "select count(following) from followings where following = %s;"
        cur.execute(query, (userId,))
        followings = cur.fetchone()[0]

        query = "select count(follower) from followings where follower = %s;"
        cur.execute(query, (userId,))
        followers = cur.fetchone()[0]

        conn.commit()
        print(email, followings, followers)

        response = Response()

        response.data = {
            'user name': email,
            'number of followers': followers,
            'number of following': followings
        }
        return response


class PostCreate(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')

        title = request.data['title']
        desc = request.data['desc']
        currenttime = datetime.datetime.utcnow()

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Error")

        userId = payload['id']

        query = "insert into posts (title,description,time,user_id) values ( %s,%s,%s,%s) returning post_id;"
        cur.execute(query, (title, desc, currenttime, userId,))
        post_id = cur.fetchone()[0]
        # print(post_id)
        conn.commit()

        response = Response()

        response.data = {
            'post_id': post_id,
            'title': title,
            'desc': desc,
            'createdtime': currenttime
        }

        return response


class PostDelete(APIView):
    def delete(self, request):
        token = request.COOKIES.get('jwt')

        post_id = request.data['post_id']

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Error")

        userId = payload['id']

        query = "delete from posts where post_id = %s and user_id = %s"
        cur.execute(query, (post_id, userId))
        conn.commit()

        response = Response()

        response.data = {
            'post_id': post_id
        }

        return response


class PostLike(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')

        post_id = request.data['post_id']

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Error")

        userId = payload['id']

        query = "insert into likes(post_id,liked_by) values (%s,%s);"
        cur.execute(query, (post_id, userId))
        conn.commit()

        return HttpResponse("Success")


class PostUnLike(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')

        post_id = request.data['post_id']

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Error")

        userId = payload['id']

        query = "delete from likes where post_id = %s and liked_by= %s;"
        cur.execute(query, (post_id, userId))
        conn.commit()

        return HttpResponse("Unliked")


class Comment(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')

        comment = request.data['comment']
        post_id = request.data['post_id']

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Error")

        userId = payload['id']

        query = "insert into comments (comment,post_id) values ( %s,%s) returning c_id;"
        cur.execute(query, (comment, post_id))
        comment_id = cur.fetchone()[0]
        # print(post_id)
        conn.commit()

        response = Response()

        response.data = {
            'comment_id': comment_id,
        }

        return response


class PostDetails(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        post_id = request.data['post_id']

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Error")

        userId = payload['id']

        query = "select count(*) from likes where post_id = %s;"
        cur.execute(query, (post_id,))
        likes = cur.fetchone()[0]

        query = "select count(*) from comments where post_id = %s;"
        cur.execute(query, (post_id,))
        comments = cur.fetchone()[0]

        conn.commit()

        response = Response()

        response.data = {
            'post_id': post_id,
            'number of likes': likes,
            'number of comments': comments
        }
        return response


class AllPost(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Error")

        userId = payload['id']

        query = '''
        select posts.post_id,posts.title,posts.description,posts.time,count(posts.post_id) from posts left outer join likes on posts.post_id=likes.post_id 
        where posts.user_id = %s group by posts.post_id order by posts.time;'''
        cur.execute(query, (userId,))
        postdetails = cur.fetchall()
        # print(r)

        query = "select posts.post_id,comments.comment from posts left outer join comments on posts.post_id=comments.post_id where posts.user_id = %s;"
        cur.execute(query, (userId,))
        res = cur.fetchall()

        d = dict()
        for x in res:
            if x[0] in d:
                if x[1] != None:
                    d[x[0]].append(x[1])
            else:
                if x[1] != None:
                    d[x[0]] = [x[1].strip()]
                else:
                    d[x[0]] = []

        result = []
        for postdetail in postdetails:
            result.append({
                'id': postdetail[0],
                'title': postdetail[1].strip(),
                'description': postdetail[2].strip(),
                'created_time': postdetail[3],
                'likes': postdetail[4],
                'comments': d[postdetail[0]]
            })

        print(result)

        conn.commit()

        response = Response()

        response.data = result
        return response


def insert_authenticate():
    cur.execute('''
        insert into authenticate (email,password) values ('user1@gmail.com','user1');
        ''')
    cur.execute('''
            insert into authenticate (email,password) values('user2@gmail.com','user2');
            ''')

    conn.commit()


def create_authenticate():
    cur.execute('''

            create table authenticate (
                Id serial primary key,
                email char(50) not null,
                password char(20) not null
                );

        ''')
    conn.commit()


def create_following():
    cur.execute('''
        drop table followings;
    ''')

    cur.execute('''
        create table followings (
            following int,
            follower int
        );
    ''')

    conn.commit()


def create_post():
    cur.execute('''
        create table posts (
        post_id serial primary key,
        title char(100),
        description char(300),
        time timestamp,
        user_id int
        );
    ''')

    conn.commit()


def create_likes():
    cur.execute('drop table likes');

    cur.execute('''
        create table likes (
            post_id int,
            liked_by int,
            constraint fk_post_id foreign key(post_id) references posts(post_id) on delete cascade
        );

    ''')

    conn.commit()


def create_comments():
    cur.execute("drop table comments");
    cur.execute('''
        create table comments (
            c_id serial primary key,
            comment char(100),
            post_id int,
            constraint fk_post_id foreign key(post_id) references posts(post_id) on delete cascade
        );
    ''')

    conn.commit()


def create(request):
    # create_authenticate()
    # insert_authenticate()
    # create_following()
    # create_post()
    # create_likes()
    # create_comments()

    return HttpResponse('done')






from django.urls import path

from . import views
from .views import LoginView, FollowUser,UnFollowUser,UserDetails,PostCreate,PostDelete,PostLike,PostUnLike,Comment,PostDetails,AllPost

urlpatterns = [
    path('',views.home,name='home'),
    path('create',views.create,name='create'),
    path('login', LoginView.as_view()),
    path('follow', FollowUser.as_view()),
path('unfollow', UnFollowUser.as_view()),
path('userdetails', UserDetails.as_view()),
path('postcreate', PostCreate.as_view()),
path('postdelete', PostDelete.as_view()),
path('postlike', PostLike.as_view()),
path('postunlike', PostUnLike.as_view()),
path('comment', Comment.as_view()),
path('postdetails', PostDetails.as_view()),
path('allpost', AllPost.as_view())


]