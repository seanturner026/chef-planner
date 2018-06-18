"""
cooking.py reads dishes from a yaml file or database, and prints out ordered instructions
detailing when to execute each step listed in dishes.yaml so that all dishes will be ready
at the same point in time
"""

# TODO:

#  1) Data visualisations? -- time on x-axis depicting frequency of actions.
#  2) Create class to hold all functions
#  3) Flask + front end
#  4) How to account for the time needed to boil water and also preheating oven?
# key in dishes.yaml that specifies that the oven is needed or that water
# needs to be boiled?
#  5) Ask for how long it will take the user's oven to preheat to x
# temperature, or how long it will take  to boil water. Where to store these
# values for future use? in a second database?
#  6) Add alias column to database? Will be used when printing instructions.
# Beef Bourguignon v. Beef Bourguignon with Onions and Carrots. Should the
# alias column support a character limit?

import ruamel.yaml
import argparse
import sys
import psycopg2
# import time

def get_durations(dishes):
    """
    Generates a list which contains calculations of the total time required
    for each dish
    """
    # instantiate a list to hold the total duration required for each dish
    durations = []
    # loop through each dish, and write the total duration for the current dish
    # to durations
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

def assign_time(dishes):
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
                    # instantiate variable to hold current point in time after
                    # all preceeding steps have been executed
                    start = dishes[k][step - 1][0] + dishes[k][step-1][2]
                    # write current point in time to current step for current dish
                    dishes[k][step].append(start)
        # flow control for all other dishes
        else:
            # iterate through steps for the current dish
            for j, step in enumerate(dishes[k].keys()):
                # flow control to select the step to execute first
                if j == 0:
                    # instantiate variable to hold point in time when the dish
                    # should be started
                    start = durations[max_duration_idx] - durations[i]
                    # write time to the list for step zero for the current dish
                    dishes[k][step].append(start)
                # flow control to select following steps
                elif isinstance(step, int):
                    # instantiate variable to hold current point in time after
                    # all preceeding steps have been executed
                    start = dishes[k][step - 1][0] + dishes[k][step-1][2]
                    # write current point in time to current step for current dish
                    dishes[k][step].append(start)

    return dishes

def organise_steps(dishes):
    """
    Instantiate list to hold all step details (duration, instruction,
    point in time) and list to hold points in time that require action
    """
    instructions, epochs = [], []
    # iterate through dishes
    for dish in dishes.keys():
        # iterate through steps
        for step in dishes[dish].keys():
            if isinstance(step, int):
                # extract step details (duration, instruction, point in time) for
                # current dish, and write to instructions list
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
    for e in epochs:
        # flow control to see if a particular point in time already exists
        if e in epochs_d.keys():
            # increase point in time frequency by one
            epochs_d.update({e:(epochs_d[e]+1)})
        else:
            # create specific point in time as a dictionary key
            epochs_d[e] = 1
    # add final point in time to epochs
    epochs.append(max_duration)
    epochs_d.update({max_duration:0})

    return instructions, epochs, epochs_d

def concurrency(instructions, epochs_d, dishes):
    """
    Read output generated by organise_steps function and handle points in time
    which require more than one action
    """
    # instantiate dictionary to hold all step details in order
    instructions_ordered = {}
    # iterate through ordered points in time
    for e in epochs_d.keys():
        if epochs_d[e] > 1:

            d = {}
            # iterate over instructions holding all step details
            for instruction in instructions:
                # flow control to select steps in order
                if e == instruction[2]:
                    d.update({instruction[3] : [instruction[1], instruction[2], instruction[0]]})
            instructions_ordered.update({e:d})
            continue

        for instruction in instructions:
            # flow control to select steps in order
            if e == instruction[2]:
                # # write step lists to instructions_ordered in order of time
                instructions_ordered.update({e : {instruction[3] : [instruction[1], \
                                                                    instruction[2], \
                                                                    instruction[0]]}})

    return instructions_ordered

