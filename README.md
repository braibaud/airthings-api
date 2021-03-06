# airthings-api
## Description

Python Wrappers for AirThings API

## Installation

* Package published at https://pypi.org/project/airthings-api/
* Install package: `pip install -i airthings-api`

## Usage (Jupyter)

> NB: You can now use async/await at the top level in the IPython terminal and in the notebook, it should — in most of the cases — “just work”. Update IPython to version 7+, IPykernel to version 5+.

```python
# import the library
ata = __import__('airthings-api')
import aiohttp

session = aiohttp.ClientSession()

# Create an API manager; use your dashboard's credentials
manager = ata.api.web.AirThingsManager(
    username='jdoe@gmail.com', 
    password='xxxxxxxx',
    session=session) 

# Get the 'me' instance
me = await manager.get_me_instance()

print(me.email)
# Should be 'jdoe@gmail.com' I guess

# Get the 'locations' instances
locations_instance = await manager.get_locations_instance()

# Print devices and sensor values
for location in locations_instance.locations:
    for device in location.devices:
        print('device: {0}'.format(device.room_name))
        
        for current_sensor_value in device.current_sensor_values:
            print('  {0}: {1} {2}'.format(
                current_sensor_value.type_,
                current_sensor_value.value,
                current_sensor_value.provided_unit))

await session.close()

# device: Wave Mini
#   temp: 21.6 c
#   humidity: 41.0 pct
#   voc: 253.0 ppb
#   mold: 0.0 riskIndex
# device: Wave
#   radonShortTermAvg: 103.0 bq
#   temp: 20.5 c
#   humidity: 47.0 pct
# device: Hub AirThings
```

## Usage (Python file)

> NB: If you run in a Python file, wrapping the call within `asyncio.run(...)` will do the trick.

```python
ata = __import__('airthings-api')
import aiohttp
import asyncio


async def test():

    session = aiohttp.ClientSession()

    # Create an API manager; use your dashboard's credentials
    manager = ata.api.web.AirThingsManager(
        username='jdoe@gmail.com', 
        password='xxxxxxxx',
        session=session) 

    # Get the 'me' instance
    me = await manager.get_me_instance()

    print(me.email)
    # Should be 'jdoe@gmail.com' I guess

    # Get the 'locations' instances
    locations_instance = await manager.get_locations_instance()

    # Print devices and sensor values
    for location in locations_instance.locations:
        for device in location.devices:
            print('device: {0}'.format(device.room_name))
            
            for current_sensor_value in device.current_sensor_values:
                print('  {0}: {1} {2}'.format(
                    current_sensor_value.type_,
                    current_sensor_value.value,
                    current_sensor_value.provided_unit))

    await session.close()

    # device: Wave Mini
    #   temp: 21.6 c
    #   humidity: 41.0 pct
    #   voc: 253.0 ppb
    #   mold: 0.0 riskIndex
    # device: Wave
    #   radonShortTermAvg: 103.0 bq
    #   temp: 20.5 c
    #   humidity: 47.0 pct
    # device: Hub AirThings


if __name__ == '__main__':

    asyncio.run(test())
```
