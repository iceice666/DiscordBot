

from src.config import lang

exec(f"from src.i18n.{lang} import translation,console")

TRANSLATION = translation
CONSOLE = console
