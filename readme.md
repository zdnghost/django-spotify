
## 1. Chạy Virtual Environment (venv)
kích hoạt môi trường ảo:

### Windows:
```bash
venv\Scripts\activate
```

## 2.Tạo env
copy file ```.env.example``` thành ```.env```

## 3.Tạo venv
python -m venv venv

## 4.Truy cập venv
.\venv\Scripts\Activate.ps1

## 5.Install các package trong file Requirement.txt
pip install -r requirements.txt

## 6.Run Server

```bash
python manage.py runserver
```

## Lưu ý nếu không có quyền admin thì chạy 
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass