"""
module docstring
"""

# TODO:
#  1) Add functionality which asks User for yaml file name to allow User to have
    # access to multiple meals
#  2) Adjust output to be neater in that text always starts at the same
    # position. e.g. Account for ints of different length. --> if mins > 10: 
    # print('xyz') vs print(' xyz')
#  3) Add persistent volume which records recepies for future use
#  4) Add argparse functionality to all application to start by utilising recepies
    # saved in persistent volume
#  5) Add code to prevent print help, and reninstantiate sys.args when incorrect
    # arg is provided
#  6) How to handle database conflicts?
#  7) Add code to instantiate a database if one doesn't exist?

import yaml
import argparse
import sys
import psycopg2

parser = argparse.ArgumentParser(description='Chef planning assistant')

parser.add_argument('-w', '--writer', action='store_false', default=False,
                    help='write recipies to persistent database')

parser.add_argument('-s', '--selector', action='store_false', default=False,
                    help='select from existing recipies')

# load in instructions for all dishes to be prepared
dishes = yaml.load(open('dishes.yaml'))

# database has columns dish, duration, and steps

def get_durations(dishes):
    """
    Generates a list which contains calculations of the total time required for each dish
    """
    # instantiate a list to hold the total duration required for each dish
    duration_list = []
    
    # loop through each dish, and write the total duration for the current dish
    # to duration_list
    for dish in dishes.keys():
        total_duration = 0

        # calculating the total duration for the current dish
        for step in dishes[dish].keys():
            total_duration += dishes[dish][step][0]

        # writing total duration for current dish to total_duration list
        duration_list.append(total_duration)

        # instantiating max duration variable
        max_duration = max(duration_list)

        # instantiating index of max duration in duration_list
        # serves to identify which dish requires the most time
        max_duration_idx = duration_list.index(max_duration)

    return duration_list, max_duration, max_duration_idx


def assign_time(dishes):
    """
    Append start times to each dish
    """
    # iterate through dishes
    for i, k in enumerate(dishes.keys()):

        # flow control to select the dish requiring the most time
        if i == max_duration_idx:

            # iterate through steps for the current dish
            for j, step in enumerate(dishes[k].keys()):

                # flow control to select the step to execute first
                if j == 0:

                    # write time 0 to the list for step zero for current dish
                    dishes[k][step].append(0)

                # flow control to select following steps
                else:

                    # instantiate variable to hold current point in time after
                    # all preceeding steps have been executed
                    start_val = dishes[k][step - 1][0] + dishes[k][step - 1][2]

                    # write current point in time to current step for current dish
                    dishes[k][step].append(start_val)

        # flow control for all other dishes
        else:

            # iterate through steps for the current dish
            for j, step in enumerate(dishes[k].keys()):

                # flow control to select the step to execute first
                if j == 0:

                    # instantiate variable to hold point in time when the dish
                    # should be started
                    start_val = duration_list[max_duration_idx] - duration_list[i]

                    # write time to the list for step zero for the current dish
                    dishes[k][step].append(start_val)

                # flow control to select following steps
                else:

                    # instantiate variable to hold current point in time after
                    # all preceeding steps have been executed
                    start_val = dishes[k][step - 1][0] + dishes[k][step - 1][2]

                    # write current point in time to current step for current dish
                    dishes[k][step].append(start_val)

    return dishes

def organise_steps(dishes):
    """
    instantiate list to hold all step details (duration, instruction,
    point in time) and list to hold points in time that require action
    """
    instructions, epochs = [], []

    # iterate through dishes
    for dish in dishes.keys():

        # iterate through steps
        for step in dishes[dish].keys():

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
    for i, e in enumerate(epochs):

        # flow control to see if a particular point in time already exists
        if e in epochs_d.keys():

            # increase point in time frequency by one
            epochs_d.update({e : (epochs_d[e] + 1)})

        else:

            # create specific point in time as a dictionary key
            epochs_d[e] = 1

    return instructions, epochs, epochs_d

def parallel_timings(instructions, epochs_d, dishes):

    # instantiate list to hold step description text for steps which occur at
    # the same point in time
    instruction_temp = []

    # instantiate list to hold all step details in order
    instructions_final = []

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
            instructions_final.append(step_temp)

            # update step instruction to reflect all necessary actions
            instructions_final[i][1] = (' AND ').join(instruction_temp)

        # flow control for points in time associated with only one action
        else:

            # iterate through each list in instructions
            for instruction in instructions:

                # flow control to select steps in order
                if e == instruction[2]:

                    # write step lists to instructions_final in order of time
                    instructions_final.append(instruction)
                    
    return instructions_final

def broadcast_instructions(epochs, epochs_d, instructions_final):
    """
    Print timings for various dishes
    """
    # iterate through points in time
    for i, (t, p) in enumerate(zip(epochs, epochs_d.keys())):

        # iterate through ordered lists of details for all steps
        for instruction in instructions_final:

            # flow control to select list of details depending on point in time
            if instruction[2] == p:

                # flow control for first step (time zero)
                try:

                    # flow control for current step durations which exceeds the
                    # following point in time
                    if instruction[0] > epochs[i + 1]:

                        # print time until next step, and action to be taken
                        print('set timer for {} minutes --> {}'\
                        .format(epochs[i+1], instruction[1]))

                    # flow control for all other durations
                    # instruction[0] < epochs[i+1]
                    else:

                        # print time until next step, and the action to be taken
                        print('set timer for {} minutes --> {}'\
                        .format(epochs[i+1] - epochs[i], instruction[1]))

                # flow control for after the final step
                except IndexError:
                    continue

    print('\nEnjoy!\n')

if __name__ == "__main__":
    # should -h ask for new arguments 
    if '-h' in sys.argv[1:]:
        print(parser.parse_args())
    # need code to ask if an existing dish should be overwritten, OR, if the current
    # dish can be renamed
    elif '-w' in sys.argv[1:]:

        try:    
            print('Writing all dishes to database.')
            conn = psycopg2.connect(dbname='cooking', user='sean', host='localhost')
            cur = conn.cursor()
            duration_list, max_duration, max_duration_idx = get_durations(dishes)
            dishes = assign_time(dishes)
            instructions, epochs, epochs_d = organise_steps(dishes)
            instructions_final = parallel_timings(instructions, epochs_d, dishes)
            broadcast_instructions(epochs, epochs_d, instructions_final)

        except psycopg2.OperationalError:
            print('Cannot connect to the database.')

    elif '-s' in sys.argv[1:]:
        print('Select dishes to be prepared')