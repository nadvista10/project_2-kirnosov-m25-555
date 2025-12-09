import prompt


def welcome():
    print("Первая попытка запустить проект!\n\n***")
    print_help()

    while(True):
        command = prompt.string("Введите команду:")
        print("\n")
        if command == "exit":
            break
        if command == "help":
            print_help()

def print_help():
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")