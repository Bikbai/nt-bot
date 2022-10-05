FROM python:latest

COPY req.txt .
RUN pip install -r req.txt
RUN git clone https://github.com/Bikbai/nt-bot.git
VOLUME "/data"
RUN ls