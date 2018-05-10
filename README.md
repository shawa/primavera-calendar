# Primavera Sound 2018 Calendar Generator

This is a Python utility for generating an `.ics` file for the timetable on Primavera Sound's 2018 webpage. Recommended useage is to create a shared Google Calendar you and your pals can use to click 'attending' etc to coordinate bops.

## Setup

Ensure you have `pipenv` installed, then install dependencies

```
$ pipenv install
```

Then actiave the virtualenv

```
$ pipenv shell
```

Then run!

```
$ ./main.py
fetching day 1 of 7
parsed act: Sala Apolo, Ganges, 20:50-21:30
parsed act: La [2] de Apolo, The Men, 21:15-22:15
parsed act: Sala Apolo, Kelsey Lu, 22:00-22:50
fetching day 2 of 7
parsed act: Sala Apolo, Za!, 20:45-21:40
parsed act: Sala Apolo, The Sea and Cake, 22:00-23:00
fetching day 3 of 7
parsed act: Day Pro, Guano Padano, 11:50-12:20
parsed act: Day Pro, Any Other, 12:40-13:10
parsed act: Day Pro, Marion Harper, 13:30-14:00
   ...
```

You'll see a new `.ics` file in the current directory, which you can import into Calendar.app, Google Calendar etc.

Happy Primavering!
