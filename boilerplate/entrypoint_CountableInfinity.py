from util.Client import Client
if __name__ == '__main__':
    bot_name = b"NAME CountableInfinity\n" # <--- bot name goes where it says "aaa"
    c = Client(bot_name)
    c.setup_bot()
    c.run_bot()
