# battery sender

## Branch Description
This is the zero branch where development of the battery sender happens

## Future Work
This program may read command line data for setting the loglevel before the configuration file is read.

## Description
This daemon sends battery data onto the HAL network.

### MQTT Publishing
Each battery reading is published onto the network under the `run` topic.

Each time the `reporter/checkup_req` is received, cached data is published under the `checkup` topic

### Modbus Interface
The battery parameters span from
0 to 144 inclusive

Here is a table of the registers we use:
| FC 3 Register | Data |
|---------------|------------|
| 21 | State of Charge |
| 22 | Voltage |
| 113 | cell 0 |
| ... | ... |
| 128 | cell 15 |

## Dependencies
* [MAGLabPyLib](https://github.com/MAGLaboratory/MAGLabPyLib)  (included as a submodule)
* minimalmodbus

## Installation
(optional) Move files where appropriate:
* `MAGLabPyLib` may be installed using `pip install`
* `battery.py` may be installed in `/usr/local/bin/`
* `battery.json` may be installed in `/etc/`
* `battery.env` may be installed in the same location as the former

Modify the included `battery_sender.service` to your installation:
* where the python script is
* where the .env file is
* which user is running this script

Copy the `battery_sender.service` to `/usr/lib/systemd/system/` or where your distribution stores systemd scripts

## Help
Please do not hesitate to leave a Github issue or email the MAG Laboratory contact email: contact [at] maglaboratory [dot] org.
Our social media locations are on the website.

## Authors
* @blu006

## Version History
todo

## License
The Unlicense
