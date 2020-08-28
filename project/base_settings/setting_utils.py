# list of all utility attributes
list_of_attributes = ['list_of_attributes', 'parse_bool_from_str', 'auth_from_env', '_auth']

def parse_bool_from_str(string):
    return string.lower() in ['true', '1', 't', 'y', 'yes']
