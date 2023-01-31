![FOODGRAM STATUS](https://github.com/Oleg-zag/foodgram-project-react/actions/workflows/yamdb_workflow.yml/badge.svg)
## Описание
### Возможности проекта
При помощи представленного сервиса пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

<img width="479" alt="foodgram" src="https://user-images.githubusercontent.com/102435345/215749177-14eccfa8-3f34-44e4-a944-5ae34296410b.png">

### Расширение функциональности
Функционал проекта адаптирован для использования PostgreSQL и развертывания в контейнерах Docker. Используются инструменты CI и CD.
### Ссылка на сайт
Проект был запущен и доступен по [адресу](http://62.84.120.138/).

Может быть недоступно в связи с прекращением обслуживания.
## Технологии
 - Python 3.7
 - Django 2.2.16
 - REST Framework 3.12.4
 - PyJWT 2.1.0
 - Django filter 21.1
 - Gunicorn 20.0.4
 - PostgreSQL 12.2
 - Docker 20.10.2
 - подробнее см. прилагаемый файл зависимостей requrements.txt
## Установка
### Шаблон описания файла .env
 - DB_ENGINE=django.db.backends.postgresql
 - DB_NAME=<имя базы данных postgres> 
 - POSTGRES_USER=<пользователь бд>
 - POSTGRES_PASSWORD=<пароль>
 - DB_HOST=<db>
 - DB_PORT=<5432>
 - SECRET_KEY=<секретный ключ проекта django>
### Инструкции для развертывания и запуска приложения
для Linux-систем все команды необходимо выполнять от имени администратора
- Склонировать репозиторий
```bash
git clone https://github.com/Oleg-zag/fodgram-project-react.git
```
- Выполнить вход на удаленный сервер
- Установить docker на сервер:
        Чтобы установить Docker на Ubuntu, выполните подготовительные действия. Для начала, обновите состав установочных пакетов, чтобы иметь представление об их актуальных версиях:
    ```sh
    sudo apt update
    ```
    Предварительно установите набор пакетов, необходимый для доступа к репозиториям по протоколу HTTPS:
**apt-transport-https** — активирует передачу файлов и данных через https;
**ca-сertificates** — активирует проверку сертификаты безопасности;
**curl** — утилита для обращения к веб-ресурсам;
**software-properties-common** — активирует возможность использования скриптов для управления программным обеспечением.
    ```sh
    sudo apt install apt-transport-https ca-certificates curl software-properties-common
    ```
    Далее добавьте в систему GPG-ключ для работы с официальным репозиторием Docker:
    ```sh
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    ```
    Добавьте репозиторий Docker в локальный список репозиториев:
    ```sh
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    ```
    Повторно обновите данные о пакетах операционной системы:
    ```sh
    sudo apt update
    ```

    ```bash
    sudo apt install docker-ce -y
    ```
    установите пакет Docker
    ```sh
    sudo apt install docker-ce -y
    ```
    После завершения установки запустите демон Docker и добавьте его в автозагрузку:
    ```sh
    sudo systemctl start docker
    ```
    ```sh
   sudo systemctl enable docker
    ```
- Установить docker-compose на сервер:
```sh
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```
- Локально отредактировать файл infra/nginx.conf, обязательно в строке server_name вписать IP-адрес сервера
- Скопировать файлы docker-compose.yml и default.conf из директории infra на сервер:
```sh
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/default.conf
```
- Для работы с Workflow добавить в Secrets GitHub переменные окружения для работы:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    
    DOCKER_PASSWORD=<пароль от DockerHub>
    DOCKER_USERNAME=<имя пользователя>
    
    SECRET_KEY=<секретный ключ проекта django>

    USER=<username для подключения к серверу>
    HOST=<IP сервера>
    PASSPHRASE=<пароль для сервера, если он установлен>
    SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

    TELEGRAM_TO=<ID чата, в который придет сообщение>
    TELEGRAM_TOKEN=<токен вашего бота>
    ```
    Workflow состоит из четырёх шагов:
     - Проверка кода на соответствие PEP8
     - Сборка и публикация образа бекенда на DockerHub.
     - Автоматический деплой на удаленный сервер.
     - Отправка уведомления в телеграм-чат.
- собрать и запустить контейнеры на сервере:
```bash
docker-compose up -d --build
```
- После успешной сборки выполнить следующие действия (только при первом деплое):
    * провести миграции внутри контейнеров:
    ```bash
    docker-compose exec foodgram_backend python manage.py migrate
    ```
    * собрать статику проекта:
    ```
    docker-compose exec foodgram_backend python manage.py collectstatic --no-input
    ```
    * Создать суперпользователя Django, после запроса от терминала ввести логин и пароль для суперпользователя:
    ```bash
    docker-compose exec foodgram_backend python manage.py createsuperuser
    ```
    * Загрузить в БД предопределенные ингредиенты из .csv файла:
    ```bash
    docker-compose exec foodgram_backend python manage.py load_ingredients
    ```
### Команды для заполнения базы данными
- Заполнить базу данными
- Создать резервную копию данных:
```bash
docker-compose exec web python manage.py dumpdata > fixtures.json
```
- Остановить и удалить неиспользуемые элементы инфраструктуры Docker:
```bash
docker-compose down -v --remove-orphans
```