def broadcast_details(dishes):
    """Print the ingredients and servings required to produce the various dishes"""
    dish_details = {}
    for dish in dishes.keys():
        dish_details.update({dish: {}})
        for k in dishes[dish].keys():
            if k == 'ingredients':
                dish_details[dish].update({'ingredients':dishes[dish][k]})
            elif k == 'servings':
                dish_details[dish].update({'servings':dishes[dish][k]})

    for dish in dish_details.keys():
        if dish_details[dish]['ingredients'] is None:
            if dish_details[dish]['servings'] is None:
                print('{} (no serving information or ingredients provided)' \
                .format(dish))
            else:
                print('{} serves {} (ingredients not provided)'\
                .format(dish, dish_details[dish]['servings']))
        elif dish_details[dish]['servings'] is None:
            print('{} requires the following ingredients \
            (no serving information provided):'.format(dish))
            for ingredient in dish_details[dish]['ingredients']:
                print('*', ingredient)
        else:
            print('{} serves {}, and requires the following ingredients:' \
            .format(dish, dish_details[dish]['servings']))
            for ingredient in dish_details[dish]['ingredients']:
                print('*', ingredient)
    print()

def broadcast_instructions(instructions_ordered, max_duration):
    """Print timings for various dishes"""
    print('INSTRUCTIONS:\n')
    # iterate through points in time
    for i, k in enumerate(instructions_ordered.keys()):
        if k != list(instructions_ordered.keys())[-1]:
            for dish in instructions_ordered[k].keys():
                print('{}: {}'.format(dish, instructions_ordered[k][dish][0]))
            print('» Set timer for {} minutes\n'.format( \
            list(instructions_ordered.keys())[i + 1] - \
            list(instructions_ordered.keys())[i]))
        elif k == list(instructions_ordered.keys())[-1]:
            for dish in instructions_ordered[k].keys():
                print('{}: {}'.format(dish, instructions_ordered[k][dish][0]))
            print('» Set timer for {} minutes. All of your dishes should be finished.'.format(max_duration - k))
        else:
            for dish in instructions_ordered[k].keys():
                print('{}: {}'.format(dish, instructions_ordered[k][dish][0]))
            print('» Set timer for {} minutes'.format(k))

    print('\nEnjoy!')

def db_duplication_check(dishes, conn, cur):
    """
    Check the database for duplicate dish names, and
    prevent duplicates from being entered into the database
    """
    cur.execute("SELECT dish FROM dishes")
    for dish in cur.fetchall():
        if dish[0] in dishes.keys():
            print('{} already exists in the database. Please rename the dish in the yaml file.'.format(dish[0]))
            sys.exit()

def flatten_yaml(dishes):
    """
    Flatten each dish in dishes.yaml into a dictionary
    which can be entered into the database
    """
    dishes_flat = {}
    for dish in dishes.keys():
        dishes_flat.update({dish : {}})
        dishes_flat[dish].update({'dish_name': dish})
        dish_durations = []
        dish_instructions = []
        dish_ingredients = []
        dish_servings = 0
        total_duration = 0

        for step in dishes[dish].keys():
            if isinstance(step, int):
                dish_durations.append(dishes[dish][step][0])
                dish_instructions.append(dishes[dish][step][1])
                total_duration += dishes[dish][step][0]
            elif step == 'description':
                dish_description = dishes[dish][step]
            elif step == 'ingredients':
                dish_ingredients = dishes[dish][step]
            elif step == 'servings':
                dish_servings = dishes[dish][step]

        dishes_flat[dish].update({'dish_name': dish})
        dishes_flat[dish].update({'duration': dish_durations})
        dishes_flat[dish].update({'total_duration': total_duration})
        dishes_flat[dish].update({'instructions': dish_instructions})
        dishes_flat[dish].update({'description': dish_description})
        dishes_flat[dish].update({'ingredients': dish_ingredients})
        dishes_flat[dish].update({'servings': dish_servings})

    return dishes_flat

def write_db_entries(dishes_flat, conn, cur):
    """Enter flattened dictionary into the database"""
    for dish in dishes_flat.keys():

        cur.execute("""
        INSERT INTO dishes (dish, duration, total_duration, instructions, description, ingredients, servings)
        VALUES(%(dish_name)s, %(duration)s, %(total_duration)s, %(instructions)s, %(description)s, %(ingredients)s, %(servings)s)
        """,
        dishes_flat[dish])

        conn.commit()
        print('Wrote {} to the database'.format(dishes_flat[dish]['dish_name']))

