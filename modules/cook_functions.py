"""
cook_functions.py is indirectly called by main() in cooking.py and calls all of the functions
in cooking.py necessary to run the program from start to finish
"""

import functools

from yaml import safe_load

import cooking
from modules import dish


def load_yaml(yaml_file) -> dict:
    """
    Takes a yaml file and loads the file into memory
    """
    with open(yaml_file) as yaml:
        return safe_load(yaml)


def func_reader() -> None:
    """
    Calls functions necessary to read dishes.yaml and produce the cooking plan
    """
    organizer = cooking.Organizer()
    yaml_dishes = load_yaml("dishes.yaml")
    organizer = cooking.Organizer()
    for plate in yaml_dishes:
        structured_dish = dish.Dish(
            dish_name=plate,
            description=yaml_dishes[plate]["description"],
            ingredients=yaml_dishes[plate]["ingredients"],
            servings=yaml_dishes[plate]["servings"],
            steps=yaml_dishes[plate]["steps"],
        )
        structured_dish.construct_dish()
        organizer.dishes.update(structured_dish.dish)
        if structured_dish.dish[plate]["total_duration"] > organizer.max_duration:
            organizer.max_duration = structured_dish.dish[plate]["total_duration"]
    print(
        f"Reading all dishes from dishes.yaml. Your meal will require {organizer.max_duration} "
        "minutes to prep.\n"
    )
    organizer.assign_start_time()
    organizer.assign_actions()
    organizer.broadcast_details()
    organizer.broadcast_instructions()


def func_writer() -> None:
    """
    Calls functions necessary to write any dishes from dishes.yaml to DynamoDB
    """


def func_selector() -> None:
    """
    Calls functions necessary to select dishes from DynamoDB and output the cooking plan
    """


def func_modifier() -> None:
    """
    Calls all functions necessary to modifies dishes in DynamoDB to reflect the dishes with
    the same name in the given yaml file
    """
