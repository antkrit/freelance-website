### Setup

- Create virtual environment:
```bash
python3.11 -m venv venv
```

- Activate virtual environment:
```bash
source venv/bin/activate
```

- Install dependencies: 
```bash
pip install poetry
poetry install
```

### Local Run

First you need to create `.env` file in project root directory. You can find an example in the `.env.local` file. Make sure that database specified in the .env file exists.

#### Use uvicorn

```bash
uvicorn main:app --reload
```

#### Use Docker

- Build Docker images
```bash
docker build --tag freelance_website .
```

- Run Docker image
```bash
docker run --publish 8000:8000 --env-file .env freelance_website:latest
```


### Testing

The easiest way to test is by using docker compose:
```bash
docker compose up
```

To test API use Swagger UI that is hosted on `localhost:8000/docs`. It is protected with basic authorization, credentials are specified in the `.env` file (default username/password: admin/root).

To test protected endpoints you need to be authorized. On application startup admin user is created if not exists (username: `admin`, password: `root`). Also, you can register your own user (may not have enough permissions for some endpoints). To authorize in Swagger UI use big green "Authorize" button in right upper corner.