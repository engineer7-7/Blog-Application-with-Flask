from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date

# create an instance of flask
app = Flask(__name__)

# create ckeditor
ckeditor = CKEditor(app)

# secret key
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

# config the boostrap framework
Bootstrap5(app)


# create form to add new block post
class BlockPost(FlaskForm):
    post_title = StringField('Blog Post Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    name = StringField('Your Name', validators=[DataRequired()])
    img_url = StringField('Blog Image URL', validators=[URL()])
    blog_content = CKEditorField('Blog Content', validators=[DataRequired()])
    submit = SubmitField('SUBMIT POST')


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


# config the database with SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    posts = []
    # grab all the data from the table
    all_data = db.session.execute(db.select(BlogPost)).scalars().all()
    for post in all_data:
        posts.append(post)
    return render_template("index.html", all_posts=posts)


@app.route('/<int:post_id>')
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


@app.route('/new-post', methods=['GET', 'POST'])
def add_new_post():
    form = BlockPost()
    if form.validate_on_submit():
        new_blog_post = BlogPost(
            title=form.post_title.data,
            subtitle=form.subtitle.data,
            body=form.blog_content.data,
            img_url=form.img_url.data,
            author=form.name.data,
            date=date.today(),

        )
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=form)


@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = BlockPost()
    if form.validate_on_submit():
        new_blog_post = BlogPost(
            title=form.post_title.data,
            subtitle=form.subtitle.data,
            body=form.blog_content.data,
            img_url=form.img_url.data,
            author=form.name.data,
            date=date.today(),
        )
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))

    return render_template('make-post.html', post=requested_post, form=form, is_edit=True)


@app.route('/delete/<int:post_id>')
def delete(post_id):
    requested_id = db.get_or_404(BlogPost, post_id)
    db.session.delete(requested_id)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
