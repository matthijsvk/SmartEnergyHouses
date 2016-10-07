For this project, we simulated the energy consumption of a home for one day, modeling different large-consumption devices like dishwashers, furnace, charging electric cars, lights, heating, and local power generation (solar and wind).

The purpose was to show how energy consumption fluctuates during the day, and to think about possible solutions for the problems this poses to the grid.

We had one computer set up with a python program running connected to a MySQL database. You could select which type of demo to show, and it would fetch the corresponding energy consumption data from the database.

This is for example at what time and for how long certain devices are turned on. To show the effects of this, we built a model house, with an arduino controlling mostly leds that represented the devices.

One arduino (the 'piper') was connected to the pc, and transmitted its data via bluetooth to the second one (SEH, Smart Energy house) which controlled the model house.
