
## 1. Chạy Virtual Environment (venv)
kích hoạt môi trường ảo:

### Windows:
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

## 2.Run Server 

```bash
python manage.py runserver
```