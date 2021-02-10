# speed-glass

`speed-glass` is a lightweight pythontool to circumvent the rather patience-straining UI of a the commonly used [Telekom Speedport series](https://www.telekom.de/hilfe/geraete-zubehoer/router/speedport-smart "Telekom Speedport series").

Its primary goals are to assess the operational status of the device and to list hosts known to it in a timely manner.

## motivation

The speedports UI appears to encourage the user not to use, let alone buy another speedport-related device.
Only one user can access the devices admin-panel at once,
the UI looses its knowledge about this one user every once in a while;
it's poorly designed and using it in multiple browser tabs fails to recognize the user as only one user.
Adding the poor response times of the webserver, its a hassle of about half a minute to list all current network devices;
and anotherone to recognize devices one searches for.

This CLI-tool helps to identify network devices and is more reliable than the browser UI,
even if the speedport is under load.

## usage

`speed-glass` has currently two modes.
The first does not require a login and is called using `speed-glass --info`, which returns every info available without credentials including internet connection status and bandwidth, if unlocked.

The second one is a dhcp glass, which lists current as well as still known, but gone devices, which have either still a valid lease or a static assignment.
Legacy IP is supported, as well as info about how the devices are connected (wired, 2.4- or 5GHz).

For now, calling `speed-glass` gives the currently fatest possible glance over your network using these routers.

## passwords

There is no option to give the password via commandline-parameters in order to preserve users to log it in their history, too easily.

If one still wants the comfort of not entering it any time one'd like to assess the network, use of a password file is encouraged; as well as it is to use some sort of disk- or home-encryption.

However. This tool looms for a file called `.speedport_password` in the current directory, or in `~/.config/speedport/.password`, as fallback.

The contents of this file are simply the password in the first line of the file; an example is provided in `.speedport_password.example`.

## requirements

This tool uses features of python 3.4, as well as the library [requests](https://pypi.org/project/requests/ "requests").

## development

Ideas and bugreports are welcome, please use the issues instead of email.

I do not have a vast amount of speedports lying around, the codebase is developed against 'speedport smart' devices:
starting at firmware revision `050129.3.5.006.0`, which is available on their [firmwarepage](http://https://www.telekom.de/hilfe/geraete-zubehoer/router/speedport-smart/firmware-speedport-smart "firmwarepage").

The codebase runs at least until python 3.9.1.

Feedback regarding compatibility to other devices or firmware revisions is appreciated.

## Known issues

The current firmware (as well as a ton of others before it) has a concatenation issue in JSON-files,
where it builds invalid JSON using a trailing comma after the last array element.
As soon as that's gone, the regex hack which reformats it since c2d1681ebf972765caeef43f09ba180451398d5c will be as well.
