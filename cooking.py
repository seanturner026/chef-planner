"""cooking.py reads dishes from a yaml file or database, and prints out ordered instructions
detailing when to execute each step listed in dishes.yaml so that all dishes will be ready
at the same point in time
"""

import argparse
import sys
# import time

from ruamel.yaml import YAML
from modules import cook_functions


def load_yaml(yaml_file):
    """Load a yaml file containing dishes"""
    # returns commented dict object
    yaml = YAML()
    with open(yaml_file) as file:
        return yaml.load(file)


def get_durations(dishes):
    """Generates a list which contains calculations of the total time required for each dish"""
    # instantiate a list to hold the total duration required for each dish
    durations = []
    # loop through each dish, and write the total duration for the current dish to durations
    for dish in dishes.keys():
        total_duration = 0
        # calculating the total duration for the current dish
        for step in dishes[dish].keys():
            if isinstance(step, int):
                total_duration += dishes[dish][step][0]
        # writing total duration for current dish to total_duration list
        durations.append(total_duration)
        # instantiating max duration variable
        max_duration = max(durations)
        # instantiating index of max duration in durations as a list
        # serves to identify which dish(es) requires the most time
        max_duration_idx = [i for i, v in enumerate(durations) if v == max_duration][0]

    return durations, max_duration, max_duration_idx


def assign_time(dishes, max_duration_idx, durations):
    """Append start times to each dish"""
    # iterate through dishes
    for i, k in enumerate(dishes.keys()):
        # flow control to select the dish(es) requiring the most time
        if i == max_duration_idx:
            # iterate through steps for the current dish
            for j, step in enumerate(dishes[k].keys()):
                # flow control to select the step to execute first
                if j == 0:
                    # write time 0 to the list for step zero for current dish
                    dishes[k][step].append(0)
                # flow control to select following steps
                elif isinstance(step, int):
                    # instantiate variable to hold current point in time after all preceeding steps
                    # have been executed
                    start = dishes[k][step - 1][0] + dishes[k][step-1][2]
                    # write current point in time to current step for current dish
                    dishes[k][step].append(start)
        # flow control for all other dishes
        else:
            # iterate through steps for the current dish
            for j, step in enumerate(dishes[k].keys()):
                # flow control to select the step to execute first
                if j == 0:
                    # instantiate variable to hold point in time when the dish should be started
                    start = durations[max_duration_idx] - durations[i]
                    # write time to the list for step zero for the current dish
                    dishes[k][step].append(start)
                # flow control to select following steps
                elif isinstance(step, int):
                    # instantiate variable to hold current point in time after all preceeding steps
                    # have been executed
                    start = dishes[k][step - 1][0] + dishes[k][step-1][2]
                    # write current point in time to current step for current dish
                    dishes[k][step].append(start)

    return dishes


def organise_steps(dishes, max_duration):
    """Instantiate list to hold all step details (duration, instruction, point in time) and list to
    hold points in time that require action
    """
    instructions, epochs = [], []
    # iterate through dishes
    for dish in dishes.keys():
        # iterate through steps
        for step in dishes[dish].keys():
            if isinstance(step, int):
                # extract step details (duration, instruction, point in time) for current dish, and
                # write to instructions list
                instructions.append(dishes[dish][step])
                # append current dish to instructions list
                instructions[-1].append(dish)
                # extract points in time that require action to epochs list
                epochs.append(dishes[dish][step][2])
    # sort points in time in ascending order
    epochs = sorted(epochs)
    # create dictionary to keep track of point in time frequency
    epochs_d = {}
    # iterate through points in time
    for epoch in epochs:
        # flow control to see if a particular point in time already exists
        if epoch in epochs_d.keys():
            # increase point in time frequency by one
            epochs_d.update({epoch: (epochs_d[epoch]+1)})
        else:
            # create specific point in time as a dictionary key
            epochs_d[epoch] = 1
    # add final point in time to epochs
    epochs.append(max_duration)
    epochs_d.update({max_duration: 0})

    return instructions, epochs_d


