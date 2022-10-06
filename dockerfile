FROM python:latest

COPY req.txt .
RUN pip install -r req.txt &&\
    rm req.txt
RUN git clone https://github.com/Bikbai/nt-bot.git
VOLUME "/data"