Cooking best practice involves planning such that all of your dishes finish at the same time. This is great because your food will be warm, and you have some time for washing up in otherwise idle moments. This planning has been automated using Python. The yaml file provides the program with dishes, and for each dish, how long each step requires in minutes, and the description of each step. The program then figures out at what points in time each step should be done.

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
      # added to showcase flow control for steps which occur simultaneously
      0 : [16, 'Cook steak'],
      'description':null
    }
}
```

### Useage

```
python cooking.py -h

Chef planning assistant

optional arguments:
  -h, --help         show this help message and exit
  -f, --file         read and plan using recipies from a specific yaml file
  -r, --reader       read and plan using recipies from dishes.yaml
  -s, --selector     create cooking plan from existing recipies in persistent
                     database
  -w, --writer       write recipies from dishes.yaml to the persistent
                     database
  -fw, -file writer  write recipies from a specific yaml file to the
                     persistent database
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
