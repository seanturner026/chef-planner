## Database has columns dish, duration, and steps

|dish         |duration |tot_duration|instructions               |
|:------------|:--------|:-----------|:--------------------------|
|Salad        |[12,4]   |16          |[Make dressing, Toss salad]|


## transform yaml to database format

    d = {
        ['dish_name', duration_list, steps_list]
        ['dish_name', duration_list, steps_list]
    }
    
## write to db

    • write duration values to a list
    • write step values to a list 
    • write total duration

### change column types in database to accommodate lists

### reorder database columns


### lining up output

    Figure out how to print » at col 27 e.g.:
    set timer for 333 minutes »
    set timer for 33 minutes  »

### connect to postgres database

    psql cooking
    \c cooking
    SELECT * FROM dishes;

### add a desc key to each dish, have the selector display this text from the database 