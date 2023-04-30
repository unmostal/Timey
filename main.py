from flask import Flask, render_template, redirect, request, abort
from data import db_session
from data.tasks import Tasks
from forms.tasks import TasksForm
from forms.user import RegisterForm
from forms.loginform import LoginForm
from flask_login import LoginManager
from data.users import User
from flask_login import login_user, logout_user, login_required, current_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)



def main():
    db_session.global_init("db/blogs.db")
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        tasks = db_sess.query(Tasks).filter(
            (Tasks.user == current_user) | (Tasks.is_private != True))
    else:
        tasks = db_sess.query(Tasks).filter(Tasks.is_private != True)
    return render_template("index.html", news=tasks)

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
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/tasks',  methods=['GET', 'POST'])
@login_required
def add_tasks():
    form = TasksForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        tasks = Tasks()
        tasks.title = form.title.data
        tasks.content = form.content.data
        tasks.is_private = form.is_private.data
        current_user.tasks.append(tasks)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('tasks.html', title='Добавление новости',
                           form=form)

@app.route('/tasks/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_tasks(id):
    form = TasksForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        tasks = db_sess.query(Tasks).filter(Tasks.id == id,
                                            Tasks.user == current_user
                                            ).first()
        if tasks:
            form.title.data = tasks.title
            form.content.data = tasks.content
            form.is_private.data = tasks.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        tasks = db_sess.query(Tasks).filter(Tasks.id == id,
                                            Tasks.user == current_user
                                            ).first()
        if tasks:
            tasks.title = form.title.data
            tasks.content = form.content.data
            tasks.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('tasks.html',
                           title='Редактирование задачи',
                           form=form
                           )

@app.route('/tasks_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def tasks_delete(id):
    db_sess = db_session.create_session()
    tasks = db_sess.query(Tasks).filter(Tasks.id == id,
                                       Tasks.user == current_user
                                       ).first()
    if tasks:
        db_sess.delete(tasks)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')

if __name__ == '__main__':
    main()