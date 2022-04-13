import pathlib


al=list(pathlib.Path("./audioCache").glob("em4CBR_pvwM"))
bl=list(pathlib.Path("./audioCache").glob("em4CBR_pvw"))

if al is False:
    print("al")
if not bl :
    print("bl")

input()