==========================================================
ASGI (Asynchronous Server Gateway Interface) Specification
==========================================================

**Version**: 2.0 (2017-11-28)

Abstract 摘要
========

This document proposes a standard interface between network protocol
servers (particularly web servers) and Python applications, intended
to allow handling of multiple common protocol styles (including HTTP, HTTP/2,
and WebSocket).

本文檔提出了網路協議間的標準介面服務器（尤其是 web 服務器）和 Python 應用程式，意在允許處理
多種常見協議樣式（包含 HTTP, HTTP/2, 和 WeBSocket）


This base specification is intended to fix in place the set of APIs by which
these servers interact and run application code;
each supported protocol (such as HTTP) has a sub-specification that outlines
how to encode and decode that protocol into messages.

這個基本規劃旨在解決這些服務器交互並運行應用程序程式碼的 API 集合; 每個支持的協議（例如 HTTP）都
有一個子規範，概述如何將該協議編碼和解碼成為訊息。


Rationale 依據
=========

The WSGI specification has worked well since it was introduced, and
allowed for great flexibility in Python framework and web server choice.
However, its design is irrevocably tied to the HTTP-style
request/response cycle, and more and more protocols are becoming a
standard part of web programming that do not follow this pattern
(most notably, WebSocket).

WSGI 規範從推出後運行的很順利，並且允許 Python 框架與 Web server 選擇有很大彈性。
然和他的設計與 HTTP 風格請求/回應響應週期不可改變且緊密地結合在一起，同時有越來越多的
協議逐漸成為開發 web 程式的標準，它們也逐漸不再遵循這種模式（最為人所知就是 WebSocket）。


ASGI attempts to preserve a simple application interface, but provide
an abstraction that allows for data to be sent and received at any time,
and from different application threads or processes.

ASGI 嘗試保留一個簡單的應用程式介面，但提供一個抽象化可以允許隨時從不同應用程式
執行緒或是行程來發送與接收資料。


It also take the principle of turning protocols into Python-compatible,
asynchronous-friendly sets of messages and generalises it into two parts;
a standardised interface for communication and to build servers around (this
document), and a set of standard message formats for each protocol.

它也採用將協議轉換成 Python-兼容，非同步-友好的訊息集合並將其概括為兩部分原則;一個用於通信
的標準介面與圍繞建構伺服器（本文件），以及一組用於每個協議的標準訊息格式。


Its primary goal is to provide a way to write HTTP/2 and WebSocket code,
alongside normal HTTP handling code, however, and part of this design is
ensuring there is an easy path to use both existing WSGI servers and
applications, as a large majority of Python web usage relies on WSGI and
providing an easy path forwards is critical to adoption. Details on that
interoperability are covered in the ASGI-HTTP spec.

他主要目標是提供一個方法來編寫 HTTP/2 與 WebSocket 程式碼，以及一般的 HTTP 處理程式碼，
然而這種設計一部分是確保有個簡單的途徑來使用現有的 WSGI 服務器與應用程式，作為絕大多數依賴 
WSGI 的 Python web 提供一個簡單途徑繼續前進，至關重要。ASGI-HTTP 規範介紹了這種互通性
的細節。


Overview 總覽
========

ASGI consists of two different components:

ASGI 由兩個不同的兩個組件組成


- A *protocol server*, which terminates sockets and translates them into
  connections and per-connection event messages.

- 一個*協議服務器*，其用來終止 sockets 與轉換他們成為一個連接與每個連接的事件訊息。


- An *application*, which lives inside a *protocol server*, is instantiated
  once per connection, and handles event messages as they happen.

- 一個*應用程式*，它位於一個*協議服務器*內，每一個連接會實例化一次，並在事件訊息發生時處理。


Like WSGI, the server hosts the application inside it, and dispatches incoming
requests to it in a standardized format. Unlike WSGI, however, applications
are instantiated objects that are fed events rather than simple callables,
and must run as ``asyncio``-compatible coroutines (on the main thread;
they are free to use threading or other processes if they need synchronous code).

