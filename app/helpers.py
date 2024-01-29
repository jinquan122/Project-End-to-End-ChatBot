import configparser

def config_reader():
    '''
    Read the config file and return the config object.
    Returns: 
        config object.
    '''
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config