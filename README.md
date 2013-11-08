smsgateway
==========

The SMS Gateway Server is an application that runs a HTTPS server that accepts requests to send SMS messages. The messages are queued by the application and sent by writing AT commands to a GSM modem (or handset) that is connected to the computer.

The web server provides a HTML form for sending SMS messages which allows shared access to message sending, but is also intended for applications/scripts to be able to send SMS messages.

The SMS Gateway Server is written for Python 2.7. It uses WSGI as webserver and pyGSM for the serial port connectivity. 

the server is optimised to use minimume resources, perfect to use in embaded systems with very limited resources. the server is secured using using SSL certificats, and allows the to store all activities on a log file and store all the SMS that have been sent on a database serevr.