與 WSGI 很類似，服務器託管其中的應用程式，接著以標準格式對其發送傳入請求。然而與 WSGI 不同是
應用程式是實例化後的對象，它們是事件，而非簡單可調用的，而且必須作為 ``asyncio``--兼容的協程運作
（在主線程上;假如需要同步程式碼，可以自由地使用線程或是其它行程）。


Unlike WSGI, there are two separate parts to an ASGI connection:

不同於 WSGI，一個 ASGI 有兩個獨立的連接部分：


- A *connection scope*, which represents a protocol connection to a user and
  survives until the connection closes.

- 一個*連接範圍*，其代表一個協議連接到一個使用者，且它會存活直到連接被關閉。


- *Events*, which are sent to the application as things happen on the
  connection.

- *事件*，其發生在連結時發送給應用程序。


Applications are instantiated with a connection scope, and then run in an
event loop where they are expected to handle events and send data back to the
client.

應用程序在一個連線範圍內被實例化，然後在預期處理事件時執行一個事件迴圈接著傳送資料回去客戶端。


Each application instance maps to a single incoming "socket" or connection, and
is expected to last the lifetime of that connection plus a little longer if
there is cleanup to do. Some protocols may not use traditional sockets; ASGI
specifications for those protocols are expected to define what the scope
(instance) lifetime is and when it gets shut down.

每個應用程式實例都映射到一個單一傳入的 "socket" 或連接，假如有清理操作，則預計將持續
這個連接的生命週期再加上一點時間。一些協議也許不會使用傳統的 socket; ASGI 規範將針對這些協議去
做預期，接著定義範圍（實例）的生命週期以及何時將它關閉。


Specification Details 規格細節
=====================

Connection Scope 連接範圍
----------------

Every connection by a user to an ASGI application results in an instance of
that application being created for the connection. How long this lives, and
what information it gets given upon creation, is called the *connection scope*.

用戶到 ASGI 應用程式的每個連接都將導致為該連接應用程式的實例被建立。多長，與在建立時所得到
的訊息，這些被稱為*連接範圍*


For example, under HTTP the connection scope lasts just one request, but it
contains most of the request data (apart from the HTTP request body, as this
is streamed in via events).

舉個例，在 HTTP 連接範圍下知會持續一個請求，但它已經包含大多數的請求資料（除 HTTP request 
body 外，因為它透過 streamed 來傳遞事件）


Under WebSocket, though, the connection scope lasts for as long as the socket
is connected. The scope contains information like the WebSocket's path, but
details like incoming messages come through as Events instead.

但，在 WebSocket，只要 socket 連接著，連接範圍就會不斷持續著。這個範圍包含的訊息像是 
WebSocket 的路徑，但傳入訊息等細節則是以事件的形式出現。


Some protocols may give you a connection scope with very limited information up
front because they encapsulate something like a handshake. Each protocol
definition must contain information about how long its connection scope lasts,
and what information you will get inside it.

有些協議可能會提供一個連接範圍，但只有非常有限的訊息，因為他們封裝了握手之類的東西。每個協議
定義都必須包含觀其連接範圍持續多長的訊息，與從中獲得哪些訊息。


Applications **cannot** communicate with the client when they are
initialized and given their connection scope; they must wait until their
event loop is entered, and depending on the protocol spec, may have to
wait for an initial opening message.

應用程式在被初始化與給定期連接範圍時**不能**與客戶端進行通訊; 他們必須等待到事件迴圈進入
並且根據協議規範，可能必須等待最初開始的訊息。


Events 事件
------

ASGI decomposes protocols into a series of *events* that an application must
react to. For HTTP, this is as simple as two events in order - ``http.request``
and ``http.disconnect``. For something like a WebSocket, it could be more like
``websocket.connect``, ``websocket.receive``, ``websocket.receive``,
``websocket.disconnect``.

ASGI 將協議分解一系列應用程式必須回應的*事件*，這與按順序的兩個事件一樣簡單 - ``http.request``
與 ``http.disconnect``。 針對像是一個 WebSocket，可能就會像是 ``websocket.connect``, ``websocket.receive``, ``websocket.receive``,
``websocket.disconnect``。


