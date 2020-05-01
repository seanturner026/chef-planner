"""
Cooking.py reads dishes.yaml, plans out a workflow, and broadcasts the workflow to the terminal
"""

import collections

import click

from modules import cook_functions


class Organizer:
    """
    Oragnizer takes a collection of Dish.dish objects and structures them into self.dishes, and
    then restructures self.dishes into self.epochs

    Example Structure self.dishes
    -----------------------------
    {
        "Salad": {
            "description": "some salad",
            "ingredients": [{"ingredient": "salad", "quantity_with_units": "1 bag"}],
            "servings": 3,
            "start_time": 0,
            "steps": {
                0: {"duration": 12, "instruction": "Make dressing"},
                1: {"duration": 4, "instruction": "Toss salad"},
            },
            "total_duration": 16,
        },
        "Pasta": {
            "description": "delish pasta",
            "ingredients": [
                {"ingredient": "noodles", "quantity_with_units": "16 oz"},
                {"ingredient": "pesto", "quantity_with_units": "1 jar"},
            ],
            "servings": 4,
            "start_time": 0,
            "steps": {
                0: {"duration": 16, "instruction": "Boil noodles"},
                1: {"duration": 3, "instruction": "Mix noodles with sauce"},
            },
            "total_duration": 19,
        },
        "Steak": {
            "description": "STEAK",
            "ingredients": [{"ingredient": "ny strip", "quantity_with_units": "1 kg"}],
            "servings": 4,
            "start_time": 0,
            "steps": {0: {"duration": 16, "instruction": "Cook steak"}},
            "total_duration": 16,
        },
    }

    Example Structure self.epochs
    -----------------------------
    OrderedDict(
        [
            (0, {"Pasta": {"instruction": "Boil noodles", "duration": 16}}),
            (
                3,
                {
                    "Salad": {"instruction": "Make dressing", "duration": 12},
                    "Steak": {"instruction": "Cook steak", "duration": 16},
                },
            ),
            (15, {"Salad": {"instruction": "Toss salad", "duration": 4}}),
            (16, {"Pasta": {"instruction": "Mix noodles with sauce", "duration": 3}}),
        ]
    )
    """

    def __init__(self):
        self.dishes = {}
        self.epochs = {}
        self.max_duration = 0

    def assign_start_time(self) -> None:
        """
        Append start times to each dish based on what other dishes are being made, and write start
        times to epochs.
        """
        for plate in self.dishes:
            if self.dishes[plate]["total_duration"] != self.max_duration:
                self.dishes[plate]["start_time"] = (
                    self.max_duration - self.dishes[plate]["total_duration"]
                )
            start_time = self.dishes[plate]["start_time"]
            if start_time not in self.epochs.keys():
                self.epochs[start_time] = {}
            self.epochs[start_time].update(
                {
                    plate: {
                        "instruction": self.dishes[plate]["steps"][0]["instruction"],
                        "duration": self.dishes[plate]["steps"][0]["duration"],
                    }
                }
            )

    def assign_actions(self) -> None:
        """
        Parse dishes and populate epochs with points in time that completes instructions for all
        dishes.
        """
        for plate in self.dishes:
            for step in self.dishes[plate]["steps"]:
                if step != 0:
                    point_in_time = (
                        self.dishes[plate]["start_time"]
                        + self.dishes[plate]["steps"][step - 1]["duration"]
                    )
                    if point_in_time not in self.epochs.keys():
                        self.epochs[point_in_time] = {}
                    self.epochs[point_in_time].update(
                        {
                            plate: {
                                "instruction": self.dishes[plate]["steps"][step][
                                    "instruction"
                                ],
                                "duration": self.dishes[plate]["steps"][step][
                                    "duration"
                                ],
                            }
                        }
                    )
        self.epochs = collections.OrderedDict(sorted(self.epochs.items()))

    def broadcast_details(self) -> None:
        """
        Print the ingredients and servings required to produce the various dishes
        """
        for plate in self.dishes:
            print(
                f"{plate} serves {self.dishes[plate]['servings']}, "
                "and requires the following ingredients:"
            )
            for ingredient_collection in self.dishes[plate]["ingredients"]:
                print(
                    f"* {ingredient_collection['ingredient']}, "
                    f"{ingredient_collection['quantity_with_units']}"
                )
        print()

    def broadcast_instructions(self) -> None:
        """
        Print timings for various dishes
        """
        print("INSTRUCTIONS:\n")
        for idx, current_time in enumerate(self.epochs):
            points_in_time = list(self.epochs.keys())
            if current_time != points_in_time[-1]:
                print(
                    f"Set timer for {points_in_time[idx + 1] - points_in_time[idx]} minutes"
                )
                for dish in self.epochs[current_time]:
                    print(f"» {dish}: {self.epochs[current_time][dish]['instruction']}")
                    if dish is list(self.epochs[current_time])[-1]:
                        print()
            else:
                print(f"Set timer for {self.max_duration - current_time} minutes.")
                for dish in self.epochs[current_time]:
                    print(f"» {dish}: {self.epochs[current_time][dish]['instruction']}")
        print("\nAll of your dishes should be finished. Enjoy!")


def parse_arguments(
    modifier: str or None,
    reader: str or None,
    selector: str or None,
    writer: str or None,
) -> None:
    """
    Executes flow control to check commandline flag and run program accordingly
    """
    for key in [modifier, reader, selector, writer]:
        if key:
            switch_function(key)
    print("Please specify a flag as a command line argument.")
    print('See "python cooking.py -h" for additional information.')


def switch_function(key: str) -> ():
    """
    Reads parsed command line flag and runs corresponding workflow

    Parameters
    ----------
    key:
    - modifier
    - reader
    - selector
    - writer

    Returns
    -------
    Call to function
    - cook_functions.func_modifier()
    - cook_functions.func_reader()
    - cook_functions.func_selector()
    - cook_functions.func_writer()
    """
    return {
        "modifier": cook_functions.func_modifier,
        "reader": cook_functions.func_reader,
        "selector": cook_functions.func_selector,
        "writer": cook_functions.func_writer,
    }.get(key)()


@click.command()
@click.option(
    "-m",
    "--modifier",
    default=None,
    flag_value="modifier",
    help="modify all recipies in the persistent database by the same name as in a specified "
    "yaml file",
)
@click.option(
    "-r",
    "--reader",
    default=None,
    flag_value="reader",
    help="create cooking plan using dishes.yaml",
)
@click.option(
    "-s",
    "--selector",
    default=None,
    flag_value="selector",
    help="create cooking plan using recipies existing in the persistent database",
)
@click.option(
    "-w",
    "--writer",
    default=None,
    flag_value="writer",
    help="write recipies from dishes.yaml to the persistent database",
)
def main(modifier, reader, selector, writer):
    """
    Reads command line arguments and begins workflow
    """
    parse_arguments(modifier=modifier, reader=reader, selector=selector, writer=writer)


if __name__ == "__main__":
    main()
