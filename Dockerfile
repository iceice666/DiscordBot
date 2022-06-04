FROM python:3.10

LABEL NAME="DiscordBot" DESCRIPTION="A high-mobility Discord bot."
LABEL author="KSHSlime#9034" Github="https://github.com/iceice666/DiscordBot"

WORKDIR /user/src/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python3","run.py"]