Each event is a ``dict`` with a top-level ``type`` key that contains a
unicode string of the message type. Users are free to invent their own message
types and send them between application instances for high-level events - for
example, a chat application might send chat messages with a user type of
``mychat.message``. It is expected that applications would be able to handle
a mixed set of events, some sourced from the incoming client connection and
some from other parts of the application.

每個事件都是一個 ``dict`` 並帶著一個最高等級 ``type`` key，包含訊息類型的一個 unicode 字串。
使用者可以自由的建立他們自己的訊息種類，並在應用程式實例之間發送他們以進行高級別事件 - 舉例
一個聊天應用程式可能會發送一個使用者 ``mychat.message`` 種類的聊天訊息。預期應用程式可以處理
一組混合的事件，其中一些事件來自傳入客戶端連接，另一些則來自應用程式的其他部分。


Because these messages could be sent over a network, they need to be
serializable, and so they are only allowed to contain the following types:

因為這些訊息可能來自其他網路，他們需要被序列化，因此訊息被要求只能包含如以下幾種類型：


* Byte strings
* Unicode strings
* Integers (within the signed 64 bit range)
* Floating point numbers (within the IEEE 754 double precision range, no ``Nan`` or infinities)
* Lists (tuples should be encoded as lists)
* Dicts (keys must be unicode strings)
* Booleans
* ``None``


Applications 應用程式
------------

ASGI applications are defined as a callable::

ASGI 應用程式被定義成可調用的：


    application(scope) 應用（範圍）

* ``scope``: The Connection Scope, a dictionary that contains at least a
  ``type`` key specifying the protocol that is incoming.

* ``範圍``：連接範圍，一個至少包含一個 ``type`` key 所指定傳入協議的字典。


This first callable is called whenever a new connection comes in to the
protocol server, and creates a new *instance* of the application per
connection (the instance is the object that this first callable returns).

每當一個新的連接進入協議服務器，這個第一個可調用的對像在有新連接時會被調用
並建立一個新的*實例*（這個實例是一個物件，第一次被調用時回傳）


This callable is synchronous, and must not contain blocking calls (it's
recommended that all it does is store the scope). If you need to do
blocking work, you must do it at the start of the next callable, before you
application awaits incoming events.

這個調用是一個同步的，且不能包含阻塞調用（建議只作為儲存的範圍）。假如你需要去執行阻塞工作，
則必須在下一個可以調用的開始時執行它，然後你的應用程式才會進入 await 等待事件傳入。


It must return another, awaitable callable::

它必須返回另一個，可以等待的調用::


    coroutine application_instance(receive, send)

    協程 application_instance(receive, send)


* ``receive``, an awaitable callable that will yield a new event dict when
  one is available

* ``receive``，一個可供等待的可調用函數，當可用時它會 yield 一個新的事件字典
  
  
* ``send``, an awaitable callable taking a single event dict as a positional
  argument that will return once the send has been completed

* ``send``，一個可等待的可調用的單個事件字典作為一位置參數，一旦發送完成就會返回


This design is perhaps more easily recognised as one of its possible
implementations, as a class::

這個設計也許更容易被認為是一個可能的實現，像是一個 class::


    class Application:

        def __init__(self, scope):
            self.scope = scope

        async def __call__(self, receive, send):
            ...

The application interface is specified as the more generic case of two callables
to allow more flexibility for things like factory functions or type-based
dispatchers.

應用程序的界面是被指定兩個可被調用且更一般情況，看起來會像是工廠功能或是基於 dispatchers 等提供
更多彈性。


Both the ``scope`` and the format of the messages you send and receive are
defined by one of the application protocols. ``scope`` must be a ``dict``.
The key ``scope["type"]`` will always be present, and can be used to work
out which protocol is incoming.

無論是 ``scope`` 或你發送和接受的應用持續協議中的一種訊息。``scope``必須是一個 ``dict``。
key ``scope["type"]`` 始終存在，並可用於確定傳入哪個協議。


The protocol-specific sub-specifications cover these scope
and message formats. They are equivalent to the specification for keys in the
``environ`` dict for WSGI.

