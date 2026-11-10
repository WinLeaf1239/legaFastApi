# python -m uvicorn very_first:app --reload

from fastapi import FastAPI, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse , RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import csv
import hashlib
import templates
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.add_middleware(SessionMiddleware, secret_key='legenda67prosuper')

white_urls = ["/", "/login", "/logout", "/register"]

users = [{'username' : 'admin' , 'password' : '1234'}]

app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("SECRET_KEY", "super-secret-key-123"),
    max_age=3600 * 24  # Сессия будет жить 24 часа
)

# Маршрутизация приложения
@app.get("/", response_class=HTMLResponse) # перехват адреса http://localhost:8000/
def main_page(request: Request):
    return templates.TemplateResponse(request=request, name ="based_main.html")

@app.get("/home", response_class=HTMLResponse)
def home_page(request: Request):
    username = request.session.get('username')
    password_hash = request.session.get('password_hash')
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request,
                                       name="home.html" ,
                                       context={'username'  : username,
                                                'password_hash': password_hash})
    

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/register", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@app.get("/404", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="404.html")


USERS_DB = {
    "alex_dev": {"id": 101, "password_hash": "hashed_pass_1"},
    "marina": {"id": 102, "password_hash": "hashed_pass_2"}
}



@app.post("/login")
def login(request: Request, 
          username: str = Form(...), 
          password: str = Form(...)
        ):
    print(request)
    print(username)
    print(password)
    with open(file='users.csv' , mode = 'r' , newline='', encoding='utf-8') as file:
        read = csv.DictReader(file)
        hash_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
        print(hash_password)
        for row in read:
            if row['username'] == username and row['password_hash'] == hash_password:
                print('Есть попадание')
                request.session['username'] = username
                request.session['password_hash'] = hash_password
                return RedirectResponse(url="/home", status_code=303)
            else:
                print('Нету попадания')
                return templates.TemplateResponse(request=request, name='login.html', context={'error': 'Неверное имя пользователя или пароль'})


@app.post("/register")
def log(request: Request,
        username : str = Form(...),
        password : str = Form(...),
        admin_login : str = Form(...),
        admin_password: str = Form(...)
        ): 
    print(request)
    print(username)
    print(password)
    print(admin_login)
    print(admin_password)
    with open(file='users.csv' , mode = 'r' , newline='', encoding='utf-8') as file:
        read = csv.DictReader(file)
        hash_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
        print(hash_password)
        for row in read:
            if row['username'] == username and row['password_hash'] == hash_password and admin_login == 'admin' and admin_password == '1234':
                print('Есть попадание')
                return RedirectResponse(url="/home", status_code=303)
            else:
                print('Нету попадания')
                return templates.TemplateResponse(request=request, name='register.html', context={'error': 'Неверное имя пользователя или пароль или имя админа или пароль админа'})








@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    # Как сервер узнает конкретного юзера при следующем запросе?
    # Браузер сам пришлет куку. Middleware расшифрует ее и положит данные в request.session
    user_id = request.session.get("user_id")
    username = request.session.get("username")
    
    # Если в сессии нет user_id, значит пользователь не авторизован (или сессия истекла)
    if not user_id:
        return "<h1>Доступ запрещен. Пожалуйста, <a href='/login'>войдите</a>.</h1>"
        
    # Если user_id есть — мы успешно идентифицировали конкретного пользователя!
    return f"<h1>Добро пожаловать в личный кабинет, {username}! Ваш ID: {user_id}</h1>"


@app.post("/logout")
async def logout(request: Request):
    # Удаление сессии (отвязка от юзера)
    # Метод .clear() полностью очищает данные. При ответе клиенту отправится пустая кука.
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
