import configparser

def config_reader():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config