# DiscordBot

一個中文化的Discord機器人

* 現在可以播音樂

## For Developers

### You need

* [Python 3.10+](https://www.python.org/downloads/) (Only Python 3.10 support match-case syntax!)
* [Pycord](https://github.com/Pycord-Development/pycord)
* [Wavelink](https://github.com/PythonistaGuild/Wavelink)
  * A [Lavalink](https://github.com/freyacodes/Lavalink) server
  * You can use [public server](https://lavalink.darrennathanael.com/) or [build your own](https://github.com/freyacodes/Lavalink#server-configuration).

```bash
pip install pyyaml
pip install py-cord[voice] --pre
pip install wavelink
```

>Or just install all requriement.
>
>```bash
> pip install -r requirements.txt
>```

### Run

```bash
python run.py
```

Or you can just use `.dockerfile` to run.

```bash
docker build --pull --rm -f ".dockerfile" -t discordbot:latest "."
docker run --rm -it  discordbot:latest
```

### Extension

You can add your own functions/extensions to this bot.

Put your code in `src/functions` folder.

```txt
discordbot/
    └─ src
        └─ functions
             ├─ __init__.py
             ├─ general.py
             ├─ music   #this is my project
             │ ├─ __init__.py
             │ └─ music.py
             └─ <your project> #your project. It's an example.
                ├─ __init__.py
                └─ some_code.py
```

Defines a `setup` function in your project root folder ( \_\_init\_\_.py ) like this:

```python
 # <your project>/__init__.py
 from .<your project> import <some something>
 import logging

 def setup(bot): # 'bot' argument is required.
   # load some stuff brabrabra
   do_somthing()
```

To load extensions, add the filepath where you define the `setup` function to  `activate` file.

```txt
# in activate file
...

src.functions.<your project>

#If you didn't define the setup up function in your project root folder ( __init__.py )
src.functions.<your project>.<where you define the setup function>

...
```
