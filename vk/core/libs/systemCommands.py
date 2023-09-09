from .tool import Kit

kit = Kit.build()
cursor = kit.getCursor()

@cursor.command("ls")
def commandLS(*params):
    res = kit.runSystemCommand("ls", params)
    # res 
    for line in res.stdout.decode('utf-8').split('\n')[:-1]:
        kit.print(line)
    for line in res.stderr.decode('utf-8').split('\n')[:-1]:
        kit.error(line)

@cursor.command("cd")
def commandCD(newCurrentDirectory):
    try:
        kit.changeCurrentDirectory(newCurrentDirectory)
    except FileNotFoundError:
        kit.error(f'No such file or directory: "{newCurrentDirectory}"')


@cursor.command("exit")
def commandEXIT():
    exit()

@cursor.command("help")
def commandHELP():
    kit.error(f'pass')

# pwd
# mkdir
# touch
# cat
# ping
# cp
# mv
# rm
# rmdir
# grep
# find
# wc
# whet
# git