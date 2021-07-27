![CI workflow](https://github.com/jecustoms/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
# yamdb_final
## Сервис для оценки произведений пользователями.


Проект **YaMDb** собирает отзывы (**Review**) пользователей на произведения (**Title**). Произведения делятся на категории: **«Книги», «Фильмы», «Музыка»**. Список категорий (**Category**) может быть расширен.

Читатели могут оставлять к произведениям текстовые отзывы (Review) и выставляют произведению рейтинг (оценку в диапазоне от одного до десяти). Из множества оценок автоматически высчитывается средняя оценка произведения.
Техническое описание проекта YaMDb

## Документация
Описание и структуру API после запуска можно найти по адресу  `http://127.0.0.1/redoc/`
При развертовании на боевом сервере укажите IP сервера или hostname для доступа к документации:
`http://{{server_IP}}/redoc`


## Технологии
- Python 3.8
- Django 3.0.5
- PostgreSQL 12.4
- Docker 20.10.5

## Запуск проекта для отладки
- Склонировать проект и перейти в папку проекта

```bash
git clone https://github.com/dangerousmonk/infra_sp2
cd infra_sp2
```
- Установить Python 3.8. в случае если он не установлен
- Установить и активировать виртуальное окружение, или создать новый проект в PyCharm

```bash
python3 -m venv venv
source venv\bin\activate
```

- Установить зависимости из файла **requirements.txt**
 
```bash
pip install -r requirements.txt
``` 
- В папке с файлом manage.py выполнить команды:

```bash
python manage.py makemigrations
python manage.py migrate
```
- Создать пользователя с неограниченными правами:

```bash
python manage.py createsuperuser
```
- Запустить web-сервер на локальной машине:

```bash
python manage.py runserver
```

## Docker инструкции
Проект можно развернуть используя контейнеризацию с помощью Docker  
Параметры запуска описаны в `docker-compose.yaml`.

При запуске создаются три контейнера:

 - контейнер базы данных **db**
 - контейнер приложения **web**
 - контейнер web-сервера **nginx**

Для развертывания контейнеров необходимо:


- Создать и сохранить переменные окружения в **.env** файл, образец ниже
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=yamdb
POSTGRES_USER=user
POSTGRES_PASSWORD=12345
POSTGRES_DB=yamdb #имя БД которое возьмет образ postgres
DB_HOST=db
DB_PORT=5432
```

- Запустить docker-compose

```bash
docker-compose up
```
- Выполнить миграции и подключить статику

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```
- Создать superuser

```bash
docker-compose exec web python manage.py createsuperuser
```
- Для отладки заполнить базу тестовыми данными

```bash
docker-compose exec web python manage.py loaddata fixtures.json
```
