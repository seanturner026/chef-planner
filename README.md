Cooking best practice involves planning such that all of your dishes finish at the same time. All of your food will be warm, and you have  time for washing up in otherwise idle moments. 

This planning has been automated using Python. The program goes through each dish in the yaml file, reads how long each step requires in minutes, and determines at what points in time each step should be executed. Once all of the calculations are completed, the final instructions are printed to the console.

### Dishes.yaml
```
{
  'Pasta':
    {
      0 : [16, 'Boil pasta'],
      1 : [3, 'Mix Pasta with Sauce'],
      'description':null
    },

  'Salad':
    {
      0 : [12, 'Make dressing'],
      1 : [4, 'Toss salad'],
      'description':null
    },

  'Steak':
    {
      0 : [16, 'Cook steak'],
      'description':null
    }
}
```

### Usage

```
python cooking.py -h

Chef planning assistant

optional arguments:
  -h, --help         show this help message and exit
  -f, --file         create cooking plan using a specified yaml file
  -r, --reader       create cooking plan using dishes.yaml
  -s, --selector     create cooking plan using recipies existing in the
                     persistent database
  -w, --writer       write recipies from dishes.yaml to the persistent
                     database
  -fw, -file writer  write recipies from a specified yaml file to the
                     persistent database
```
```
python cooking.py -r
Reading all dishes from dishes.yaml. Your meal will require 19 minutes to prepare
set timer for   3 minutes » Boil pasta
set timer for  12 minutes » Make dressing AND Cook steak
set timer for   1 minutes » Toss salad
set timer for   3 minutes » Mix Pasta with Sauce

Enjoy!
```
```
python cooking.py -w
Writing all dishes from dishes.yaml to the database...
Wrote Pasta to the database
Wrote Salad to the database
Wrote Steak to the database

Done!
```
```
python cooking.py -s
Select dishes to be prepared:

Id Dish Name
 0 Pasta
 1 Salad
 2 Steak

Please provide the numbers of the dishes you would like to prepare, separated by spaces
» 0 1 2

Preparing Pasta, Salad, Steak. Your meal will require 19 minutes to prepare
set timer for   3 minutes » Boil pasta
set timer for  12 minutes » Make dressing AND Cook steak
set timer for   1 minutes » Toss salad
set timer for   3 minutes » Mix Pasta with Sauce

Enjoy!
```
