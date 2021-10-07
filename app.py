from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from markdown2 import Markdown
import os

converter = Markdown()

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    desc = db.Column(db.String(100))
    body = db.Column(db.Text())

    def __init__(self, title, desc, body):
        self.title = title
        self.desc = desc
        self.body = body


class PostSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'desc', 'body')


post_schema = PostSchema()
posts_schema = PostSchema(many=True)


@app.route('/')
def index():
    posts = Post.query.all()
    res = posts_schema.dump(posts)
    return render_template('index.html', articles=res)


@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        body = request.form.get('body')

        if title == '' or desc == '' or body == '':
            return render_template('new.html', error='Please fill required fields.')

        new_post = Post(title, desc, body)
        db.session.add(new_post)
        db.session.commit()

        return redirect('/')
    else:
        return render_template('new.html')


@app.route('/delete/<id>')
def delete(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()

    return redirect('/')


@app.route('/edit/<id>', methods=['POST', 'GET'])
def edit(id):
    if request.method == 'POST':
        post = Post.query.get(id)

        title = request.form.get('title')
        desc = request.form.get('desc')
        body = request.form.get('body')

        post.title = title
        post.desc = desc
        post.body = body

        db.session.commit()

        return redirect('/')
    else:
        post = Post.query.get(id)
        post_data = post_schema.dump(post)

        return render_template('edit.html', values=post)


@app.route('/posts/<id>')
def post(id):
    posts = Post.query.get(id)
    post = post_schema.dump(posts)

    return render_template('post.html', post_title=post['title'], post_body=converter.convert(post['body']), post_desc=post['desc'])


@app.route('/test')
def test():
    print(post_schema.dump(Post.query.get(1)))
    return ''


if __name__ == '__main__':
    app.run(debug=True)
