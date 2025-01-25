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

First you need to create `.env` file in project root directory. You can find an example in the `.env.local` file

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

Verify the API works properly at `localhost:8000`, and there are no errors in the console. Swagger is hosted under `localhost:8000/docs`
