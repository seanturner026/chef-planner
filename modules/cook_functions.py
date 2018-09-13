"""
cook_functions.py is indirectly called by main() in cooking.py and calls all of the functions
in cooking.py necessary to run the program from start to finish
"""

import functools
import sys

import psycopg2
import cooking as ck


def switch_decorator(func):
    """Flow control which passes args to decorated function"""
    @functools.wraps(func)
    def wrapper(args):
        """Provides arguments to decorated function if needed"""
        if func.__name__ in ['func_file', 'func_file_writer', 'func_modifier']:
            return func(args)
        return func()
    return wrapper


@switch_decorator
def func_file(args):
    """Calls function necessary to read a given yaml and produce the cooking plan"""
    dishes = ck.load_yaml(args.get('file'))
    durations, max_duration, max_duration_idx = ck.get_durations(dishes)
    print('Reading all dishes from {}. Your meal will require {} minutes to prepare.\n'
          .format(args.get('file'), max_duration))
    dishes = ck.assign_time(dishes, max_duration_idx, durations)
    instructions_ordered = ck.concurrency(*ck.organise_steps(dishes, max_duration))
    instructions_ordered = ck.combine_instructions(instructions_ordered, max_duration)
    ck.broadcast_details(dishes)
    ck.broadcast_instructions(instructions_ordered, max_duration)
    return None


@switch_decorator
def func_reader():
    """Calls functions necessary to read dishes.yaml and produce the cooking plan"""
    dishes = ck.load_yaml('dishes.yaml')
    durations, max_duration, max_duration_idx = ck.get_durations(dishes)
    print('Reading all dishes from dishes.yaml. Your meal will require {} minutes to prep.\n'
          .format(max_duration))
    dishes = ck.assign_time(dishes, max_duration_idx, durations)
    instructions_ordered = ck.concurrency(*ck.organise_steps(dishes, max_duration))
    instructions_ordered = ck.combine_instructions(instructions_ordered, max_duration)
    ck.broadcast_details(dishes)
    ck.broadcast_instructions(instructions_ordered, max_duration)
    return None


@switch_decorator
def func_writer():
    """Calls functions necessary to write any dishes from dishes.yaml to the database"""
    dishes = ck.load_yaml('dishes.yaml')
    try:
        conn = psycopg2.connect(dbname='cooking', user='sean', host='localhost')
        cur = conn.cursor()
    except psycopg2.OperationalError:
        print('Cannot connect to the database.')
        sys.exit(0)
    ck.db_duplication_check(dishes, cur)
    print('Writing all dishes from dishes.yaml to the database...')
    ck.write_db_entries(*ck.flatten_yaml(dishes), conn, cur)
    print('\nDone!')
    conn.close()
    cur.close()
    return None


@switch_decorator
def func_file_writer(args):
    """Calls functions necessary to write any dishes from a given yaml file to the database"""
    dishes = ck.load_yaml(args.get('file_writer'))
    try:
        conn = psycopg2.connect(dbname='cooking', user='sean', host='localhost')
        cur = conn.cursor()
    except psycopg2.OperationalError:
        print('Cannot connect to the database.')
        sys.exit(0)
    ck.db_duplication_check(dishes, cur)
    print('Writing all dishes from {} to the database...'.format(args.get('file_writer')))
    ck.write_db_entries(*ck.flatten_yaml(dishes), conn, cur)
    print('\nDone!')
    conn.close()
    cur.close()
    return None


@switch_decorator
def func_selector():
    """Calls functions necessary to select dishes from the database and output the cooking plan"""
    try:
        conn = psycopg2.connect(dbname='cooking', user='sean', host='localhost')
        cur = conn.cursor()
    except psycopg2.OperationalError:
        print('Cannot connect to the database.')
        sys.exit(0)
    print('Select dishes to be prepared:\n')
    print('{} {:^4} {}'.format(' Id', ' ', 'Dish Name'))
    items = ck.fetch_db(cur)
    selection = input('\nPlease provide the id numbers of the dishes you would '
                      'like to prepare, separated by spaces.\n» ').split()
    selection = [int(num) for num in selection]
    for i, selected in enumerate(selection):
        if i in items.keys():
            selection[i] = items[selected][1:]
            # converting tuple structure to list
            selection[i] = [item for item in selection[i]]
    selection = ck.read_db_entries(selection)
    durations, max_duration, max_duration_idx = ck.get_durations(selection)
    print('\nPreparing {}. Your meal will require {} minutes to prepare.\n'
          .format((', ').join([dish for dish in selection]), max_duration))
    selection = ck.assign_time(selection, max_duration_idx, durations)
    instructions_ordered = ck.concurrency(*ck.organise_steps(selection, max_duration))
    instructions_ordered = ck.combine_instructions(instructions_ordered, max_duration)
    ck.broadcast_details(selection)
    ck.broadcast_instructions(instructions_ordered, max_duration)
    conn.close()
    cur.close()
    return None


@switch_decorator
def func_modifier(args):
    """Calls all functions necessary to modifies dishes in the database to reflect the dishes with
    the same name in the given yaml file
    """
    try:
        conn = psycopg2.connect(dbname='cooking', user='sean', host='localhost')
        cur = conn.cursor()
    except psycopg2.OperationalError:
        print('Cannot connect to the database.')
        sys.exit(0)
    dishes_modified = ck.load_yaml(args.get('modifier'))
    dishes_flat = ck.flatten_yaml(dishes_modified)
    dishes_flat = ck.fetch_dish_id(dishes_flat, cur)
    print('The following dish(es) will be modified to match the contents of modify.yaml:')
    for dish in dishes_flat:
        print('* {}'.format(dish))
    confirmation = input('\nProceed? (y/n) > ')
    if confirmation == 'y':
        ck.update_db(dishes_flat, conn, cur)

    elif confirmation == 'n':
        print('Database will not be updated')

    else:
        print('Please input the letters y or n.')

    conn.close()
    cur.close()
    return None
