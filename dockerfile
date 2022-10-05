FROM python:latest

COPY req.txt .
RUN pip install -r req.txt
RUN rm req.txt
RUN git clone https://github.com/Bikbai/nt-bot.git
WORKDIR ./nt-bot
VOLUME "/data"