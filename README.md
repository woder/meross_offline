# Meross_Offline
A library for integrating Meross devices that are on MQTT directly.

Requires the MerossIOT library to be installed. To ensure compatibility with this code use the forked version found here https://github.com/woder/MerossIot


## Basic setup
To setup this plugin just add it to the custom_components under a folder "meross_offline". Ensure you setup each device using the great meross_powermon tool: https://github.com/davidb24v/meross-powermon

Copy the device config file it generates into the config.json file found at the root of this plugin. Ensure to add the ca.crt certificate that you used to setup the MQTT server to the plugin directory, and to specify
the path to this file within the config.json file. The plugin will then make all of the entities you specified in the config.json and register them within Home Assistant. 

## More information
For more information, check out the blog post on how I managed to use my Meross Devices offline: https://wltd.org
