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

你可以在bot裡添加自己的插件

將你的插件代碼放在  `src/extensions` 資料夾裡

```txt
discordbot/
    └─ src
        └─ extensions
             ├─ __init__.py
             ├─ general.py
             └─ <your project> #your project. It's an example.
                ├─ __init__.py
                └─ some_code.py
```

在插件的根資料夾（Root folder）中的 `\_\_init\_\_.py` 裡定義一個 `setup` 函數 :

```python
  # <your project>/__init__.py
  from .<your project> import <some something>
  # 參數 'bot' 是必要的，因為bot在載入時會傳入一個 discord.Bot 物件來載入如 'commands.Cog' 等特定功能.
  def setup(bot):
    # load some stuff brabrabra
    do_somthing()

```

要真正的載入插件，你需要在`config.yml`中的`Modules`項裡添加**從`src`資料夾開始到定義`setup`函數的檔案**的路徑

```yml
# in config.yml file
...
Modules:
  - "src.extensions.<where you define the setup function in your project>"
  #Just like
  - "src.extensions.<your project>"

...
```
