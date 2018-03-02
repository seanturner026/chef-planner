"""
cooking.py reads dishes.yaml, and prints out ordered instructions detailing when to 
execute each step listed in dishes.yaml so that all dishes will be ready at the same
point in time
"""

# TODO:

#  1) How to handle database conflicts? Duplicate names? Multiple primary keys?
#  2) Data visualisations? -- time on x-axis depicting frequency of actions
#  3) Create class to hold all functions

import yaml
import argparse
import sys
import psycopg2

def get_durations(dishes):
    """
    Generates a list which contains calculations of the total time required for each dish
    """
    # instantiate a list to hold the total duration required for each dish
    durations = []
    
    # loop through each dish, and write the total duration for the current dish
    # to durations
    for dish in dishes.keys():
        total_duration = 0

        # calculating the total duration for the current dish
        for step in dishes[dish].keys():
            if type(step) == int:
                total_duration += dishes[dish][step][0]

        # writing total duration for current dish to total_duration list
        durations.append(total_duration)

        # instantiating max duration variable
        max_duration = max(durations)

        # instantiating index of max duration in durations as a list
        # serves to identify which dish(es) requires the most time
        max_duration_idx = [i for i, v in enumerate(durations) if v == max_duration]

    return durations, max_duration, max_duration_idx


def assign_time(dishes):
    """
    Append start times to each dish
    """
    # iterate through dishes
    for i, k in enumerate(dishes.keys()):

        # flow control to select the dish(es) requiring the most time
        if i in max_duration_idx:

            # iterate through steps for the current dish
            for j, step in enumerate(dishes[k].keys()):

                # flow control to select the step to execute first
                if j == 0:

                    # write time 0 to the list for step zero for current dish
                    dishes[k][step].append(0)

                # flow control to select following steps
                elif type(step) == int:

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
                    start = durations[max_duration_idx[0]] - durations[i]

                    # write time to the list for step zero for the current dish
                    dishes[k][step].append(start)

                # flow control to select following steps
                elif type(step) == int:

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
            
            if type(step) == int:
                
                # extract step details (duration, instruction, point in time) for
                # current dish, and write to instrcutions list
                instructions.append(dishes[dish][step])

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
            epochs_d.update({e : (epochs_d[e]+1)})

        else:

            # create specific point in time as a dictionary key
            epochs_d[e] = 1

    return instructions, epochs, epochs_d

def concurrency(instructions, epochs_d, dishes):
    """
    Read output generated by oragnise_steps function and handle points in time 
    which require more than one action
    """
    # instantiate list to hold step description text for steps which occur at
    # the same point in time
    instruction_temp = []

    # instantiate list to hold all step details in order
    instructions_ordered = []

    # iterate through ordered points in time
    for i, e in enumerate(epochs_d.keys()):

        # flow control for points in time associated with multiple actions
        if epochs_d[e] > 1:

            # iterate over instructions holding all step details
            for instruction in instructions:

                # flow control to select steps in order
                if e == instruction[2]:

                    # extract step description text for all associated actions
                    instruction_temp.append(instruction[1])

                    # instantiate variable to hold all step details. variable is
                    # overwritten because the only important information is point
                    # in time
                    step_temp = instruction

            # append current step details to master step details list
            instructions_ordered.append(step_temp)

            # update step instruction to reflect all necessary actions
            instructions_ordered[i][1] = (' AND ').join(instruction_temp)

        # flow control for points in time associated with only one action
        else:

            # iterate through each list in instructions
            for instruction in instructions:

                # flow control to select steps in order
                if e == instruction[2]:

                    # write step lists to instructions_ordered in order of time
                    instructions_ordered.append(instruction)

    return instructions_ordered

def broadcast_instructions(epochs, epochs_d, instructions_ordered):
    """
    Print timings for various dishes
    """

    # instantiate variable to aid flow control so that proper timing instructions
    # are provided when multiple dishes are started at time zero
    z = 0
    for i in range(len(epochs)):
        if epochs[i] != 0:
            z = i
            break

    # iterate through points in time
    for i, p in enumerate(epochs_d.keys()):

        # iterate through ordered lists of details for all steps
        for instruction in instructions_ordered:

            # flow control to select list of details depending on point in time
            if instruction[2] == p:

                # flow control for first step (time zero)
                try:
                    
                    # flow control for concurrent first steps
                    if epochs[i+1] == 0:
                        
                        # flow control for current step durations which exceeds the
                        # following point in time
                        if instruction[0] > epochs[z]:

                            # print time until next step, and action to be taken
                            print('set timer for {:3} minutes » {}'\
                            .format(epochs[z], instruction[1]))

                        # flow control for all other durations
                        # instruction[0] < epochs[i+1]
                        else:

                            # print time until next step, and the action to be taken
                            print('set timer for {:3} minutes » {}'\
                            .format(epochs[i+1] - epochs[i], instruction[1]))

                    else:
                        # flow control for current step durations which exceeds the
                        # following point in time
                        if instruction[0] > epochs[i+1]:

                            # print time until next step, and action to be taken
                            print('set timer for {:3} minutes » {}'\
                            .format(epochs[i+1], instruction[1]))

                        # flow control for all other durations
                        # instruction[0] < epochs[i+1]
                        else:

                            # print time until next step, and the action to be taken
                            print('set timer for {:3} minutes » {}'\
                            .format(epochs[i+1] - epochs[i], instruction[1]))

                # flow control for after the final step
                except IndexError:
                    continue

    print('\nEnjoy!\n')