def fetch_db(conn, cur):
    """Collect all database entries and print the dish id and dish name to the console"""
    db = {}
    cur.execute("SELECT * FROM dishes")
    for i, dish in enumerate(cur.fetchall()):
        db.update({i:dish})
    # fetch all dishes from the database
    for i in range(len(db.keys())):
        print('{:3} {:^4} {}'.format(i, ' ', db[i][1]))

    return db

def fetch_dish_id(dishes_flat, conn, cur):
    """Appends dish id from database to flattened yaml"""
    cur.execute("SELECT * FROM dishes")
    for dish in enumerate(cur.fetchall()):
        if dish[1][1] in dishes_flat.keys():
            dishes_flat[dish[1][1]].update({'id' : dish[1][0]})

    return dishes_flat

def update_db(dishes_flat, conn, cur):
    """Modifies existing database entry indexed by dish id"""
    for dish in dishes_flat.keys():

        cur.execute("""
        UPDATE dishes
        SET duration = %(duration)s,
        total_duration = %(total_duration)s,
        instructions = %(instructions)s,
        description = %(description)s,
        ingredients = %(ingredients)s,
        servings = %(servings)s
        WHERE id = %(id)s
        """,
        dishes_flat[dish])

        conn.commit()

        print('{} has been updated in the database'.format(dish))
    print('\nDone!')

def read_db_entries(dishes, conn, cur):
    """Combine all tuples produced by database query back into format resembling dishes.yaml"""
    dishes_dict = {}
    for entry in dishes:
        dishes_dict.update({entry[0]: {}})

        for i, _ in enumerate(entry[3]):
            dishes_dict[entry[0]].update({i: []})
            dishes_dict[entry[0]][i].append(entry[2][i])
            dishes_dict[entry[0]][i].append(entry[3][i])
        dishes_dict[entry[0]].update({'description': entry[4]})
        dishes_dict[entry[0]].update({'servings': entry[5]})
        dishes_dict[entry[0]].update({'ingredients': entry[6]})

    return dishes_dict

