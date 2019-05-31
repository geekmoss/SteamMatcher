FROM python:3

ADD . /SteamMatcher

RUN pip install -r /SteamMatcher/requirements.txt
WORKDIR "/SteamMatcher"

CMD ["python", "./bot.py"]