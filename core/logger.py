import logging
import sys
from pytz import timezone
from datetime import datetime

sys.stderr = open("log/errors.log", "a")

tz = timezone("Europe/Moscow")
logging.Formatter.converter = lambda *args_converter: datetime.now(tz=tz).timetuple()
logging.basicConfig(level=logging.INFO,
                    filename="log/py.log",
                    filemode="a",
                    encoding="UTF-8",
                    format="%(asctime)s %(levelname)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
logging.getLogger("aiogram").setLevel(logging.WARNING)

logger = logging.getLogger("media2gif")
