import yaml
import os


# ~ config loader
config: dict
with open(f"{os.getcwd()}/config.yaml", mode="r") as f:
    config = yaml.load(f,yaml.Loader)
