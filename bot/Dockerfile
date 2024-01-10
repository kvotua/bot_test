FROM python:3.9-alpine
WORKDIR /code
COPY . .
RUN pip install -r ./requirements.txt
# RUN python host.py
CMD ["python", "./main.py"]