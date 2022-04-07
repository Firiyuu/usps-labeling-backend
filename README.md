## United World Logisctics Backend API
version 1.0

### Running  locally
- Requires python3.6

* copy `uw-logistics/.env.example` to `uw-logistics/.env` and update settings
* python makemigrations
* python migrate
* python manage.py runserver 0.0.0.0:8000


### Using docker
* run:
```console
  docker-compose build
  docker-compose up
  docker-compose exec web_api python manage.py migrate
```