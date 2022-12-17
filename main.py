from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.dialects.sqlite
import psycopg2
import sqlalchemy
from pytube import YouTube
from pytube.cli import on_progress
from psycopg2 import Error
from config import *

file_size = 0

class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(300))
    size = db.Column(db.Integer)

    def __repr__(self):
        return f'<Video {self.id}>'


db.create_all()

conn = psycopg2.connect(user="postgres",
                                  # пароль, который указали при установке PostgreSQL
                                  password="mysecretpassword",
                                  host="localhost",
                                  port="5432",
                                  database="videos_details")
try:
    # Подключение к существующей базе данных
    conn_string = "host='localhost' dbname='videos_details' user='90389002' password='90389Ss002'"
    # conn = psycopg2.connect(conn_string)
    # Курсор для выполнения операций с базой данных
    cursor = conn.cursor()
    # Распечатать сведения о PostgreSQL
    print("Информация о сервере PostgreSQL:")
    print(conn.get_dsn_parameters(), "\n")
    # Выполнение SQL-запроса
    cursor.execute("SELECT version();")
    # Получить результат
    record = cursor.fetchone()
    print("Вы подключены к - ", record, "\n")
    # print(db.session.query(Video.title).filter(Video.size == 12).all())
except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)
finally:
    if conn:
        cursor.close()
        conn.close()
        print("Соединение с PostgreSQL закрыто")

# ssl._create_default_https_context = ssl._create_unverified_context
# ----------------------------------------------------------------------


@app.route('/home')
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about_as')
def about():
    return render_template("about.html")


@app.route('/videos')
def posts():
    all_videos = Video.query.all()
    return render_template("videos.html", videos=all_videos)


@app.route('/video/<int:id>')
def post(id):
    video_id = Video.query.get(id)
    return render_template("description.html", video=video_id)


@app.route('/video/<int:id>/delete')
def post_delete(id):
    video_id = Video.query.get_or_404(id)
    try:
        db.session.delete(video_id)
        db.session.commit()
        return redirect('/videos')
    except:
        return 'Error'


@app.route('/video/<int:id>/rename', methods=['POST', 'GET'])
def post_update(id):
    video_id = Video.query.get(id)
    if request.method == 'POST':
        video_id.title = request.form['title']

        try:
            db.session.commit()
            return redirect('/videos')
        except:
            return 'Error'
    else:
        return render_template('rename_video.html', video=video_id)


def progress_function(stream, chunk, file_handle):
    global dBtn
    file_downloaded=(file_size)
    per = (file_downloaded/file_size)*100
    dBtn.config(text="{} % Downloaded".format(per))


@app.route('/download_video', methods=['POST', 'GET'])
def download_video():
    global file_size
    if request.method == 'POST':
        try:
            url_input = request.form['url']
            yt = YouTube(url_input)
            file_size = yt.streams.get_by_itag(22).filesize
            yt.streams.filter(progressive=True, file_extension='mp4', only_video=False).order_by('resolution').desc()
            yt = yt.streams.get_highest_resolution().download(output_path=output_path)
            yt = YouTube(url_input)
            title = yt.title
            size = yt.streams.get_by_itag(22).filesize//1000000
            video = Video(title=title, size=size)
        except:
            return 'Downloading Error'
        try:
            db.session.add(video)
            db.session.commit()
            return redirect('/videos')
        except:
            return 'Saving Error'
    else:
        return render_template('download_video.html')


if __name__ == '__main__':
    app.run(debug=True)

