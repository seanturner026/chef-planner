Cooking best practice involves planning such that all of your dishes finish at the same time. All of your food will be warm, and you have  time for washing up in otherwise idle moments.

This planning has been automated using Python. The program goes through each dish in the yaml file, reads how long each step requires in minutes, and determines at what points in time each step should be executed. Once all of the calculations are completed, the final instructions are printed to the console.

### Dishes.yaml
```yaml
Salad:
  description: "some salad"
  ingredients:
    - ingredient: salad
      quantity_with_units: 1 bag
  servings: 3
  steps:
    0:
      duration: 12
      instruction: Make dressing
    1:
      duration: 4
      instruction: Toss salad

Pasta:
  description: "delish pasta"
  ingredients:
    - ingredient: noodles
      quantity_with_units: 16 oz
    - ingredient: pesto
      quantity_with_units: 1 jar
  servings: 4
  steps:
    0:
      duration: 16
      instruction: Boil noodles
    1:
      duration: 3
      instruction: Mix noodles with sauce

Steak:
  description: "STEAK"
  ingredients:
    - ingredient: ny strip
      quantity_with_units: 1 kg
  servings: 4
  steps:
    0:
      duration: 16
      instruction: Cook steak
```

### Usage

```
$ python3 cooking.py --help

Usage: cooking.py [OPTIONS]

Options:
  -r, --reader    create cooking plan using dishes.yaml
  -w, --writer    write recipies from dishes.yaml to the persistent database
  -s, --selector  create cooking plan using recipies existing in the
                  persistent database

  -m, --modifier  modify all recipies in the persistent database by the same
                  name as in a specified yaml file

  --help          Show this message and exit.
```
```
$ python3 cooking.py -r
Reading all dishes from dishes.yaml. Your meal will require 19 minutes to prep.

Salad serves 3, and requires the following ingredients:
* salad, 1 bag
Pasta serves 4, and requires the following ingredients:
* noodles, 16 oz
* pesto, 1 jar
Steak serves 4, and requires the following ingredients:
* ny strip, 1 kg

INSTRUCTIONS:

Set timer for 3 minutes
» Pasta: Boil noodles

Set timer for 12 minutes
» Salad: Make dressing
» Steak: Cook steak

Set timer for 1 minutes
» Salad: Toss salad

Set timer for 3 minutes.
» Pasta: Mix noodles with sauce

All of your dishes should be finished. Enjoy!
```
