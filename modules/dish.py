"""
dish.py contains a custom datatype of class Dish that provides documentation of the object being
organized by cooking.py
"""

import sys


class Dish:
    """
    Dish is a custom data type that holds information parsed from dishes.yaml

    Example Structure self.dish
    ---------------------------
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
        }
    }
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
        Initialize Dish
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
        Ensure that length does not exceed a specified maximum
        """
        if len(obj) > length:
            sys.exit(f"{message}")

    def validate_dish_name(self):
        """
        Ensure that self.dish_name does not contain numbers, and is not greater than 60 characters
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
        Ensure that self.description is not greater than __ characters
        """

    def validate_ingredients(self):
        """
        Ensure that each dictionary in self.ingredients respects the defined schema, and also
        ensure that an ingredient's name does not exceed 30 characters
        """
        for ingredient_dict in self.ingredients:
            for k in ingredient_dict.keys():
                if k not in ["ingredient", "quantity_with_units"]:
                    sys.exit("Please fix the schema of the passed ingredients")
                if not isinstance(ingredient_dict["ingredient"], str):
                    sys.exit(
                        f"Please specify strings for ingredients of {ingredient_dict[k]}"
                    )
            self.validate_length(
                obj=ingredient_dict["ingredient"],
                length=30,
                message=f"Please us a shorter name for ingredient {ingredient_dict['ingredient']} "
                f"in {self.dish_name}",
            )

    def validate_servings(self):
        """
        Ensure that self.servings is an integer
        """
        if not isinstance(self.servings, int):
            sys.exit(f"Please specify an integer for servings in {self.dish_name}")

    def validate_steps(self):
        """
        Ensure that self.steps does not contain more than 30 steps, that each step's length does
        not exceed 500 characters, and that a positive integer is pass for each step's duration
        """
        self.validate_length(
            obj=self.steps.keys(), length=30, message="Please use fewer steps for"
        )
        for step_num in self.steps:
            self.validate_length(
                obj=self.steps[step_num]["instruction"],
                length=500,
                message=f"Please use fewer steps for in {self.dish_name}",
            )
            if self.steps[step_num]["duration"] <= 0 or not isinstance(
                self.steps[step_num]["duration"], int
            ):
                sys.exit(
                    f"Please use a positive integer in minutes as duration for step {step_num} in "
                    f"{self.dish_name}"
                )

    def validate_dish(self):
        """
        Call all validate functions to ensure self.dish respects the schema
        """
        self.validate_dish_name()
        self.validate_description()
        self.validate_ingredients()
        self.validate_servings()
        self.validate_steps()

    def write_total_duration(self):
        """
        Sum up all steps to determine how long self.dish will take to produce
        """
        for step_num in self.steps:
            self.total_duration += self.steps[step_num]["duration"]

    def construct_dish(self):
        """
        Call all functions to combine all attributes into self.dish
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
