##Rental property finder

This application scrapes a website for the address and cost per week. Then it will use the address to calculate the distance between the rental property, work and school. Using this data it will then select the closest property to work and school. The weighting of being closer to work or school is defined by the WORK_PRIORITY global variable.

##Get working

To get this application working you will need a [Google Maps Directions API](https://developers.google.com/maps/documentation/geocoding/intro) key along with a [Google Maps Geocoding API](https://developers.google.com/maps/documentation/directions/) key.

##Setting school and work locations

Set the WORK and SCHOOL variables to a string that Google can recognize as a location. A good format for this is "<SUBURB> <STATE> <POSTCODE>".

##Choosing to find closer to work, or school?

To find properties closer to work you can set the WORK_PRIORITY variable closer to 1. By setting WORK_PRIORITY closer to 0 it will find properties closer to school.