def write_db_entries(dishes_d):
    """
    Flatten each dish in dishes.yaml into a dictionary, and enter resulting
    dictionary into the persistent database
    """
    conn = psycopg2.connect(dbname='cooking', user='sean', host='localhost')
    cur = conn.cursor()

    for dish in dishes_d.keys():
        current_dish = {'dish_name': dish}   
        dish_durations = []
        dish_instructions = []
        z = 0

        for step in dishes[dish].keys():
            if type(step) == int:
                dish_durations.append(dishes[dish][step][0])
                dish_instructions.append(dishes[dish][step][1])
                z += dishes[dish][step][0]
            else:
                dish_description = dishes[dish][step]

        current_dish.update({'duration': dish_durations})
        current_dish.update({'total_duration': z})
        current_dish.update({'instructions': dish_instructions})
        current_dish.update({'description': dish_description})

        cur.execute("""
        INSERT INTO dishes (dish, duration, total_duration, instructions, description) 
        VALUES(%(dish_name)s, %(duration)s, %(total_duration)s, %(instructions)s, %(description)s)
        """, 
        current_dish)
        conn.commit()
    
    cur.close()
    conn.close()

def read_db_entries(dishes):
    """
    Combine all tuples produced by database query back into format resembling dishes.yaml
    """
    dishes_dict = {}
    for entry in dishes:
        dishes_dict.update({entry[0]: {}})
        
        for i, _ in enumerate(entry[3]):
            dishes_dict[entry[0]].update({i: []})
            dishes_dict[entry[0]][i].append(entry[2][i])
            dishes_dict[entry[0]][i].append(entry[3][i])
        dishes_dict[entry[0]].update({'description': entry[4]})

    return dishes_dict

# top-level scripting environment
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Chef planning assistant')

    parser.add_argument('-f', '--file', action='store_false', default=False,
                        help='create cooking plan using a specified yaml file')

    parser.add_argument('-r', '--reader', action='store_false', default=False,
                        help='create cooking plan using dishes.yaml')
    
    parser.add_argument('-s', '--selector', action='store_false', default=False,
                        help='create cooking plan using recipies existing in the \
                        persistent database')

    parser.add_argument('-w', '--writer', action='store_false', default=False,
                        help='write recipies from dishes.yaml to the \
                        persistent database')
    
    parser.add_argument('-fw', '-file writer', action='store_false', default=False,
                        help='write recipies from a specified yaml file to the \
                        persistent database')

    if '-h' in sys.argv[1:]:
        print(parser.parse_args())

    elif '-f' in sys.argv[1:]:

        if len(sys.argv) < 3:
            
            print('Please specify a file after the \'-f\' flag')

        else:

            dishes = yaml.load(open(sys.argv[2]))

            print('Reading all dishes from {}'.format(sys.argv[2])) 
            durations, max_duration, max_duration_idx = get_durations(dishes)
            dishes = assign_time(dishes)
            instructions, epochs, epochs_d = organise_steps(dishes)
            instructions_ordered = concurrency(instructions, epochs_d, dishes)
            broadcast_instructions(epochs, epochs_d, instructions_ordered)
        
    elif '-r' in sys.argv[1:]:

        dishes = yaml.load(open('dishes.yaml'))

        print('Reading all dishes from dishes.yaml.')
        durations, max_duration, max_duration_idx = get_durations(dishes)
        dishes = assign_time(dishes)
        instructions, epochs, epochs_d = organise_steps(dishes)
        instructions_ordered = concurrency(instructions, epochs_d, dishes)
        broadcast_instructions(epochs, epochs_d, instructions_ordered)

    # need code to ask if an existing dish should be overwritten, OR, if the current
    # dish can be renamed
    elif '-w' in sys.argv[1:]:
        
        dishes = yaml.load(open('dishes.yaml'))

        try:
            print('Writing all dishes to database.')
            write_db_entries(dishes)
            print('Done')

        except psycopg2.OperationalError:
            print('Cannot connect to the database.')

    elif '-fw' in sys.argv[1:]:
        
        if len(sys.argv) < 3:
            
            print('Please specify a file after the \'-fw\' flag')
        
        else:
            
            dishes = yaml.load(open(sys.argv[2]))

            try:

                print('Writing all dishes to database and providing instruction.')
                write_db_entries(dishes)

                durations, max_duration, max_duration_idx = get_durations(dishes)
                dishes = assign_time(dishes)
                instructions, epochs, epochs_d = organise_steps(dishes)
                instructions_ordered = concurrency(instructions, epochs_d, dishes)
                broadcast_instructions(epochs, epochs_d, instructions_ordered)

            except psycopg2.OperationalError:

                print('Cannot connect to the database.')
    
    elif '-s' in sys.argv[1:]:

        try:
            print('Select dishes to be prepared:\n')
            conn = psycopg2.connect(dbname='cooking', user='sean', host='localhost')
            cur = conn.cursor()

            db = {}
            cur.execute("SELECT * FROM dishes;")
            for i, dish in enumerate(cur.fetchall()):
                db.update({i:dish})
                print('{:2}'.format(i), db[i][1])
            
            conn.close()
            print()
            
            selection = input('Please provide the numbers of the dishes you would like to prepare, separated by spaces\n» ').split()
            selection = [int(num) for num in selection]
            
            for i, j in enumerate(selection):
                if i in db.keys():
                    selection[i] = db[j][1:]
                    # converting tuple structure to list
                    selection[i] = [item for item in selection[i]]

            print('Preparing {}'.format((', ').join([dish[0] for dish in selection])))

            selection = read_db_entries(selection)
            durations, max_duration, max_duration_idx = get_durations(selection)
            dishes = assign_time(selection)
            instructions, epochs, epochs_d = organise_steps(selection)
            instructions_ordered = concurrency(instructions, epochs_d, selection)
            broadcast_instructions(epochs, epochs_d, instructions_ordered)

        except psycopg2.OperationalError:
            print('Cannot connect to the database.')