協議特定的子規範包含了這些範圍的訊息格式。它們相當於 ``environ`` WSGI 字典中 key 的規範。


Protocol Specfications 協議規範
----------------------

These describe the standardized scope and message formats for various protocols.

這邊描述各種協議的標準化範圍和訊息格式


The one common key across all scopes and messages is ``type``, a way to indicate
what type of scope or message is being received.

跨所有範圍和訊息的一個 common key 是 ``type``，一種只是正在接收什麼類型的範圍或訊息方法。


In scopes, the ``type`` key must be a unicode string, like ``"http"`` or
``"websocket"``, as defined in the relevant protocol specification.

在範圍中，``type`` key 必須是一個 unicode 字串，像是 ``"http"`` 或是 ``"websocket"``，
如相關協議規範中的定義。


In messages, the ``type`` should be namespaced as ``protocol.message_type``,
where the ``protocol`` matches the scope type, and ``message_type`` is
defined by the protocol spec. Examples of a message ``type`` value include
``http.request`` and ``websocket.send``.

在訊息中，``type`` 應該是命名空間 ``protocol.message_type``，所述， ``protocol`` 
匹配 scope type，並且 ``message_type`` 是個由協議規範的定義。訊息中 ``type`` 值的
例子包含 ``http.request`` 與 ``websocket.send``。


Current protocol specifications:

當前協議規範：


* `HTTP and WebSocket <https://github.com/django/asgiref/blob/master/specs/www.rst>`_


Middleware 中間件
----------

It is possible to have ASGI "middleware" - code that plays the role of both
server and application, taking in a scope and the send/receive awaitables,
potentially modifying them, and then calling an inner application.

ASGI "middleware" 是可能的 - 程式碼扮演了服務器和應用程式的角色，又接受一個範圍和
發送/接收等待，可能修改它們，然後呼叫一個內部應用程式。


When middleware is modifying the scope, it should make a copy of the scope
object before mutating it and passing it to the inner application, as otherwise
changes may leak upstream. In particular, you should not assume that the copy
of the scope you pass down to the application is the one that it ends up using,
as there may be other middleware in the way; thus, do not keep a reference to
it and try to mutate it outside of the initial ASGI constructor callable that
gets passed ``scope``.

當一個 middleware 是一個修改範圍時，應該要在作用域對象的副本進行變異並將其傳遞給內部應用程序
之前進行修改，否則更改可能會向上游洩漏。特別是，您不應該假設您傳遞給應用程序的範圍的副本是其最
終使用的範圍的副本，因為可能有其他中間件; 因此，不要保留對它的引用，並嘗試將它改變為傳遞的初始 
ASGI 構造器可調用外部 ``scope``。


It's notable that the part of ASGI applications that gets to modify the
``scope`` runs synchronously, as it's designed to be compatible with Python
class constructors. If you need to put objects into the scope that require
blocking/asynchronous work to resolve, then either make them awaitables
themselves, or make objects that you can fill in later during the coroutine
entry (remember, the objects must be modifiable; you cannot keep a reference
to the scope and try to add keys later).

值得注意的是，ASGI應用程序的一部分 ``scope``同步運行，因為它旨在與 Python 類構造函數兼容。
如果您需要將對象放入需要阻塞/異步工作解決的範圍中，則可以讓它們自己等候，或者在協程入口期間
創建可以填寫的對象（請記住，對象必須是可修改的;您無法保留對范圍的引用並嘗試稍後添加鍵）。


Error Handling 錯誤處理
--------------

If a server receives an invalid event dict - for example, with an unknown type,
missing keys a type should have, or with wrong Python types for objects (e.g.
unicode strings for HTTP headers), it should raise an exception out of the
``send`` awaitable back into the application.

如果服務器收到一個無效的事件字典-例如，一個未知類型，缺少密鑰的類型都應該有，或者用錯了
Python 類型的對象（例如對於 HTTP headers Unicode 字串），它應該拋出一個異常出的
``send`` awaitable 回進入應用程式。

If an application receives an invalid event dict from ``receive`` it should
raise an exception.

如果應用程序收到無效的事件字典，``receive`` 應該引發異常。


