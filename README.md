Cooking best practice involves planning such that all of your dishes finish at the same time. This is great because your food will be warm, and you have some time for washing up in otherwise idle moments. This planning has been automated using Python. The yaml file provides the program with dishes, and for each dish, how long each step requires in minutes, and the description of each step. The program then figures out at what points in time each step should be done.


### Useage

```
python cooking.py -h

optional arguments:
  -h, --help         show this help message and exit
  -s, --selector     select from existing recipies from persistent database (not currently implemented)
  -r, --reader       reads and plans using recipies from dishes.yaml
  -w, --writer       write recipies to persistent database
  -rw, -read/writer  reads and plans using recipies from dishes.yaml, and
                     writes to persistent database
```
```
python cooking.py -r

Reading all dishes from dishes.yaml.
set timer for   3 minutes » Boil pasta
set timer for   3 minutes » Make dressing AND Cook steak
set timer for  12 minutes » Toss salad
set timer for   1 minutes » Mix Pasta with Sauce

Enjoy!
```
