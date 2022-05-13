import argparse

from src.Bot import run, docker_run


parser = argparse.ArgumentParser()
parser.add_argument(
    "-d", "--docker", help="It will not be able to log the log file and\
         set the console logging level to logging.DEBUG.",
    action="store_true")
args = parser.parse_args()

if args.docker:
    docker_run()
else:
    run()
