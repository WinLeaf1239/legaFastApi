# python -m uvicorn very_first:app --reload

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse , RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import csv
import hashlib
import templates
import os
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

white_urls = ["/", "/login", "/logout", "/register", "/403"]

users = [{'username' : 'admin' , 'password' : '1234'}]


@app.middleware("http")
async def check_session_middleware(request: Request, call_next):
    path = request.url.path
    
    # Пропускаем открытые страницы и статические файлы
    if path in white_urls or path.startswith("/static"):
        return await call_next(request)
    
    # Если прошло 10 секунд, SessionMiddleware очистит сессию, и сработает редирект на /403
    if not request.session.get("username"):
        return RedirectResponse(url="/403", status_code=303)
        
    return await call_next(request)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "legenda67prosuper"),
    max_age = 60 # Сессия будет жить 90(в секундах)
)

app.add_middleware(HTTPSRedirectMiddleware)

# Маршрутизация приложения
@app.get("/", response_class=HTMLResponse) # перехват адреса http://localhost:8000/
def main_page(request: Request):
    return templates.TemplateResponse(request=request, name ="based_main.html")

@app.get("/home", response_class=HTMLResponse)
def home_page(request: Request):
    username = request.session.get("username")
    password_hash = request.session.get("password_hash")

    #Защита страницы: если в сессии нет имени пользователя, отправляем на вход
    if not username:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"username": username, "password_hash": password_hash})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/register", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@app.get("/404", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="404.html")


@app.get("/403", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="403.html")



@app.post("/login")
def login(request: Request, 
          username: str = Form(...), 
          password: str = Form(...)
        ):
    print(request)
    print(username)
    print(password)

    hash_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    
    with open(file='users.csv' , mode = 'r' , newline='', encoding='utf-8') as file:
        read = csv.DictReader(file)
        print(hash_password)
        for row in read:
            if row['username'] == username and row['password_hash'] == hash_password:
                print('Есть попадание')
                request.session['username'] = username  
                request.session['password_hash'] = hash_password
                return RedirectResponse(url="/home", status_code=303)
            
    print('Нету попадания') 
    return templates.TemplateResponse(request=request, name='login.html', context={'error': 'Неверное имя пользователя или пароль'})


@app.post("/register")
def log(request: Request,
        username : str = Form(...),
        password : str = Form(...),
        admin_login : str = Form(...),
        admin_password: str = Form(...),
        avatar: UploadFile = File(None)
        ): 
    print(request)
    print(username)
    print(password)
    print(admin_login)
    print(admin_password)
    print(avatar)

    if admin_login != "admin" or admin_password != "1234":
        return templates.TemplateResponse(request=request, name = "register.html", context={"error" : "Неверный админ логин и админ пароль"})

    with open(file="users.csv" , mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username:
                return templates.TemplateResponse(
                    request=request,
                    name="register.html",
                    context={"error": "Пользователь с таким именем уже существует"}
                )

    hash_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

    with open(file="users.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Передаем пустую строку '' для колонки avatar_path, чтобы сохранить структуру CSV
        writer.writerow([username, hash_password, ""])

    request.session["username"] = username
    request.session["password_hash"] = hash_password

    return RedirectResponse(url="/home", status_code=303)


@app.get("/logout")
def logout(request: Request):
    # 6. Очищаем сессию при выходе из аккаунта
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/whoami")
def whoami(request: Request):
    # Возвращаем весь словарь сессии как есть
    return {
        "session_data": dict(request.session),
        "is_authenticated": "username" in request.session
    }


