FROM python:3.9

WORKDIR /usr/src

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./main.py .

ENTRYPOINT [ "python3", "-m", "uvicorn", "main:app"]
CMD ["--log-level=info", "--host", "0.0.0.0", "--port", "80"]
