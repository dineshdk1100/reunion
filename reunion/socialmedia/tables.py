import psycopg2
import os


DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

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

            create table if not exists authenticate (
                Id serial primary key,
                email char(50) not null,
                password char(20) not null
                );

        ''')
    conn.commit()


def create_following():


    cur.execute('''
        create table if not exists followings (
            following int,
            follower int
        );
    ''')

    conn.commit()


def create_post():

    cur.execute('''
        create table if not posts (
        post_id serial primary key,
        title char(100),
        description char(300),
        time timestamp,
        user_id int
        );
    ''')

    conn.commit()


def create_likes():


    cur.execute('''
        create table if not exists likes (
            post_id int,
            liked_by int,
            constraint fk_post_id foreign key(post_id) references posts(post_id) on delete cascade
        );

    ''')

    conn.commit()


def create_comments():

    cur.execute('''
        create table if not exists comments (
            c_id serial primary key,
            comment char(100),
            post_id int,
            constraint fk_post_id foreign key(post_id) references posts(post_id) on delete cascade
        );
    ''')

    conn.commit()