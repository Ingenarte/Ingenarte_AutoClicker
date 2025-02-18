# components/utils.py
component_counter = 0

def get_next_id():
    global component_counter
    component_counter += 1
    return component_counter - 1