def concurrency(instructions, epochs_d):
    """Read output generated by organise_steps function and handle points in time which require
    more than one action
    """
    # instantiate dictionary to hold all step details in order
    instructions_ordered = {}
    # iterate through ordered points in time
    for key in epochs_d.keys():
        if epochs_d[key] > 1:

            orders = {}
            # iterate over instructions holding all step details
            for instruction in instructions:
                # flow control to select steps in order
                if key == instruction[2]:
                    orders.update({
                        instruction[3]: [instruction[1], instruction[2], instruction[0]]
                        })
            instructions_ordered.update({key: orders})
            continue

        for instruction in instructions:
            # flow control to select steps in order
            if key == instruction[2]:
                # # write step lists to instructions_ordered in order of time
                instructions_ordered.update({key: {instruction[3]: [instruction[1],
                                                                    instruction[2],
                                                                    instruction[0]
                                                                    ]}})
    return instructions_ordered


def broadcast_details(dishes):
    """Print the ingredients and servings required to produce the various dishes"""
    dish_details = {}
    # iterate through dishes
    for dish in dishes.keys():
        # create an empty dictionary as a value for a dish name in dish_details
        dish_details.update({dish: {}})
        # iterate through the keys for each dish in dishes
        for k in dishes[dish].keys():
            if k == 'ingredients':
                # add ingredients as a key with value to dish_details
                dish_details[dish].update({'ingredients': dishes[dish][k]})
            elif k == 'servings':
                # add servings as a key with value to dish_details
                dish_details[dish].update({'servings': dishes[dish][k]})
    # iterate through dish_details
    for dish in dish_details:
        # check if no ingredient or serving information is provided
        if dish_details[dish]['ingredients'] is None:
            if dish_details[dish]['servings'] is None:
                print(f'{dish} (no serving information or ingredients provided)')
            # print serving information only
            else:
                print(f'{dish} serves {dish_details[dish]["servings"]} (ingredients not provided)')
        # print ingredient information only
        elif dish_details[dish]['servings'] is None:
            print(f'{dish} requires the following ingredients (no serving information provided):')
            for ingredient in dish_details[dish]['ingredients']:
                print('*', ingredient)
        # print serving and ingredient information
        else:
            print(f'{dish} serves {dish_details[dish]["servings"]}, and requires the following ingredients:')
            for ingredient in dish_details[dish]['ingredients']:
                print('*', ingredient)
    print()
    return None


def combine_instructions(instructions_ordered, max_duration):
    """Combine instructions when the time difference between two steps is two minutes or less"""
    delete = []
    for i, k in enumerate(instructions_ordered):

        if i + 1 is len(instructions_ordered):
            break
        if list(instructions_ordered)[i + 1] - list(instructions_ordered)[i] <= 1:
            instructions_ordered.update({
                k: {**instructions_ordered[k],
                    **instructions_ordered[list(instructions_ordered)[i + 1]]
                    }
                })
            original_time = instructions_ordered[k][list(instructions_ordered[k])[0]][2]
            for dish in instructions_ordered[k]:
                instructions_ordered[k][dish][2] = original_time
            delete.append(list(instructions_ordered)[i + 1])

    for k in delete:
        del instructions_ordered[k]

    return instructions_ordered


def broadcast_instructions(instructions_ordered, max_duration):
    """Print timings for various dishes"""
    print('INSTRUCTIONS:\n')
    # iterate through the dictionary -- outermost keys are points in time
    for i, current_time in enumerate(instructions_ordered):
        # check that current_time is not the final point in time
        if current_time != list(instructions_ordered)[-1]:
            # print the difference in time between current_time and the next iter of current_time
            print(f'Set timer for {list(instructions_ordered)[i + 1] - list(instructions_ordered)[i]} minutes')
            # print the dish name and step given current_time
            for dish in instructions_ordered[current_time]:
                print(f'» {dish}: {instructions_ordered[current_time][dish][0]}')
                if dish is list(instructions_ordered[current_time])[-1]:
                    print()
        # check that current_time is the final point in time
        elif current_time == list(instructions_ordered)[-1]:
            # print the time until all dishes are ready
            print(f'Set timer for {max_duration - current_time} minutes.')
            # print the dish name and step given current_time
            for dish in instructions_ordered[current_time]:
                print(f'» {dish}: {instructions_ordered[current_time][dish][0]}')

    print('\nAll of your dishes should be finished. Enjoy!')
    return None


