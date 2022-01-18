from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .tables import *
import psycopg2
import jwt,datetime
import os


DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()


def home(request):
    return HttpResponse("Home")



class Authenticate(APIView):
    def post(self,request):

        try:
            email = request.data['email']
            password = request.data['password']
        except:
            return HttpResponse("check parameters")

        query = "select id from authenticate where email = %s and password = %s;"
        cur.execute(query,(email,password,))

        Id = cur.fetchone()
        print(Id)

        if Id==None:
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
    def post(self,request):
        try:
            token = request.COOKIES.get('jwt')
            followingUserId = request.data['userid']
        except:
            return HttpResponse('check parameters')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Expired - Login again")

        userId= payload['id']

        query = "select * from followings where following = %s and follower =%s;"
        cur.execute(query, (userId,followingUserId,))
        res = cur.fetchone()

        if res != None:
            return HttpResponse("You already following this user")

        query = "insert into followings (following,follower) values (%s, %s);"
        cur.execute(query,(userId,followingUserId,))

        conn.commit()


        return HttpResponse('followed')

class UnFollowUser(APIView):
    def post(self,request):

        try:
            token = request.COOKIES.get('jwt')
            followingUserId = request.data['userid']
        except:
            return HttpResponse('check parameters')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Expired - Login again")

        userId= payload['id']

        query = "delete from followings where following = %s and follower = %s;"
        cur.execute(query,(userId,followingUserId,))

        conn.commit()


        return HttpResponse('unfollowed')


class UserDetails(APIView):
    def get(self,request):
        token = request.COOKIES.get('jwt')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Expired - Login again")

        userId= payload['id']

        query = "select email from authenticate where id = %s;"
        cur.execute(query,(userId,))
        email = cur.fetchone()[0]

        query = "select count(following) from followings where following = %s;"
        cur.execute(query, (userId,))
        followings = cur.fetchone()[0]

        query = "select count(follower) from followings where follower = %s;"
        cur.execute(query, (userId,))
        followers = cur.fetchone()[0]

        conn.commit()
        print(email,followings,followers)

        response = Response()


        response.data = {
            'user name': email,
            'number of followers': followers,
            'number of following': followings
        }
        return response


class Posts(APIView):
    def post(self,request):

        try:
            token = request.COOKIES.get('jwt')

            title = request.data['title']
            desc = request.data['desc']
        except:
            return HttpResponse('check parameters')

        currenttime = datetime.datetime.utcnow()

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Expired - Login again")

        userId= payload['id']

        query = "insert into posts (title,description,time,user_id) values ( %s,%s,%s,%s) returning post_id;"
        cur.execute(query,(title,desc,currenttime,userId,))
        post_id = cur.fetchone()[0]
        # print(post_id)
        conn.commit()


        response = Response()

        response.data ={
            'post_id' : post_id,
            'title' : title,
            'desc':desc,
            'createdtime': currenttime
        }

        return response

    def delete(self,request):

        try:
            token = request.COOKIES.get('jwt')

            post_id = request.data['post_id']
        except:
            return HttpResponse('check parameters')


        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Expired - Login again")

        userId= payload['id']

        query = "delete from posts where post_id = %s and user_id = %s"
        cur.execute(query,(post_id,userId))
        conn.commit()


        response = Response()

        response.data ={
            'post_id' : post_id
        }

        return response

    def get(self,request):

        try:
            token = request.COOKIES.get('jwt')

            post_id = request.data['post_id']
        except:
            return HttpResponse('check parameters')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Expired - Login again")

        userId= payload['id']



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





class PostLike(APIView):
    def post(self,request):

        try:
            token = request.COOKIES.get('jwt')

            post_id = request.data['post_id']

        except:
            return HttpResponse('check parameters')


        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Expired - Login again")

        userId= payload['id']

        query = "select * from likes where post_id = %s and liked_by =%s;"
        cur.execute(query, (post_id, userId))
        res = cur.fetchone()

        if res !=None:
            return HttpResponse("You already Liked")

        query = "insert into likes(post_id,liked_by) values (%s,%s);"
        cur.execute(query,(post_id,userId))
        conn.commit()


        return HttpResponse("Liked")


class PostUnLike(APIView):
    def post(self,request):

        try:
            token = request.COOKIES.get('jwt')

            post_id = request.data['post_id']

        except:
            return HttpResponse('check parameters')


        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Expired - Login again")

        userId= payload['id']

        query = "delete from likes where post_id = %s and liked_by= %s;"
        cur.execute(query,(post_id,userId))
        conn.commit()


        return HttpResponse("Unliked")


class Comment(APIView):
    def post(self,request):

        try:
            token = request.COOKIES.get('jwt')

            comment = request.data['comment']
            post_id = request.data['post_id']

        except:
            return HttpResponse('check parameters')


        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Expired - Login again")

        userId= payload['id']

        query = "insert into comments (comment,post_id) values ( %s,%s) returning c_id;"
        cur.execute(query,(comment,post_id))
        comment_id = cur.fetchone()[0]
        # print(post_id)
        conn.commit()


        response = Response()

        response.data ={
            'comment_id' : comment_id,
        }

        return response


class AllPost(APIView):
    def get(self,request):
        token = request.COOKIES.get('jwt')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Expired - Login again")

        userId= payload['id']



        query = '''
        select posts.post_id,posts.title,posts.description,posts.time,count(posts.post_id),comments.comment from 
        posts left outer join comments on posts.post_id=comments.post_id  left outer join likes on posts.post_id=likes.post_id
        where posts.user_id = %s group by posts.post_id,comments.comment order by posts.time desc;'''
        cur.execute(query, (userId,))
        postdetails = cur.fetchall()

        d=dict()
        for x in postdetails:
            if x[0] in d:
                if x[5] != None:
                    d[x[0]][5].append(x[5].strip())
            else:
                if x[5]!=None:
                    d[x[0]]=[x[0],x[1].strip(),x[2].strip(),x[3],x[4],[x[5].strip()]]
                else:
                    d[x[0]]=[x[0],x[1].strip(),x[2].strip(),x[3],x[4],[]]

        print(d)



        result=[]
        for post in d:
            result.append({
                'post_id':d[post][0],
                'title':d[post][1],
                'description':d[post][2],
                'created_time':d[post][3],
                'likes':d[post][4],
                'comments':d[post][5]
            })

        conn.commit()

        response = Response()


        response.data = result
        return response







def create(request):

    create_authenticate()
    insert_authenticate()
    create_following()
    create_post()
    create_likes()
    create_comments()

    return HttpResponse('Tables created')