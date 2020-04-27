import collections
import sys

import click
from modules import cook_functions


class Dish:
    """
    pass
    """

    def __init__(
        self,
        dish_name: str,
        description: str,
        ingredients: list(dict({"ingredient": str, "quantity_with_units": str})),
        servings: int,
        steps: dict({int: dict({"duration": int, "instruction": str})}),
    ):
        """
        pass
        """
        self.dish = {}
        self.dish_name = dish_name
        self.description = description
        self.ingredients = ingredients
        self.servings = servings
        self.steps = steps
        self.total_duration = 0

    def validate_length(self, obj: str, length: int, message: str):
        """
        pass
        """
        if len(obj) > length:
            sys.exit(f"{message}")

    def validate_dish_name(self):
        """
        pass
        """
        for num in "0123456789":
            if num in self.dish_name:
                sys.exit("Dish names cannot contain numbers")
        self.validate_length(
            obj=self.dish_name,
            length=60,
            message=f"Please use a shorter name for {self.dish_name}",
        )

    def validate_description(self):
        """
        pass
        """
        pass

    def validate_ingredients(self):
        """
        pass
        """
        for ingredient_dict in self.ingredients:
            for k in ingredient_dict.keys():
                if k not in ["ingredient", "quantity_with_units"]:
                    sys.exit("Please fix the schema of the passed ingredients")
                if type(ingredient_dict["ingredient"]) != str:
                    sys.exit(
                        f"Please specify strings for ingredients of {ingredient_dict[k]}"
                    )
            self.validate_length(
                obj=ingredient_dict["ingredient"],
                length=30,
                message=f"Please us a shorter name for ingredient {ingredient_dict['ingredient']} in {self.dish_name}",
            )

    def validate_servings(self):
        """
        pass
        """
        pass

    def validate_steps(self):
        """
        pass
        """
        self.validate_length(
            obj=self.steps.keys(), length=30, message=f"Please use fewer steps for"
        )
        for step_num in self.steps:
            self.validate_length(
                obj=self.steps[step_num]["instruction"],
                length=500,
                message=f"Please use fewer steps for in {self.dish_name}",
            )
            if self.steps[step_num]["duration"] <= 0:
                sys.exit(
                    f"Please use a positive number in minutes as duration for step {step_num} in {self.dish_name}"
                )

    def validate_dish(self):
        """
        pass
        """
        self.validate_dish_name()
        self.validate_description()
        self.validate_ingredients()
        self.validate_servings()
        self.validate_steps()

    def write_total_duration(self):
        """
        pass
        """
        for step_num in self.steps:
            self.total_duration += self.steps[step_num]["duration"]

    def construct_dish(self):
        """
        pass
        """
        self.validate_dish()
        self.write_total_duration()
        self.dish.update(
            {
                self.dish_name: {
                    "description": self.description,
                    "ingredients": self.ingredients,
                    "servings": self.servings,
                    "start_time": 0,
                    "steps": self.steps,
                    "total_duration": self.total_duration,
                }
            }
        )


