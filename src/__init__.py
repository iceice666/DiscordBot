import yaml

config: dict

with open("src.config.ymal", mode="r") as f:
    config = yaml.load(f)
