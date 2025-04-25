
## 1. Chạy Virtual Environment (venv)
tạo môi trường ảo:

```bash
python -m venv venv 
```

chạy môi trường ảo
```bash
venv\Scripts\activate
```

## 2.Tạo env
copy file ```.env.example``` thành ```.env```

### Windows:
```bash
copy .env.example .env
```
### Linux / macOS / Git Bash / WSL:
```bash
cp .env.example .env
```
rồi config lại file env


## 3.Install các package trong file Requirement.txt
```bash
pip install -r requirements.txt
```
## 4.Run Server

```bash
python manage.py runserver
```

## Lưu ý nếu không có quyền admin thì chạy 
```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```