def db_duplication_check(dishes, cur):
    """Check the database for duplicate dish names, and prevent duplicates from being entered into
    the database
    """
    # extract all dish names from the database as an iterable
    cur.execute("SELECT dish FROM dishes")
    # iterate through database extraction
    for dish in cur.fetchall():
        # check if the dish name from the database is the same as in the yaml file
        if dish[0] in dishes.keys():
            print(f'{dish[0]} already exists in the database. Please rename the dish in the yaml file.')
            sys.exit(0)
            # print(f'Would you like to rename {dish[0]}, exit?')
            # choice = input('rename / exit ')
            # if choice == 'exit':
            #     sys.exit(0)
            # else:
    return None


def flatten_yaml(dishes):
    """Flatten each dish from the yaml into a dictionary which can be entered into the database"""
    dishes_flat = {}
    # iterate through dishes
    for dish in dishes.keys():
        # dishes_flat will hold the data from the yaml in a format that the database can take
        dishes_flat.update({dish: {}})
        dishes_flat[dish].update({'dish_name': dish})
        # instantiate various python objects to hold the corresponding information for each dish
        dish_durations = []
        dish_instructions = []
        dish_ingredients = []
        dish_servings = 0
        dish_total_duration = 0
        # iterate through the keys for each dish in dishes
        for step in dishes[dish].keys():
            # check if the key is an integer -- the associated values are lists containing
            # [step_duration, step_instruction]
            if isinstance(step, int):
                # write step_duration to dish_durations
                dish_durations.append(dishes[dish][step][0])
                # write step_instruction to dish_instructions
                dish_instructions.append(dishes[dish][step][1])
                # add step_duration to dish_total_duration
                dish_total_duration += dishes[dish][step][0]
            # check if the key is description
            elif step == 'description':
                # write the description for the current dish to dish_description
                dish_description = dishes[dish][step]
            elif step == 'ingredients':
                dish_ingredients = dishes[dish][step]
            elif step == 'servings':
                dish_servings = dishes[dish][step]
        # write all objects to dishes_flat
        dishes_flat[dish].update({'dish_name':      dish})
        dishes_flat[dish].update({'duration':       dish_durations})
        dishes_flat[dish].update({'total_duration': dish_total_duration})
        dishes_flat[dish].update({'instructions':   dish_instructions})
        dishes_flat[dish].update({'description':    dish_description})
        dishes_flat[dish].update({'ingredients':    dish_ingredients})
        dishes_flat[dish].update({'servings':       dish_servings})

    return dishes_flat


def write_db_entries(dishes_flat, conn, cur):
    """Iterate through the flattened dictionary and enter it into the database"""
    for dish in dishes_flat.keys():
        cur.execute("""
                    INSERT INTO dishes (dish,
                                        duration,
                                        total_duration,
                                        instructions,
                                        description,
                                        ingredients,
                                        servings)
                    VALUES(%(dish_name)s,
                           %(duration)s,
                           %(total_duration)s,
                           %(instructions)s,
                           %(description)s,
                           %(ingredients)s,
                           %(servings)s)
                    """,
                    dishes_flat[dish])
        conn.commit()
        print(f'Wrote {dishes_flat[dish]["dish_name"]} to the database')
    return None


