# DiscordBotExtensions

[DiscordBot](https://github.com/iceice666/DiscordBot) 插件合集

## 插件

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
                  ├─ setup.py
                  └─ src
                     └─ some_code.py
```

在插件的根資料夾（Root folder）中的 `__init__.py` 裡定義一個 `setup` 函數 :

```python
  # <your project>/__init__.py
  from .src.<your module> import <something>
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

```

> 記得在`setup.py`中處裡插件的前置作業
（如前置模組）
