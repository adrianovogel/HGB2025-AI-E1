# Exercise 2 - Jonas Gstöttenmayr

## Activitiy 1

### TODO!

## Activity 2

### A2 - Part 1

Monolith with a DB, running in docker on our lockal office server.

We can even use docker swarm, which would be a bit overkill but it could automatically restart the servie if it failed, though I would not recommend that.

As the volume, variety and velocity are very low, the best solution is most often the simplest one.
Simply store and query the PostgressSQL DB, no need for anything fancy.
This can all be done with one application or script in this case.

This solution will make debuging very easy and with the velocity and volumne that we won't have to worry for scaling for quite some time.
Any more complexity would simply cost compute power.

### A2 - Part 2

See the "temperature_data_consumer.py".

### A2 - Part 3

The implimentation is as resource efficient as it can get.
It simply queries the DB for the 10 last entries.

It is quite operable as it simply needs to be started and if it were to actually crash restarted.

The deployment complextiy is minimal as we can simple put it into a container and start the container.

The application outputs to the console so simply checking if the output is not an error is enough for the monitoring, we can even modify the script to send a message in case of an error.

## Activiy 3 

# TODO!