# top-level scripting environment
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Chef planning assistant')

    parser.add_argument('-f', '--file', action='store_false', default=False,
                        help='create cooking plan using a specified yaml file')

    parser.add_argument('-r', '--reader', action='store_false', default=False,
                        help='create cooking plan using dishes.yaml')

    parser.add_argument('-w', '--writer', action='store_false', default=False,
                        help='write recipies from dishes.yaml to the \
                        persistent database')

    parser.add_argument('-s', '--selector', action='store_false', default=False,
                        help='create cooking plan using recipies existing in the \
                        persistent database')

    parser.add_argument('-m', '--modifier', action='store_false', default=False,
                        help='modify all recipies in the persistent database by \
                        the same name as in modify.yaml')

    parser.add_argument('-fw', '-file writer', action='store_false', default=False,
                        help='write recipies from a specified yaml file to the \
                        persistent database')

    if '-h' in sys.argv[1:]:
        print(parser.parse_args())

    elif '-f' in sys.argv[1:]:
        if len(sys.argv) < 3:
            print('Please specify a file after the \'-f\' flag')
        else:
            dishes = ruamel.yaml.load(open(sys.argv[2]))

            durations, max_duration, max_duration_idx = get_durations(dishes)
            print('Reading all dishes from {}. Your meal will require {} minutes to prepare.\n' \
                .format(sys.argv[2], max_duration))
            dishes = assign_time(dishes)
            instructions, epochs, epochs_d = organise_steps(dishes)
            instructions_ordered = concurrency(instructions, epochs_d, dishes)
            broadcast_details(dishes)
            broadcast_instructions(instructions_ordered, max_duration)

    elif '-r' in sys.argv[1:]:
        dishes = ruamel.yaml.load(open('dishes.yaml'))

        durations, max_duration, max_duration_idx = get_durations(dishes)
        print('Reading all dishes from dishes.yaml. Your meal will require {} minutes to prepare.\n' \
            .format(max_duration))
        dishes = assign_time(dishes)
        instructions, epochs, epochs_d = organise_steps(dishes)
        instructions_ordered = concurrency(instructions, epochs_d, dishes)
        broadcast_details(dishes)
        broadcast_instructions(instructions_ordered, max_duration)

    # need code to ask if an existing dish should be overwritten, OR, if the current
    # dish can be renamed
    elif '-w' in sys.argv[1:]:
        dishes = ruamel.yaml.load(open('dishes.yaml'))

        try:
            conn = psycopg2.connect(dbname='cooking', user='sean', host='localhost')
            cur = conn.cursor()
        except psycopg2.OperationalError:
            print('Cannot connect to the database.')

        db_duplication_check(dishes, conn, cur)

        print('Writing all dishes from dishes.yaml to the database...')
        dishes_flat = flatten_yaml(dishes)
        write_db_entries(dishes_flat, conn, cur)
        print('\nDone!')

        conn.close()
        cur.close()

    elif '-fw' in sys.argv[1:]:

        if len(sys.argv) < 3:
            print('Please specify a file after the \"-fw\" flag')
        else:
            dishes = ruamel.yaml.load(open(sys.argv[2]))
            try:
                conn = psycopg2.connect(dbname='cooking', user='sean', host='localhost')
                cur = conn.cursor()
            except psycopg2.OperationalError:
                print('Cannot connect to the database.')
            db_duplication_check(dishes, conn, cur)

            print('Writing all dishes from {} to the database...'.format(sys.argv[2]))
            dishes_flat = flatten_yaml(dishes)
            write_db_entries(dishes_flat, conn, cur)
            print('\nDone!')

            conn.close()
            cur.close()

    elif '-s' in sys.argv[1:]:

        try:
            conn = psycopg2.connect(dbname='cooking', user='sean', host='localhost')
            cur = conn.cursor()
        except psycopg2.OperationalError:
            print('Cannot connect to the database.')

        print('Select dishes to be prepared:\n')
        print('{} {:^4} {}'.format(' Id', ' ', 'Dish Name'))
        db = fetch_db(conn, cur)

        selection = input('\nPlease provide the id numbers of the dishes you would like to prepare, separated by spaces.\n» ').split()
        selection = [int(num) for num in selection]

        for i, selected in enumerate(selection):
            if i in db.keys():
                selection[i] = db[selected][1:]
                # converting tuple structure to list
                selection[i] = [item for item in selection[i]]

        selection = read_db_entries(selection, conn, cur)
        durations, max_duration, max_duration_idx = get_durations(selection)
        print('\nPreparing {}. Your meal will require {} minutes to prepare.\n' \
            .format((', ').join([dish for dish in selection.keys()]), max_duration))
        dishes = assign_time(selection)
        instructions, epochs, epochs_d = organise_steps(selection)
        instructions_ordered = concurrency(instructions, epochs_d, selection)
        broadcast_details(selection)
        broadcast_instructions(instructions_ordered, max_duration)

        conn.close()
        cur.close()

    elif '-m' in sys.argv[1:]:

        try:
            conn = psycopg2.connect(dbname='cooking', user='sean', host='localhost')
            cur = conn.cursor()
        except psycopg2.OperationalError:
            print('Cannot connect to the database.')

        dishes_modified = ruamel.yaml.load(open(sys.argv[2]))

        dishes_flat = flatten_yaml(dishes_modified)
        dishes_flat = fetch_dish_id(dishes_flat, conn, cur)

        print('The following dish(es) will be modified to match the contents of modify.yaml:')
        for dish in dishes_flat.keys():
            print('* {}'.format(dish))

        confirmation = input('Proceed? (y/n) > ')

        if confirmation == 'y':
            update_db(dishes_flat, conn, cur)
        elif confirmation == 'n':
            print('Database will not be updated')
        else:
            print('Please input the letters y or n.')

        conn.close()
        cur.close()

    else:
        print('Please specify a flag as a command line argument. \
        See \"python cooking.py -h\" for additional information.')