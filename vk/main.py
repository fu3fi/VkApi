from .core.libs.tool import Kit
from .core.libs import systemCommands
from .bin import mainHandler

def run():
    Kit.build().getCursor().run()