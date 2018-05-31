# [The Report Of Our Death](https://glyph.twistedmatrix.com/2014/05/the-report-of-our-death.html)

*The report of Twisted’s death was an exaggeration.*

`Thursday May 08, 2014`


Lots of folks are very excited about the [Tulip project](https://code.google.com/p/tulip/), [recently released as the asyncio standard library module in Python 3.4](https://docs.python.org/3.4/whatsnew/3.4.html#whatsnew-asyncio).


This module is potentially exciting for two reasons:

1. It provides an abstract, language-blessed, standard interface for event-driven network I/O. This means that instead of every event-loop library out there having to [implement everything](http://tornado.readthedocs.org/en/latest/twisted.html) in terms of [every other event-loop library’s ideas](https://github.com/jyio/geventreactor) of how things work, each library can simply implement adapters from and to those standard interfaces. These interfaces substantially resemble the abstract [interfaces that Twisted has provided](https://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.html) for a long time, so it will be [relatively easy for us to adapt to them](https://github.com/itamarst/txtulip).

2. It provides a new, high-level [coroutine scheduler](http://legacy.python.org/dev/peps/pep-3156/#coroutines-and-the-scheduler), providing a slightly cleaned-up syntax (`return` works!) and more efficient implementation (no need for a manual [trampoline](https://en.wikipedia.org/wiki/Trampoline_%28computers%29), it’s built straight into the language runtime via yield from) of something like [inlineCallbacks](https://twistedmatrix.com/documents/13.2.0/api/twisted.internet.defer.inlineCallbacks.html).

However, in their understandable enthusiasm, some observers of Tulip’s progress – links withheld to protect the guilty – have been forecasting Twisted’s inevitable death, or at least its inevitable consignment to the dustbin of “legacy code”.

At first I thought that this was just sour grapes from people who disliked Twisted for some reason or other, but then I started hearing this as a concern from users who had enjoyed using Twisted.

So let me reassure you that the idea that Twisted is going away is totally wrong. I’ll explain how.

The logic that leads to this belief seems to go like this:


>Twisted is an async I/O thing, `asyncio` is an async I/O thing. Therefore they are the same kind of thing. I only need one kind of thing in each category of thing. Therefore I only need one of them, and the “standard” one is probably the better one to depend on. So I guess nobody will need Twisted any more!


The problem with this reasoning is that “an async I/O thing” is about as specific as “software that runs on a computer”. After all, Firefox is also “an async I/O thing” but I don’t think that anyone is forecasting the death of web browsers with the release of Python 3.4.

## Which Is Better: OpenOffice or Linux?

Let’s begin with the most enduring reason that Twisted is not going anywhere any time soon. `asyncio` is an implementation of a transport layer and an event-loop API; it can move bytes into and out of your application, it can schedule timed calls to happen at some point in the future, and it can start and stop. It’s also an implementation of a coroutine scheduler; it can interleave apparently sequential logic with [explicit](https://glyph.twistedmatrix.com/2014/02/unyielding.html) yield points. There are also some experimental third-party extension modules available, including [an event-driven HTTP server and client](https://pypi.python.org/pypi/aiohttp/0.6.5), and the community keeps building more stuff.

In other words, asyncio is a *kernel* for event-driven programming, with some applications starting to be developed.

Twisted is also an implementation of a transport layer and an event-loop API. It’s also got a coroutine scheduler, in the form of `inlineCallbacks`.

Twisted is also a production-quality event-driven [HTTP server and client](https://twistedmatrix.com/trac/wiki/TwistedWeb) including its own [event-driven templating engine](https://twisted.readthedocs.org/en/latest/web/howto/twisted-templates.html), with third-party HTTP addons including [server microframeworks](https://github.com/twisted/klein), [high-level client tools](https://github.com/dreid/treq), [API construction kits](http://haddock.atleastfornow.net/en/latest/intro.html#a-very-simple-example), [robust, two-way browser communication](https://pypi.python.org/pypi/txsockjs), and [automation for usually complex advanced security features](https://github.com/glyph/txsni).

Twisted is also an [SSH client](https://twisted.readthedocs.org/en/latest/conch/howto/conch_client.html), both an API and a command-line replacement for OpenSSH. It’s also an SSH server which I have heard [some people think is OK](http://www.slideshare.net/mwhudson/how-we-use-twisted-in-launchpad) to [use in production](https://twitter.com/nzoschke/status/285913791433146369). Again, the SSH server is both an API and again as a daemon replacement for OpenSSH. (I'd say "drop-in replacement" except that neither the client nor server can parse OpenSSH configuration files. [Yet](https://twistedmatrix.com/trac/ticket/3830).)

Twisted also has a [native, symmetric event-driven message-passing protocol](https://twisted.readthedocs.org/en/latest/core/howto/amp.html) designed to be [easy to implement](http://amp-protocol.net/) in [other languages and environments](http://amp-protocol.net/Implementations/), making it incredibly easy to develop a custom protocol to propagate real-time events through multiple components; clients, servers, embedded devices, [even web browsers](https://github.com/lvh/txampext).

Twisted is also a [chat server you can deploy with one shell command](https://twistedmatrix.com/trac/wiki/TwistedWords). Twisted is also a [construction kit for IRC bots](https://github.com/jessamynsmith/talkbackbot). Twisted is also an [XMPP client and server library](http://metajack.im/2008/09/25/an-xmpp-echo-bot-with-twisted-and-wokkel/). [Twisted is also a DNS server](https://twistedmatrix.com/trac/wiki/TwistedNames) and [event-driven DNS client](http://twisted.readthedocs.org/en/latest/names/howto/client-tour.html). Twisted is also a [multi-protocol integrated authentication API](http://twisted.readthedocs.org/en/latest/core/howto/cred.html). Twisted is also [a pluggable system for creating transports](http://twisted.readthedocs.org/en/latest/core/howto/endpoints.html#maximizing-the-return-on-your-endpoint-investment) to allow for third-party transport components to do things like [allow you to run as a TOR hidden service](https://txtorcon.readthedocs.org/en/latest/) with a single command-line switch and [no modifications to your code](https://twistedmatrix.com/pipermail/twisted-python/2014-May/028294.html).

Twisted is also a system for [processing streams of geolocation data](http://twisted.readthedocs.org/en/latest/core/howto/positioning.html) including [from real hardware devices, via serial port support](https://twistedmatrix.com/documents/13.2.0/api/twisted.internet.serialport.SerialPort.html).

Twisted also natively implements [GUI integration support for the Mac, Windows, and Linux](http://twisted.readthedocs.org/en/latest/core/howto/choosing-reactor.html?highlight=choosing#choosing-a-reactor-and-gui-toolkit-integration).

I could go on.

If I were to include what third-party modules are available as well, [I could go on at some considerable length](https://launchpad.net/tx).

The point is, while Twisted also has an existing kernel – largely compatible, at a conceptual level at least, with the way `asyncio` was designed – it also has a huge suite of functionality, both libraries and applications. Twisted is OpenOffice to `asyncio`’s Linux.

Of course this metaphor isn’t perfect. Of course the [nascent `asyncio` community](http://asyncio.org/) will come to supplant some of these things with other third-party tools. Of course there will be some duplication and some competing projects. That’s normal, and even healthy. But this is not a winner-take all existential Malthusian competition. Being able to leverage the existing functionality within the Twisted and Tornado ecosystems – and vice versa, allowing those ecosystems to leverage new things written with `asyncio` – was not an accident, it was an [explicit, documented design goal of asyncio](http://legacy.python.org/dev/peps/pep-3156/#interoperability).

## Now And Later

Python 3 is the future of Python.

While Twisted still has [a ways to go](https://twistedmatrix.com/trac/wiki/Plan/Python3) to finish porting to Python 3, you will be able to `pip install` the portions that already work as of the upcoming 14.0 release (which should be out any day now). So contrary to some incorrect impressions I’ve heard, the Twisted team is working to support that future.

(One of the odder things that I’ve heard people say about `asyncio` is that now that Python 3 has `asyncio`, porting Twisted is now unnecessary. I'm not sure that Twisted is necessary per se – our planet has been orbiting that [cursed orb](https://twistedmatrix.com/trac/ticket/5000) for over 4 billion years without Twisted’s help – but if you want to create an XMPP to IMAP gateway in Python it's not clear to me how having just `asyncio` is going to help.)

However, while Python 3 may be the future of Python, right now it is sadly just the future, and [not the present](http://alexgaynor.net/2014/jan/03/pypi-download-statistics/).

If you want to use `asyncio` today, that means foregoing the significant performance benefits of [pypy](http://pypy.org/). (Even the beta releases of pypy3, which still routinely segfault for me, only support the language version 3.2, so no “`yield from`” syntax.) It means cutting yourself off from a [significant](http://py3readiness.org/) (albeit gradually diminishing) subset of available Python libraries.

You could use the Python 2 backport of Tulip, [Trollius](https://warehouse.python.org/project/trollius/), but since idiomatic Tulip code relies heavily on the new `yield from` syntax, it’s possible to write code that works on both, [but not idiomatically](http://trollius.readthedocs.org/#write-code-working-on-trollius-and-tulip). Trollius actually works on Python 3 as well, but then you miss out on one of the real marquee features of Tulip.

Also, while Twisted has a [strict compatibility policy](https://twistedmatrix.com/trac/wiki/CompatibilityPolicy), `asyncio` is still marked as having [provisional status](https://docs.python.org/3.4/glossary.html#term-provisional-api), meaning that unlike the rest of the standard library, its API may change incompatibly in the next version of Python. While it’s unlikely that this will mean major changes for `asyncio`, since Python 3.4 was just released, it will be in this status for at least the next 18 months, until Python 3.5 arrives.

As opposed to the huge laundry list of functionality above, all of these reasons will eventually be invalidated, hopefully sooner rather than later; if these were the only reasons that Twisted were going to stick around, I would definitely be worried. However, they’re still reasons why today, even if you only need the pieces of an asynchronous I/O system that the new `asyncio` module offers, you still might want to choose Twisted’s core event loop APIs. Keep in mind that using Twisted today doesn’t cut you off from using `asyncio` in the future: far from it, it makes it likely that you will be able to easily integrate whatever new `asyncio` code you write once you adopt it. Twisted’s goal, as Laurens van Houtven eloquently explained it this year in a PyCon talk, is to [work with absolutely everything](http://pyvideo.org/video/2597/twisted-mixing), and that very definitely includes `asyncio` and Python 3.

## My Own Feelings

I feel like `asyncio` is a step forward for Python, and, despite the dire consequences some people seemed to expect, a tremendous potential *benefit* to Twisted.

For years, while we – the Twisted team – were trying to build the “engine of your Internet”, we were also having to make a constant, tedious sales pitch for the event-driven model of programming. Even today, we’re still stuck writing [rambling, digressive rants](https://glyph.twistedmatrix.com/2014/02/unyielding.html) explaining why you might not want three threads for every socket, giving [conference talks where we try to trick the audience into writing a callback](http://www.pyvideo.org/video/1681/so-easy-you-can-even-do-it-in-javascript-event-d), and trying to explain [basic stuff about networking protocols](https://thoughtstreams.io/glyph/your-game-doesnt-need-udp-yet/) to an unreceptive, frustrated audience.

This audience was unreceptive because the broader python community has been less than excited about event-driven networking and cooperative task coordination in general. It’s a vicious cycle: programmers think events look “unpythonic”, so they write their code to block. Other programmers then just want to make use of the libraries suitable to their task, and they find ones which couple (blocking) I/O together with basic data-processing tasks like parsing.

Oddly enough, I noticed a drop in the frequency that I needed to have this sort of argument once [node.js](http://nodejs.org/) started to gain some traction. Once server-side Python programmers started to hear all the time about how writing callbacks wasn't a totally crazy thing to be doing on the server, there was a whole other community to answer their questions about why that was.

With the advent of `asyncio`, there is functionality available in the standard library to make event-driven implementations of things immediately useful. Perhaps even more important this functionality, there is guidance on how to make your own event-driven stuff. Every module that is written using `asyncio` rather than `io` is a module that at least can be made to work natively within Twisted without rewriting or monkeypatching it.

In other words, this has shifted the burden of arguing that event-driven programming is a worthwhile thing to do *at all* from Twisted to a module in the language’s core.

While it’ll be quite a while before most Python programmers are able to use `asyncio` on a day to day basis its mere *existence* justifies the conceptual basis of Twisted to our core consituency of Python programmers who want to put an object on a network. Which, in turn, means that we can dedicate more of our energy to doing cool stuff with Twisted, and we can dedicate more of the time we spend educating people to explaining how to do cool things with all the crazy features Twisted provides rather than explaining why you would even want to write all these weird callbacks in the first place.

So Tulip is a good thing for Python, a good thing for Twisted, I’m glad it exists, and it doesn't make me worried at all about Twisted’s future.

Quite the opposite, in fact.