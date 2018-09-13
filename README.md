Cooking best practice involves planning such that all of your dishes finish at the same time. All of your food will be warm, and you have  time for washing up in otherwise idle moments.

This planning has been automated using Python. The program goes through each dish in the yaml file, reads how long each step requires in minutes, and determines at what points in time each step should be executed. Once all of the calculations are completed, the final instructions are printed to the console. Yaml files can also be imported into a database, and read by the application which eliminates the need to manage the yaml files.

Please feel free to contact me at sean.turner026@gmail.com if you have a feature request or other feedback.

### Dishes.yaml
```
---
Pasta:
  0: [16, 'Boil noodles']
  1: [3, 'Mix noodles with sauce']
  description: 'delish pasta'
  ingredients: ['16 oz noodles', '1 jar pesto']
  servings: 4

Salad:
  0 : [12, 'Make dressing']
  1 : [4, 'Toss salad']
  description: null
  ingredients: null
  servings: 3
  
Steak:
  0 : [16, 'Cook steak']
  description: null
  ingredients: null
  servings: null
```

### Usage

```
$ python cooking.py -h

Chef planning assistant

optional arguments:
  -h, --help                 show this help message and exit
  -f [], --file []           create cooking plan using a specified yaml file
  -r, --reader               create cooking plan using dishes.yaml
  -w, --writer               write recipies from dishes.yaml to the persistent
                             database
  -s, --selector             create cooking plan using recipies existing in the
                             persistent database
  -m [], --modifier []       modify all recipies in the persistent database by the
                             same name as in a specified yaml file
  -fw [], --file_writer []   write recipies from a specified yaml file to the
                             persistent database
```
```
$ python cooking.py -r
Reading all dishes from dishes.yaml. Your meal will require 19 minutes to prepare.

Pasta serves 4, and requires the following ingredients:
* 16 oz noodles
* 1 jar pesto
Salad serves 3 (ingredients not provided)
Steak (no serving information or ingredients provided)

INSTRUCTIONS:

Set timer for 2 minutes
» Pasta: Boil noodles

Set timer for 12 minutes
» Salad: Make dressing
» Steak: Cook steak

Set timer for 2 minutes
» Salad: Toss salad

» Set timer for 3 minutes.
Pasta: Mix noodles with sauce

All of your dishes should be finished. Enjoy!
```
```
$ python cooking.py -w
Writing all dishes from dishes.yaml to the database...
Wrote Pasta to the database
Wrote Salad to the database
Wrote Steak to the database

Done!
```
```
$ python cooking.py -s
Select dishes to be prepared:

 Id      Dish Name
  0      Salad
  1      Ramen
  2      Sausage
  3      Pasta
  4      Steak

Please provide the id numbers of the dishes you would like to prepare, separated by spaces.
» 3 4

Preparing Pasta, Steak. Your meal will require 19 minutes to prepare.

Pasta serves 4, and requires the following ingredients:
* 16 oz noodles
* 1 jar pesto
Steak serves 11 (ingredients not provided)

INSTRUCTIONS:

Set timer for 3 minutes
» Pasta: Boil noodles

Set timer for 13 minutes
» Steak: Cook steak

» Set timer for 3 minutes.
Pasta: Mix noodles with sauce

All of your dishes should be finished. Enjoy!
```