class Organizer:
    """
    Oragnizer takes a yaml file of instructions and structures them for Planner()
    """

    def __init__(self):
        self.dishes = {}
        self.durations = []
        self.epochs = {}
        self.instructions = []
        self.instructions_ordered = {}
        self.max_duration = 0
        self.max_duration_idx = 0

    def assign_time(self):
        """
        Append start times to each dish
        """
        for plate in self.dishes.keys():
            if self.dishes[plate]["total_duration"] != self.max_duration:
                self.dishes[plate]["start_time"] = (
                    self.max_duration - self.dishes[plate]["total_duration"]
                )

        for plate in self.dishes.keys():
            start_time = self.dishes[plate]["start_time"]
            if start_time not in self.epochs.keys():
                self.epochs[start_time] = {}
            else:
                existing_step = self.epochs[start_time]
            self.epochs[start_time].update(
                {
                    plate: {
                        "instruction": self.dishes[plate]["steps"][0]["instruction"],
                        "duration": self.dishes[plate]["steps"][0]["duration"],
                    }
                }
            )

            for idx, step in enumerate(self.dishes[plate]["steps"]):
                if step != 0:
                    point_in_time = (
                        self.dishes[plate]["start_time"]
                        + self.dishes[plate]["steps"][idx - 1]["duration"]
                    )
                    if point_in_time not in self.epochs.keys():
                        self.epochs[point_in_time] = {}
                    self.epochs[point_in_time].update(
                        {
                            plate: {
                                "instruction": self.dishes[plate]["steps"][idx][
                                    "instruction"
                                ],
                                "duration": self.dishes[plate]["steps"][idx][
                                    "duration"
                                ],
                            }
                        }
                    )
        self.epochs = collections.OrderedDict(sorted(self.epochs.items()))

    # def broadcast_details(self):
    #     """
    #     Print the ingredients and servings required to produce the various dishes

    #     Format of dish_details:
    #     {
    #         "Pasta": {"ingredients": ["16 oz noodles", "1 jar pesto"], "servings": 4},
    #         "Salad": {"ingredients": None, "servings": 3},
    #         "Steak": {"ingredients": None, "servings": None},
    #     }
    #     """
    #     for dish in self.dishes.keys():
    #         dish_details.update({dish: {}})
    #         for k in self.dishes[dish].keys():
    #             if k == "ingredients":
    #                 dish_details[dish].update({"ingredients": self.dishes[dish][k]})
    #             elif k == "servings":
    #                 dish_details[dish].update({"servings": self.dishes[dish][k]})
    #     for dish in dish_details:
    #         if dish_details[dish]["ingredients"] is None:
    #             if dish_details[dish]["servings"] is None:
    #                 print(f"{dish} (no serving information or ingredients provided)")
    #             else:
    #                 print(
    #                     f'{dish} serves {dish_details[dish]["servings"]} (ingredients not provided)'
    #                 )
    #         elif dish_details[dish]["servings"] is None:
    #             print(
    #                 f"{dish} requires the following ingredients (no serving information provided):"
    #             )
    #             for ingredient in dish_details[dish]["ingredients"]:
    #                 print("*", ingredient)
    #         else:
    #             print(
    #                 f"{dish} serves {dish_details[dish]['servings']}, and requires the following ingredients:"
    #             )
    #             for ingredient in dish_details[dish]["ingredients"]:
    #                 print("*", ingredient)
    #     print()

    # def combine_instructions(self):
    #     """
    #     Combine instructions when the time difference between two steps is two minutes or less
    #     """
    #     delete = []
    #     for i, k in enumerate(self.instructions_ordered):

    #         if i + 1 is len(self.instructions_ordered):
    #             break
    #         if (
    #             list(self.instructions_ordered)[i + 1]
    #             - list(self.instructions_ordered)[i]
    #             <= 1
    #         ):
    #             self.instructions_ordered.update(
    #                 {
    #                     k: {
    #                         **self.instructions_ordered[k],
    #                         **self.instructions_ordered[
    #                             list(self.instructions_ordered)[i + 1]
    #                         ],
    #                     }
    #                 }
    #             )
    #             original_time = self.instructions_ordered[k][
    #                 list(self.instructions_ordered[k])[0]
    #             ][2]
    #             for dish in self.instructions_ordered[k]:
    #                 self.instructions_ordered[k][dish][2] = original_time
    #             delete.append(list(self.instructions_ordered)[i + 1])

    #     for k in delete:
    #         del self.instructions_ordered[k]

    def broadcast_instructions(self):
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

def parse_arguments(dish_file, reader, writer, selector, modifier, file_writer):
    """Executes flow control to check cli flags and run program accordingly"""
    args = dict(
        {
            "dish_file": dish_file,
            "reader": reader,
            "writer": writer,
            "selector": selector,
            "modifier": modifier,
            "file_writer": file_writer,
        }
    )
    for key in args.keys():
        if args.get(key) is not False:
            return {
                "reader": cook_functions.func_reader,
                "writer": cook_functions.func_writer,
                "selector": cook_functions.func_selector,
                "dish_file": cook_functions.func_dish_file,
                "file_writer": cook_functions.func_file_writer,
                "modifier": cook_functions.func_modifier,
            }.get(key)(args)
    print("Please specify a flag as a command line argument.")
    print('See "python cooking.py -h" for additional information.')


@click.command()
@click.option("-d", "--dish_file", default=False, help="specifies yaml file to use")
@click.option(
    "-r",
    "--reader",
    default=False,
    flag_value=True,
    help="create cooking plan using dishes.yaml",
)
@click.option(
    "-w",
    "--writer",
    default=False,
    help="write recipies from dishes.yaml to the persistent database",
)
@click.option(
    "-s",
    "--selector",
    default=False,
    flag_value=True,
    help="create cooking plan using recipies existing in the persistent database",
)
@click.option(
    "-m",
    "--modifier",
    default=False,
    flag_value=True,
    help="modify all recipies in the persistent database by the same name as in a specified yaml file",
)
@click.option(
    "-fw",
    "--file_writer",
    default=False,
    help="write recipies from a specified yaml file to the persistent database",
)
def main(dish_file, reader, writer, selector, modifier, file_writer):
    parse_arguments(dish_file, reader, writer, selector, modifier, file_writer)


if __name__ == "__main__":
    main()
