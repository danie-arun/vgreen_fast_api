FROM python:3.9.9
COPY . .
EXPOSE 8000
RUN pip install -r requirements.txt

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" ]
