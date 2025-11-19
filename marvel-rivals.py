def get_api_key(filename):
    with open(filename) as file:
        key = file.readlines()[2].split("=")[1].strip(" ")
    return key

API_key = get_api_key("api_keys.txt")