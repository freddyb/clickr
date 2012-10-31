*clickr* is an smpt server that pretends to store e-mails for any user
but then just clicks URLs that look like account-verification links
and does not store the e-mail afterwards.
The sending mailserver will get a "delivery in progress" response, so
that it will be unaware of the mail being dropped.
*clickr* depends on twisted_'s smtp implementation.

.. _twisted: http://twistedmatrix.com


Setup
============

1) get a free domain afraid.org (great freedns!) and point it's MX record to your host.
2) now start *clickr* using ``twistd -ny main.py`` (leave out -n for it to daemonize. no console output then).
3) *clickr* will now accept all e-mails it is getting and follow the URLs in it that contain some sort of token or one of the words "confirm" and "verify".


Known Bugs / TODO
=================

* most web sites require a valid session when following the confirmation link :( this prevents clickr from being awesome
* sporadic test coverage
* debug prints could be more tidy/beautiful


Licensing
============
* do whatever you want
* I don't mind if you credit me, in case you use this for something of major purpose