In both cases, presence of additional keys in the event dict should not raise
an exception. This is to allow non-breaking upgrades to protocol specifications
over time.

在這兩種情況下，事件字典中的其他鍵的存在都不應引發異常。這是為了允許隨著時間的推移對協議規範
進行不間斷的升級。

Servers are free to surface errors that bubble up out of application instances
they are running however they wish - log to console, send to syslog, or other
options - but they must terminate the application instance and its associated
connection if this happens.

服務器可以自由地顯示錯誤，這些錯誤會從他們正在運行的應用程序實例中冒出來 - 但是他們希望 
- 登錄到控制台，發送到系統日誌或其他選項 - 但是如果發生這種情況，他們必須終止應用程式實例
及其關聯的連接。


Extensions 擴展
----------

There are times when protocol servers may want to provide server-specific
extensions outside of a core ASGI protocol specification, or when a change
to a specification is being trialled before being rolled in.

有時候協議服務器可能希望在核心 ASGI 協議規範之外提供特定於服務器的擴展，或者在規範的更改被推入
之前進行試運行。


For this use case, we define a common pattern for ``extensions`` - named
additions to a protocol specification that are optional but that, if provided
by the server and understood by the application, can be used to get more
functionality.

對於這個用例，我們定義了一個通用模式 ``extensions`` - 對協議規範的名稱添加是可選的，
但如果由服務器提供並由應用程序理解，則可用於獲取更多功能。


This is achieved via a ``extensions`` entry in the ``scope`` dict, which is
itself a dict. Extensions have a unicode string name that
is agreed upon between servers and applications.

這是通過字典中的一個 ``extensions`` 條目實現的 ``scope``，這本身就是一個字典。
擴展名有一個在服務器和應用程序之間達成一致的unicode字符串名稱。

If the server supports an extension, it should place an entry into the
``extensions`` dict under the extension's name, and the value of that entry
should itself be a dict. Servers can provide any extra scope information
that is part of the extension inside this dict value, or if the extension is
only to indicate that the server accepts additional events via the ``send``
callable, it may just be an empty dict.

如果服務器支持擴展名，它應該 ``extensions`` 在擴展名的下面輸入一個條目，並且該條目的值本身
應該是一個字典。服務器可以提供任何額外的範圍信息，這些信息屬於此 dict 值中擴展的一部分，
或者如果擴展只是表明服務器通過 ``send`` 可調用函數接受附加事件，則它可能只是一個空字典。

As an example, imagine a HTTP protocol server wishes to provide an extension
that allows a new event to be sent back to the server that tries to flush the
network send buffer all the way through the OS level. It provides an empty
entry in the extensions dict to signal that it can handle the event::

例如，假設 HTTP 協議服務器希望提供一個擴展，允許將新事件發送回嘗試刷新網絡發送緩衝區的服務器，
直到整個操作系統級別。它在擴展詞典中提供一個空的條目來表明它可以處理該事件::

    scope = {
        "type": "http",
        "method": "GET",
        ...
        "extensions": {
            "fullflush": {},
        },
    }

If an application sees this it then knows it can send the custom event
(say, of type ``http.fullflush``) via the ``send`` callable.

如果應用程序看到它，它就知道它可以http.fullflush通過send可調用函數發送自定義事件（比如類型）。


Strings and Unicode 字串與 Unicode
-------------------

In this document, and all sub-specifications, *byte string* refers to
the ``bytes`` type in Python 3. *Unicode string* refers to the ``str`` type
in Python 3.

在本文檔和所有子規範中，字節字符串指的是 *bytes* Python 3 中的類型。
*Unicode* 字串指的 ``str`` 是 Python 3 中的類型。

This document will never specify just *string* - all strings are one of the
two exact types.

這個文檔永遠不會指定字符串 - 所有 *string* 都是兩種確切類型之一。


All dict keys mentioned (including those for *scopes* and *events*) are
unicode strings.

提到的所有字典 key（包括*範圍*和*事件*）都是 unicode 字串。


Version History
===============

* 2.0 (2017-11-28): Initial non-channel-layer based ASGI spec


Copyright
=========

This document has been placed in the public domain.
