import configparser


def parse():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['DEFAULT']['companies'].split(',')