def fetch_db(cur):
    """Collect all database entries and print the dish id and dish name to the console"""
    # instantiate empty dictionary to hold database extraction
    items = {}
    # extract all dishes from the database as an iterable
    cur.execute("SELECT * FROM dishes")
    # iterate through dishes extracted from database
    for i, dish in enumerate(cur.fetchall()):
        # write the extracted dish to the dictionary
        items.update({i: dish})
    # iterate through extracted dishes and print dish names to the terminal
    for i, _ in enumerate(items):
        print('{:3} {:^4} {}'.format(i, ' ', items[i][1]))

    return items


def fetch_dish_id(dishes_flat, cur):
    """Appends dish id from database to flattened yaml"""
    # extract all dishes from the database as an iterable
    cur.execute("SELECT * FROM dishes")
    # iterate through dishes extracted from database
    for dish in enumerate(cur.fetchall()):

        if dish[1][1] in dishes_flat.keys():
            dishes_flat[dish[1][1]].update({'id': dish[1][0]})

    return dishes_flat


def update_db(dishes_flat, conn, cur):
    """Modifies existing database entry indexed by dish id"""
    for dish in dishes_flat.keys():

        cur.execute("""
                    UPDATE dishes
                    SET duration =   %(duration)s,
                    total_duration = %(total_duration)s,
                    instructions =   %(instructions)s,
                    description =    %(description)s,
                    ingredients =    %(ingredients)s,
                    servings =       %(servings)s
                    WHERE id =       %(id)s
                    """,
                    dishes_flat[dish])

        conn.commit()

        print(f'* {dish} has been updated in the database')
    print('\nDone!')
    return None


def read_db_entries(dishes):
    """Combine all tuples produced by database query back into format resembling dishes.yaml"""
    dishes_dict = {}
    for entry in dishes:
        dishes_dict.update({entry[0]: {}})

        for i, _ in enumerate(entry[3]):
            dishes_dict[entry[0]].update({i: []})
            dishes_dict[entry[0]][i].append(entry[2][i])
            dishes_dict[entry[0]][i].append(entry[3][i])
        dishes_dict[entry[0]].update({'description': entry[4]})
        dishes_dict[entry[0]].update({'servings':    entry[5]})
        dishes_dict[entry[0]].update({'ingredients': entry[6]})

    return dishes_dict


def parse_command_line():
    """Return the command line arguments as a dictionary"""
    parser = argparse.ArgumentParser(description='Chef planning assistant')

    parser.add_argument('-f', '--file', nargs='?', default=False,
                        help='create cooking plan using a specified yaml file')

    parser.add_argument('-r', '--reader', action='store_true', default=False,
                        help='create cooking plan using dishes.yaml')

    parser.add_argument('-w', '--writer', action='store_true', default=False,
                        help='write recipies from dishes.yaml to the '
                        'persistent database')

    parser.add_argument('-s', '--selector', action='store_true', default=False,
                        help='create cooking plan using recipies existing in the '
                        'persistent database')

    parser.add_argument('-m', '--modifier', nargs='?', default=False,
                        help='modify all recipies in the persistent database by '
                        'the same name as in a specified yaml file')

    parser.add_argument('-fw', '--file_writer', nargs='?', default=False,
                        help='write recipies from a specified yaml file to the '
                        'persistent database')

    return vars(parser.parse_args())


def parse_arguments():
    """Executes flow control to check cli flags and run program accordingly"""
    args = parse_command_line()
    for key in args.keys():
        if args.get(key) is not False:
            return {
                'reader':      cook_functions.func_reader,
                'writer':      cook_functions.func_writer,
                'selector':    cook_functions.func_selector,
                'file':        cook_functions.func_file,
                'file_writer': cook_functions.func_file_writer,
                'modifier':    cook_functions.func_modifier
                }.get(key)(args)
    print('Please specify a flag as a command line argument.')
    print('See \"python cooking.py -h\" for additional information.')
    return None


def main():
    """Only run when the program is run directly"""
    parse_arguments()


# top-level scripting environment
if __name__ == "__main__":

    main()
