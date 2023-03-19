import json
import uuid
def string_to_json(input_string):
    # Remove the single quotes from the input string
    return input_string.replace("b'", "'").replace("'", "\"")
    # Convert the string to a dictionary
    # dict_obj = {}
    # for key_value in input_string.split(", "):
    #     key, value = key_value.split(": ")
    #     dict_obj[key] = value.encode("utf-8").decode("unicode_escape").strip("b'")

    # Convert the dictionary to a JSON object

if __name__ == '__main__':
    print(uuid.uuid4())
