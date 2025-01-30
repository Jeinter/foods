<h1 align="center">Foodgram</h1>

<h3 align="center">Cоциальная сеть для публикации своих рецептов. Состоит из бэкенд-приложения на Django и фронтенд-приложения на React. Поддерживает регистрацию и авторизацию, можно добавить новый рецепт на сайт или изменить существующий, а также просмотреть рецпты других пользователей.</h3>

---

### Используемые технологии:
- Python 3.10 
- Django
- Django REST Framework
- Node.js
- React
- Gunicorn
- Nginx
- Docker
- GitHub Actions

# API 

| Name           | URL                                    | Допустимые методы                            |
|----------------|----------------------------------------|----------------------------------------------|
| Users          | ```/api/users/```                      | ```GET```, ```POST```                        |
| SetPassword    | ```/api/users/set_password```          |            ```POST```                        |
| Login          | ```/api/auth/token/login/```           |            ```POST```                        |
| Logout         | ```/api/auth/token/logout/```          |            ```POST```                        |
| Follow         | ```/api/recipes/subscriptions/```      | ```DELET```,                                 |
| Follow         | ```/api/recipes/{id}/subscribe/```     | ```DELET```, ```POST```                      |
| UsersDetail    | ```/api/users/{id}/```                 |```GET```                                     |
| Recipes        | ```/api/recipes/```                    | ```GET```, ```POST```                        |
| RecipesDetail  | ```/api/recipes/{id}/```               | ```GET```, ```PATCH```,  ```DELETE```        |
| FavoriteRecipe | ```/api/recipes/{id}/favorite/```      | ```DELET```, ```POST```                      |
| ShoppingCart   | ```/api/recipes/{id}/shopping_cart/``` | ```DELET```, ```POST```,  ```GET```          |
| Tags           | ```/api/tags/```                       | ```GET```, ```POST```                        |
| Ingredients    | ```/api/ingredients/```                | ```GET```, ```POST```                        |

---

### Как развернуть проект локально
1. Клонировать репозиторий:
    ```bash
    git clone git@github.com:jeinter/foodgram-project-react.git
    cd foodgram-project-react/
    ```

2. Создать в папке foodgram/infra файл `.env` с переменными окружения.

3. Собрать и запустить докер-контейнеры через Docker Compose:
    ```bash
    docker compose up --build
    ```

### Как развернуть проект на сервере
1. Создать папку foodgram/ с файлом `.env` в домашней директории сервера.
    ```bash
    cd ~
    mkdir foodgram
    nano foodgram/.env
    ```
2. Настроить в nginx перенаправление запросов на порт 8800:
    ```nginx
    server {
        server_name <...>;
        server_tokens off;

        location / {
            proxy_pass http://127.0.0.1:8800;
        }
    }
    ```
3. Добавить в GitHub Actions следующие секреты:
- DOCKER_USERNAME - логин от Docker Hub
- DOCKER_PASSWORD - пароль от Docker Hub
- SSH_KEY - закрытый ssh-ключ для подключения к серверу
- SSH_PASSPHRASE - passphrase от этого ключа
- USER - имя пользователя на сервере
- HOST - IP-адрес сервера
- TELEGRAM_TO - ID телеграм-аккаунта для оповещения об успешном деплое
- TELEGRAM_TOKEN - токен телеграм-бота
- DOMEN_NAME - доменное имя вашего сайта

