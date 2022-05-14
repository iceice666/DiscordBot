# DiscordBot

一個中文化的Discord機器人
* 現在可以播音樂

## For Developers

### You need

* [Python 3.10+](https://www.python.org/downloads/)
* [Pycord](https://github.com/Pycord-Development/pycord)

```bash
pip install pyyaml
pip install py-cord[voice] --pre
```

>If ou want to play music, this is in need.
>* [Wavelink](https://github.com/PythonistaGuild/Wavelink)
> ```bash
> pip install wavelink
> ````
>* A [Lavalink](https://github.com/freyacodes/Lavalink) server
>  * You can use [public server](https://lavalink.darrennathanael.com/) or [build your own](https://github.com/freyacodes/Lavalink#server-configuration).

### Run

```bash
python run.py
```

Or you can just use `.dockerfile` to run.

```bash
docker build --pull --rm -f ".dockerfile" -t discordmusicbot:latest "."
docker run --rm -it  discordbot:latest
```

### Extension

You can add your own functions/extensions to this bot.

> You can put your code **anywhere**, but I recommended put in `src/functions` folder.

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

To load extensions, add the filepath where you define the `setup` function to the `extension` variable in `src/bot.py`.

```python
# in src/bot.py
...
def load_extension():
  extension.append('src.functions.<your project>')

  #If you didn't define the setup up function in your project root folder ( __init__.py )
  extension.append('src.functions.<your project>.<where you define the setup function>')

...
```
