from riposte import Riposte
from riposte.printer import Palette
import os
import subprocess
import tomllib
from collections import namedtuple

class Kit:

    _Initcursor = None

    def __init__(self, config):
        Config = namedtuple('Config', 'appName')
        self.config = Config(config['tool']['poetry']['name'])
        self.cursor = Riposte(prompt=f'{self.config.appName}:{os.getcwd()}$ ')

    @staticmethod
    def build():
        config = tomllib.load(open(os.path.dirname(os.path.abspath(__file__)) + "/../../../pyproject.toml", "rb"))
        if Kit._Initcursor == None:
            Kit._Initcursor = Kit(config)
        return Kit._Initcursor

    def getCursor(self):
        return self.cursor

    def success(self, string):
        return self.getCursor().print(Palette.GREEN.format('[+] '), string)

    def error(self, string):
        return self.getCursor().print(Palette.RED.format('[-] '), string)
    
    def warning(self, string):
        return self.getCursor().print(Palette.YELLOW.format('[!] '), string)

    def print(self, string):
        return self.getCursor().print(string)

    def runSystemCommand(self, systemCommand, params):
        return subprocess.run([systemCommand, *params], capture_output=True)

    def getPrompt(self):
        return self.getCursor()._prompt

    def getAppName(self):
        return self.config.appName

    def setPrompt(self, newPrompt):
        self.getCursor()._prompt = newPrompt

    def changeCurrentDirectory(self, newCurrentDirectory):
        os.chdir(newCurrentDirectory)
        self.setPrompt(f'{self.getAppName()}:{self.getCurrentDirectory()}$')

    def getCurrentDirectory(self):
        return os.getcwd()

    def makeQuestion(self, question):
        ind = None
        while ind not in ['y', 'Y', 'n', 'N']:
            ind = input(question + '\n')
        return {
            'y': True,
            'Y': True,
            'n': False,
            'N': False,
        }[ind]