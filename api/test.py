from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import hashlib
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Thay thế bằng một secret key bất kỳ
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db' 
app.config['SQLALCHEMY_BINDS'] = {
    'teachers': 'sqlite:///teachers.db',
    'students': 'sqlite:///students.db'
}  # Sử dụng SQLite database, bạn có thể thay đổi thành database khác nếu muốn
db = SQLAlchemy(app)

def create_tables():
    with app.app_context():
        db.create_all()

class User(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def hash_password(self, password):
        # Hàm mã hóa mật khẩu sử dụng hashlib (SHA256)
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, input_password):
        # Hàm kiểm tra mật khẩu
        return self.password == self.hash_password(input_password)


    #def get_related_content(self):
        # Tìm các nội dung liên quan dựa trên các thẻ tag đã chọn
        #related_content = Content.query.filter(Content.tags.contains(self.tags)).all()
        #return related_content

class Students(User):
    __bind_key__ = 'students'
    tags = db.Column(db.String(200))
    report = db.Column(db.Text)
    def get_tags(self):
        if self.tags:
            tags_json = self.tags
            tags_list = json.loads(tags_json)  # Chuyển đổi chuỗi JSON thành list
            return tags_list
        else:
            return []

class Teachers(User):
    __bind_key__ = 'teachers'

class Courses(db.Model):
    __bind_key__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(200))
    tag = db.Column(db.String(100))
    playlist = db.Column(db.Text)

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(200), nullable=False)

def tag_list():
    try:
        with open('tags list.txt', encoding='utf-8') as tep:
            tags = list(map(str.strip, tep.readlines()))
    except FileNotFoundError:
        tags = []

    return tags
    


@app.route('/')
def home():
    return render_template("viewpage.html")


def check_admin(name, password):
    data_admin = (
    ("An", {"password": "28082005"}),
    ("VietQuang", {"password": "456789"}),
    ("Hoàng", {"password": "123456"}),
    ("Tuệ_Mẫn", {"password": "Tuệ_Mẫn"})
)
    for admin_name, admin_password in data_admin:
        if admin_name == name:
            if admin_password["password"] == password:
                return True
            else:
                return False
    return False

@app.route('/admin')
def admin_login():
    error_message=None
    if request.method == "POST":
        name_admin_request = request.form['admin_name'] 
        name_admin_request =  request.form['password']     
        if check_admin(name_admin_request, name_admin_request):
            return redirect(url_for('admin_sys'))
        else:
            return render_template('home', error_message = "Tiễn vong")
        
@app.route('/admin/sys', methods=['GET', 'POST'])
def admin_sys():
    if request.method == "POST":
        video_id = request.form.get("video_id")
        video = Courses.query.get(video_id)  # Fetch the video from the 'Courses' table
        #general_content = Content.query.get(content_id)  # Fetch the general content from the 'Content' table

        if video:
            db.session.delete(video)
            db.session.commit()
            flash("Video đã được xóa thành công!")
        elif general_content:
            db.session.delete(general_content)
            db.session.commit()
            flash("Nội dung đã được xóa thành công!")
        else:
            flash("Không tìm thấy bài viết!")
        return redirect(url_for("admin_sys"))

    # Fetching both teacher videos and general content
    teachers_videos = Courses.query.all()  # Fetch teacher videos from the 'Courses' table
    general_content = Content.query.all()  # Fetch general user content from the 'Content' table

    teachers_videos.reverse()
    general_content.reverse()

    return render_template("admin.html", teachers_videos=teachers_videos, general_content=general_content)

    

@app.route('/logout')
def logout():
    # Clear the user's session data to log them out
    session.clear()
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        # Xử lý thông tin đăng nhập
        username_or_email = request.form['username_or_email']
        password = request.form['password']
        role = request.form.get('role')

        # Kiểm tra tên đăng nhập hoặc email
        if role == "hocvien":
            user = Students.query.filter((Students.username == username_or_email) | (Students.email == username_or_email)).first()
        elif role == "giaovien":
            user = Teachers.query.filter((Teachers.username == username_or_email) | (Teachers.email == username_or_email)).first()

        if user and user.check_password(password):
            # Đăng nhập thành công, chuyển hướng đến trang cá nhân của người dùng
            if role == "hocvien":
                return redirect(url_for('student_profile', username=user.username))
            elif role == "giaovien":
                return redirect(url_for('teacher_profile', username=user.username))
        else:
            error_message = "Tên đăng nhập hoặc mật khẩu không đúng!"

    return render_template('login.html', error_message=error_message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Xử lý thông tin đăng ký
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role')

        # Kiểm tra xem tên đăng nhập hoặc email đã tồn tại trong cơ sở dữ liệu chưa
        if role == "hocvien":
            if Students.query.filter((Students.username == username) | (Students.email == email)).first():
                return "Tên đăng nhập hoặc email đã tồn tại!"
            new_student = Students(username=username, email=email, password=User().hash_password(password))
            with app.app_context():
                db.session.add(new_student)
                db.session.commit()
        elif role == "giaovien":
            if Teachers.query.filter((Teachers.username == username) | (Teachers.email == email)).first():
                return "Tên đăng nhập hoặc email đã tồn tại!"
            new_teacher = Teachers(username=username, email=email, password=User().hash_password(password))
            with app.app_context():
                db.session.add(new_teacher)
                db.session.commit()

        # Chuyển hướng đến trang chủ sau khi đăng ký thành công
        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/select_tags/<username>', methods=['GET', 'POST'])
def select_tags(username):
    tags = tag_list()
    user = Students.query.filter_by(username=username).first()

    if not user:
        return "User not found"

    if request.method == 'POST':
        tags_selected = request.form.getlist('tags')
        tags_json = json.dumps(tags_selected)  # Chuyển đổi list thành chuỗi JSON
        user.tags = tags_json
        db.session.commit()

        return redirect(url_for('student_profile', username=username))
    else:
        current_tags = user.get_tags()
        return render_template('select_tags.html', tags=tags, current_tags=current_tags, user=user)
    

@app.route('/student/<username>')
def student_profile(username):
    user = Students.query.filter_by(username=username).first()
    tags = user.get_tags()  # Gọi hàm tags() của Students để lấy danh sách tags đã chọn
    print(tags)
    if not tags:
        # Xử lý trường hợp phương thức get_tags() trả về None, có thể chuyển hướng đến trang select_tags
        return redirect(url_for('select_tags', username=username))

    return render_template('user_profile.html', username=username, tags=tags)

@app.route('/Teachers/<username>')
def teacher_profile(username):
    return "page cho giáo viên"

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
