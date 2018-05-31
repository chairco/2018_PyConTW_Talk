# [The Report Of Our Death](https://glyph.twistedmatrix.com/2014/05/the-report-of-our-death.html)

*報導 Twisted 已死是誇大不實的*

`2014年5月8日 星期四`


許多人非常期待[鬱金香專案](https://code.google.com/p/tulip/), [它即將發佈成為 Python 3.4 內 asyncio 的標準模組](https://docs.python.org/3.4/whatsnew/3.4.html#whatsnew-asyncio).

這個模組讓人興奮有兩個原因:

1. 它提供一個摘要，language-blessed，標準的事件導向網路 I/O 介面。這意味者不是每個 event-loop 函式庫都需要去[實現所有事](http://tornado.readthedocs.org/en/latest/twisted.html)單就如何運作，[其他 event-loop 函式庫的思路](https://github.com/jyio/geventreactor), 每個函式庫都可以簡單地實現適用於這後標準介面的連接。很長一段時間，這些介面基本上與 [Twisted 所提供的抽象介面很類似](https://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.html)，所以對我們[相對而言相會容易適應](https://github.com/itamarst/txtulip).


2. 它提供一個全新，high-level [coroutine scheduler](http://legacy.python.org/dev/peps/pep-3156/#coroutines-and-the-scheduler)，也提供一些更簡潔的語法 (`return` works!) 以及更有效的建置 (不需要手冊 [trampoline](https://en.wikipedia.org/wiki/Trampoline_%28computers%29)，語言平台上建構，直接透過 yield from) 類似的東西像是 [inlineCallbacks](https://twistedmatrix.com/documents/13.2.0/api/twisted.internet.defer.inlineCallbacks.html).


然而，在熱情的理解中，一些關注鬱金香專案進展的朋友 - 拒絕保留一些相關缺失 - 不斷去預報 Twisted 未來將不可避免的被取代，或最終被遺棄到 “legac code” 的垃圾箱內。


剛開始，我以為這些人只是幾有某些理由對 Twisted 的酸葡萄心理，但後來我開始將這些聲音當作喜愛 Twisted 的關注。


所以讓我向你保證，Twisted 將離開這件事是真的搞錯了。接下來讓我解釋。


導致這個想法的邏輯應該會像這樣:


>Twisted 是用來處理 async I/O 這些事，`asyncio` 也是用來處理 async I/O 的事。因此他們有同樣的目的。我只需要不同種類中的一類。因此我只需要一種，而“標準”應該會是一個比較好的選項。所以我猜測沒有人會再需要 Twisted!


這個推理的原因在於 “async I/O 這件事”具體上與“運作一台電腦上的軟體”有關。畢竟，Firefox 也是“一個 async I/O 的事”，但我不認為會有任何預告當 Python 3.4 發佈之後 Web 瀏覽器就會隨之死亡。


## 哪個比較好: OpenOffice or Linux?

讓我們開始從為何 Twisted 在未來仍會繼續的理由。`asyncio` 是一個傳輸層以及 event-loop API 地實作;可以將 bytes 在你的應用程序中移進移出，可以排程某個未來呼叫的時間點。同時也實現一個協程(coroutin)排程器;可以透過 [explicit](https://glyph.twistedmatrix.com/2014/02/unyielding.html) yield 點來交錯原本循序的邏輯。 同時還有一些可用的實驗性第三方擴增模組，包括 [一個事件驅動的 HTTP server 和 client](https://pypi.python.org/pypi/aiohttp/0.6.5)，社群也持續不斷在打造更多輪子。


換句話說，根據些待開發的應用程式，asyncio 是針對事件導向程式的一個*核心*，


Twusted 是一種用來實現傳輸層與一個事件導向的 API。他一樣有一個以 `inlineCallbacks`形式得到的協程(coroutine)排程器。


Twisted is also a production-quality event-driven [HTTP server and client](https://twistedmatrix.com/trac/wiki/TwistedWeb) including its own [event-driven templating engine](https://twisted.readthedocs.org/en/latest/web/howto/twisted-templates.html), with third-party HTTP addons including [server microframeworks](https://github.com/twisted/klein), [high-level client tools](https://github.com/dreid/treq), [API construction kits](http://haddock.atleastfornow.net/en/latest/intro.html#a-very-simple-example), [robust, two-way browser communication](https://pypi.python.org/pypi/txsockjs), and [automation for usually complex advanced security features](https://github.com/glyph/txsni).


Twisted 同樣具備有產品品質的事件導向 [HTTP server and client](https://twistedmatrix.com/trac/wiki/TwistedWeb) 包含自身[事件導向模板引擎](https://twisted.readthedocs.org/en/latest/web/howto/twisted-templates.html)，以及第三方插件，包含 [server microframeworks](https://github.com/twisted/klein)，[high-level 用戶端工具](https://github.com/dreid/treq)，[API construction kits](http://haddock.atleastfornow.net/en/latest/intro.html#a-very-simple-example), [robust, two-way browser communication](https://pypi.python.org/pypi/txsockjs)，與[自動化，通常是針對複雜的進階安全功能](https://github.com/glyph/txsni)。


Twisted 也同樣是一個 [SSH client](https://twisted.readthedocs.org/en/latest/conch/howto/conch_client.html)，對 OpenSSH，API 和命令列兩者替換。他也是一個 SSH server，我曾聽過用在 production [一些朋友認為是 ok 的](http://www.slideshare.net/mwhudson/how-we-use-twisted-in-launchpad)。再一次，SSH server 既是一個 API 也同樣是一個針對 OpenSSH 的 daemon 替代品。("dro-in replacement" 除非 client 與 server 都無法分析 OpenSSH 的配置文件。[Yet](https://twistedmatrix.com/trac/ticket/3830))


Twisted 同樣有一個[原生的，對稱式事件導向訊息傳遞協議](https://twisted.readthedocs.org/en/latest/core/howto/amp.html)，其目的是要讓[其他語言與環境](http://amp-protocol.net/Implementations/)可以較[容易被實現](http://amp-protocol.net/)，使開發客戶端協議，用多個組件來傳播即時事件，會超乎想像的簡單;用戶端，服務器或是嵌入式裝置，[甚至 web 瀏覽器](https://github.com/lvh/txampext)


Twisted 是一個 [chat server 你可以使用一個 shell 指令來部署](https://twistedmatrix.com/trac/wiki/TwistedWords)。也是 [construction kit for IRC bots](https://github.com/jessamynsmith/talkbackbot)。或是 [XMPP client and server library](http://metajack.im/2008/09/25/an-xmpp-echo-bot-with-twisted-and-wokkel/).[又是 DNS server](https://twistedmatrix.com/trac/wiki/TwistedNames) 以及[事件導向的 DNS client](http://twisted.readthedocs.org/en/latest/names/howto/client-tour.html)。Twisted 也可以當作 [multi-protocol integrated authentication API](http://twisted.readthedocs.org/en/latest/core/howto/cred.html)。或把它當作[建立傳輸的一個可插拔的系統](http://twisted.readthedocs.org/en/latest/core/howto/endpoints.html#maximizing-the-return-on-your-endpoint-investment)來允許第三方傳輸元件來做一些事情，像是[允許你你作為 TOR hidden service 來執行](https://txtorcon.readthedocs.org/en/latest/)只要一個單一命令去切換[不需要修改你的程式碼](https://twistedmatrix.com/pipermail/twisted-python/2014-May/028294.html)。


Twisted 同樣可以作為一個[處理地理位置的數據流](http://twisted.readthedocs.org/en/latest/core/howto/positioning.html)包含[從真實硬體設備，透過序列 port 支援](https://twistedmatrix.com/documents/13.2.0/api/twisted.internet.serialport.SerialPort.html)。


Twisted 可以建置在本機 [GUI 整合支援 Mac，Windows 與 Linux](http://twisted.readthedocs.org/en/latest/core/howto/choosing-reactor.html?highlight=choosing#choosing-a-reactor-and-gui-toolkit-integration)。


繼續下去。


假如還要在說包含那些第三方模組，[可能需要更多時間](https://launchpad.net/tx)。


這裡的關鍵是，Twisted 也存在一個核心 - 很大程度是能夠兼容的，至少在概念上層級採用 `asyncio` 的設計模式 - 它還具備一整套功能，包含函式庫與應用層程序。Twisted 就像是一個 OpenOffice 到 `asyncio` 的 Linux。


當然這個比喻並不完美，同樣 [新生 `asyncio` 社群](http://asyncio.org/)將用其他第三方工具取代這些東西。也當然會有些重複與競爭的項目。這很稀鬆平常也是正向的。這不存在一個馬爾薩斯的競爭的贏者全拿。能夠重複利用 Twisted 與 Tornado 生態系統中現有功能 - 反之亦然，允許這些生態系統使用 `asyncio` 編寫新得功能 - 這不是碰巧發生，是一個 [明確，asyncio 的設計目標](http://legacy.python.org/dev/peps/pep-3156/#interoperability)。



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