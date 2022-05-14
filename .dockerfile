FROM python:3.10

LABEL NAME="DiscordBot" DESCRIPTION="A high mobility Discord bot."
LABEL author="KSHSlime#9034" Github="https://github.com/iceice666/DiscordBot"

WORKDIR /user/src/app


RUN pip install py-cord['voice'] --pre
RUN pip install wavelink
RUN pip install Pyyaml

COPY . .

CMD ["python3","run.py","--docker"]