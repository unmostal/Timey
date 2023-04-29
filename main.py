from flask import Flask, render_template, redirect, request
from data import db_session
from data.users import User
from data.tasks import Tasks
from forms.user import RegisterForm
from forms.loginform import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/blogs.db")
    app.run()


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/main')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/main', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form['data']
        add_data(data)
    database = get_data()
    return render_template('main.html', news=database)


def add_data(data):
    if data:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == 3).first()
        tasks = Tasks(title=data, content=data,
                    is_private=True)
        user.tasks.append(tasks)
        db_sess.commit()


def get_data():
    db_sess = db_session.create_session()
    user = db_sess.query(Tasks).filter(User.id == 3).all()
    return user


if __name__ == '__main__':
    main()
