# DiscordBot

就只是一個中文DiscordBot

* 現在可以播音樂

## For Developers

### 你需要

* [Python 3.10+](https://www.python.org/downloads/) (只有 Python 3.10 支持 match-case 語法!)
* [Pycord](https://github.com/Pycord-Development/pycord)
* [Wavelink](https://github.com/PythonistaGuild/Wavelink)
  * 一個 [Lavalink](https://github.com/freyacodes/Lavalink) 伺服器
  * 你可以 [使用現成的](https://lavalink.darrennathanael.com/) 或 [自己搭一個](https://github.com/freyacodes/Lavalink#server-configuration).

```bash
 pip install -r requirements.txt
```

### 運行

```bash
python run.py
```

或直接使用 `.dockerfile` 來運行.

```bash
docker build --pull --rm -f ".dockerfile" -t discordbot:latest "."
docker run --rm -it  discordbot:latest
```

### 插件
[link](https://github.com/iceice666/DiscordBotExtensions)
