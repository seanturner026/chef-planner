# TODO:
#  1) Add functionality allowing instructions to be downloadable for future use
#  2) Add try except statements so app is more user friendly
#  3) Add functionality so that steps occuring at the same point in time are
    # properly accounted for in final for loop --> SOLUTION: iterate through the
    # point in time component of instructions_final, and count how many times
    # each value appears. Then a matter of a simple if statement that accounts
    # for points in time which require multiple actions
#  4) Potentially make epochs a dictionary. Keys would be point in time, values
    # would be the frequency of each point in time. This will affect the
    # creation of instructions_final list

# instantiating dict to hold dishes and corresponding steps + instructions
dishes = {}

# instantiate dish names list
print('What are the name(s) of you dishes? e.g. Pasta, Salad')
dish_names = input('> ').split(', ')

# instantiate each dish as keys, with dict of instruction and duration as values
for dish in dish_names:

    # instantiate the number of states for the current dish
    print('How many steps does {} have?'.format(dish))
    step_count = int(input('> '))

    # instantiate a list to hold a list of instruction + duration for each step
    steps = []

    # loop through steps and write each step's instruction + duration as a list
    for step in range(step_count):

        # define instruction for the current step
        print('What is step {}?'.format(str(step + 1)))
        description = input('> ')

        # define duration for the current step
        print('How many minutes does this step take?')
        duration = int(input('> '))

        # write duration + instruction for the current step as a list
        steps.append([duration, description])

    # instantiate a dictionary to hold the step number as keys, and a list of
    # the step instruction and duration as values
    d = {}

    # loop through steps, and write the step number and step
    # instruction and duration to d
    for step, step_num in zip(steps, range(len(steps))):
        d.update({step_num: step})

    # update original dishes dict with current dish
    dishes.update({dish: d})

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

# instantiate list to hold all step details (duration, instruction,
# point in time) and list to hold points in time that require action
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

print()

# instantiate list to hold all step details in order
instructions_final = []

# iterate through ordered points in time
for e in epochs:

    # iterate through each list in instructions
    for i in instructions:

        # flow control to select steps in order
        if e == i[2]:

            # write step lists to instructions_final in order of time
            instructions_final.append(i)

# debug use only
# print()
# print(epochs)
# print(instructions_final)

# iterate through points in time
for i, t in enumerate(epochs):

    # iterate through ordered lists of details for all steps
    for instruction in instructions_final:

        # flow control to select list of details depending on point in time
        if instruction[2] == t:

            # flow control for first step (time zero)
            try:

                # flow control for current step durations which exceeds the
                # following point in time
                if instruction[0] > epochs[i+1]:

                    # print time until next step, and action to be taken
                    print('set timer for {} minutes --> {}'\
                    .format(epochs[i+1], instruction[1]))

                # elif instruction[0] == epochs[i+1]:

                # flow control for all other durations
                # instruction[0] < epochs[i+1]
                else:

                    # print time until next step, and the action to be taken
                    print('set timer for {} minutes --> {}'\
                    .format(epochs[i+1] - epochs[i], instruction[1]))

            # flow control for the final step
            except IndexError:
                print('set timer for {} minutes --> {}'\
                .format(instruction[0], instruction[1]))

        # else:

print('\nEnjoy!\n')
