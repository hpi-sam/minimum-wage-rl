
# from urllib.parse import parse_qs

import configparser

class ConfigurationParser:
    
    __parser_instance = None
    
    @staticmethod
    def get_instance(file_name):
        if ConfigurationParser.__parser_instance == None:
            __parser_instance = ConfigurationParser(file_name)
            return __parser_instance
        return ConfigurationParser.__parser_instance

    def __init__(self, file_name) -> None:
        if ConfigurationParser.__parser_instance !=None:
            raise Exception("Parser instance already exists, USE get_instance method")
        else:
            ConfigurationParser.__parser_instance = self

        self.parser = configparser.ConfigParser()
        self.parser.read(file_name)