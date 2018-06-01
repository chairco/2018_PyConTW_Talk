# 2018_PyConTW_Talk

## 環境設定

建議採用 [Pipenv](https://github.com/kennethreitz/pipenv) 做套件管理，Pipenv 是一個出色的 Python 工具管理套件，類似其他程式語言裡常見的：bundler, composer, npm, cargo, yarn, 等

如果對它還不熟悉，這裡有一篇簡單的 [Pipenv 使用教學](https://chairco.github.io/posts/2017/02/Pipenv%20tutorial.html)。

### pipenv

建立環境:
```
pipenv --python 3.6.3
```

安裝必要套件:
```
pipenv install --dev
```

進入虛擬環境:
```
pipenv shell
```


### py3 內建虛擬環境

```
python3 -m venv env
```

進入虛擬環境:
```
source env/bin/activate 
```

安裝必要套件:
```
pip install -r requirements.txt
```


## Django 環境設定

使用 python-dotenv 管理環境變數，首先需要在 settings/ 目錄下先建立 `local.env` 檔案。

```
cp 2018_PyConTW_Talk/pycontw2018/pycontw2018/settings/local_sample.env 2018_PyConTW_Talk/pycontw2018/pycontw2018/settings/local.env 
```

接著設定環境需要參數:

+ `DATABASE_URL='postgres://localhost/pycontw2018'` 預設採用 postgresql 資料庫，可根據需求修改(sqlite3 目前測試會有問題)。
+ `SECRET_KEY={}` Django 需要的 secret key。可到[這邊](https://www.miniwebtool.com/django-secret-key-generator/)取得


建立資料庫:

注意，目前資料庫預設 `Postgresql` 請先在本機端預設安裝，並且建立對應的 table。安裝完成後再執行 migrate 指令。

```
python manage.py migrate
```

建立 admin 帳號(請注意一定要輸入信箱，因為信件會發送到此):
```
python manage.py createsuperuser
```

啟動伺服器：
```
python manage.py runserver
```

如果可以順利連到 [localhost:8000/chats](http://localhost:8000/chats) 恭喜已經完成 Django Channels 聊天室。
