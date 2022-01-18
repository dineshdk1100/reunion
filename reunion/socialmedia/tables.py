import psycopg2

conn = psycopg2.connect(database="reunion1", user="postgres", password="dinesh1100", host="localhost", port="5432")
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

    cur.execute("drop table authenticate");

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
    cur.execute("drop table posts");
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