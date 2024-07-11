FROM python:3.10-alpine

RUN pip install Flask

RUN pip install requests

COPY customComponentCode.py /

CMD ["python3", "-u", "customComponentCode.py"]