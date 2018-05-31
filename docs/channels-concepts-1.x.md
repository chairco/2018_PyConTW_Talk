## [Channels Concepts](https://channels-docs-zhtw.readthedocs.io/en/1.1.5/concepts.html)
Django’s traditional view of the world revolves around requests and responses; a request comes in, Django is fired up to serve it, generates a response to send, and then Django goes away and waits for the next request.

>Django's 傳統視圖看法圍繞著請求(request)與回應(responses)；一個請求進來，Django 被觸發接著服務它，產生一個回應並送出，接著 Django 離開並且等待下一個請求。

That was fine when the internet was driven by simple browser interactions, but the modern Web includes things like WebSockets and HTTP2 server push, which allow websites to communicate outside of this traditional cycle.

>當互聯網是透過簡單的瀏覽器交互驅動時，這是好的方法，但現代的 Web 包括 WebSockets 和 HTTP2 服務器推送，它們允許網站在傳統的周期外通信。

And, beyond that, there are plenty of non-critical tasks that applications could easily offload until after a response has been sent - like saving things into a cache or thumbnailing newly-uploaded images.

>除此之外，還有許多非關鍵任務像是應用程序可以輕鬆的卸載直到一個回應被送出之後 - 例如保存東西到緩存空間或是新生成縮圖-上傳圖像。

It changes the way Django runs to be “event oriented” - rather than just responding to requests, instead Django responds to a wide array of events sent on channels. There’s still no persistent state - each event handler, or consumer as we call them, is called independently in a way much like a view is called.

>這些都改變了 Django 執行 "事件導向" 的方式 - 而非單純回應給請求，相反的 Django 回應各種事件並傳送到 channel 上。這些仍然沒有無法保持持久的狀態 - 每一種事件標頭，或是消費者(我們稱之)是一種像是各自獨立呼叫的視圖方式。

Let’s look at what channels are first.

>讓我們先看看什麼是 channel。

## What is a channel?
The core of the system is, unsurprisingly, a datastructure called a channel. What is a channel? It is an ordered, first-in first-out queue with message expiry and at-most-once delivery to only one listener at a time.

>不令人意外的，核心系統必須是一個稱為資料結構的 channel。什麼是 channel? 它是一個有序列的，先進先出(FIFO)佇列，其中消息到期並且一次只向一個 listener 傳送。

You can think of it as analogous to a task queue - messages are put onto the channel by producers, and then given to just one of the consumers listening to that channel.

>你可以想像類似一個任務的佇列 - 生產者將訊息傳到 channel，接著提供一個只能給某一位消費者監聽的 channel

By at-most-once we say that either one consumer gets the message or nobody does (if the channel implementation crashes, let’s say). The alternative is at-least-once, where normally one consumer gets the message but when things crash it’s sent to more than one, which is not the trade-off we want.

>我們可以說至少一次一個消費者或是沒有人得到訊息(我們這樣說，是假如這個 chnnel 發生 crash)。這個備選方案是至少一次，會有一個消費者獲得消息，但它則會被發送到多個，當發生 crash 時。這不是我們想要的權衡方式。

There are a couple of other limitations - messages must be made of serializable types, and stay under a certain size limit - but these are implementation details you won’t need to worry about until you get to more advanced usage.

>這裡還有一些其它的限制 - 訊息通常被建立為序列的型態，保持在一定大小的限制 - 當你有高優先權的使用時你不需要擔心這些實行的細解。

The channels have capacity, so a lot of producers can write lots of messages into a channel with no consumers and then a consumer can come along later and will start getting served those queued messages.

>channel 是具備容量的，所以許多生產者可以將大量消息寫入沒有消費者的 channel 中，消費者可以隨後再開始取得這些服務與佇列的訊息。

If you’ve used [channels in Go]: Go channels are reasonably similar to Django ones. The key difference is that Django channels are network-transparent; the implementations of channels we provide are all accessible across a network to consumers and producers running in different processes or on different machines.

>假如你使用 [channels in GO]: GO channels 和 Django 相似。但關鍵不同之處在 Django channels 是一種 network-transparent; 我們提供一種 channel 實現存取網路讓消費者與生產者可以執行在不同的行程或是不同的機器。

Inside a network, we identify channels uniquely by a name string - you can send to any named channel from any machine connected to the same channel backend. If two different machines both write to the `http.request channel`, they’re writing into the same channel.
>在網路內，我們定義名稱字串定義 channels 唯一性- 你可以從任何機器連結同樣的 channel 後台然後傳送給任何名稱的 channel。假設兩個不同機器同時寫入 `http.reqyest channel`，他們會寫入同樣 channel。

## How do we use channels?

So how is Django using those channels? Inside Django you can write a function to consume a channel:

>所以如何讓 Django 使用這些 channels? 在 Django 內你可以寫一個 consume to channel 的函式:

```python
def my_consumer(message):
    pass
```

And then assign a channel to it in the channel routing:

>接著在 channel 路由內指派一個 channel 給他:

```python
channel_routing = {
    "some-channel": "myapp.consumers.my_consumer",
}
```

This means that for every message on the channel, Django will call that consumer function with a message object (message objects have a “content” attribute which is always a dict of data, and a “channel” attribute which is the channel it came from, as well as some others).

*需要修正*
>這裡指對於所有在 channel 上訊息，Django 將會呼叫一個伴隨訊息勿件的消費者函式(訊息物件會有一個"內容"屬性，這個物件會一直是 dict 的資料，另一個 "channel" 屬性則是 channel。)

Instead of having Django run in the traditional request-response mode, Channels changes Django so that it runs in a worker mode - it listens on all channels that have consumers assigned, and when a message arrives on one, it runs the relevant consumer. So rather than running in just a single process tied to a WSGI server, Django runs in three separate layers:

>並不是讓 Django 運作在傳統的 request-response 模式，channels 改變 Django 使其可以運作在一個 worker mode - 它可以透過消費指的指派去監聽所有的 channels，當訊息抵達時，相關消費者才執行。因此和在 WSGI server 上單一行程不同，Django 分在三個獨立的 layer 中執行。

- Interface servers, which communicate between Django and the outside world. This includes a WSGI adapter as well as a separate WebSocket server - we’ll cover this later.
- The channel backend, which is a combination of pluggable Python code and a datastore (e.g. Redis, or a shared memory segment) responsible for transporting messages.
- The workers, that listen on all relevant channels and run consumer code when a message is ready.

> -介面服務，做為 Django 與外面世界的溝通。它包含一個 WSGI adapter 像是一個 separate WebSocket server - 在後面介紹。  
> -The channel 後端，用來組合插入的 python 程式碼和一個 datastore (e.g. Redis, or shared memory segment)  
> -The workers，監聽所有相關的 channel，當訊息準備好時執行消費者程式碼。

This may seem relatively simplistic, but that’s part of the design; rather than try and have a full asynchronous architecture, we’re just introducing a slightly more complex abstraction than that presented by Django views.

>這看起來相對簡單，但這是設計的一部分; 而不是嘗試並擁有完整的異步架構，我們只是引入了一個比 Django 視圖呈現的更複雜的抽象。

A view takes a request and returns a response; a consumer takes a channel message and can write out zero to many other channel messages.

>一個視圖提供一個請求與回傳一個回應；一個消費者帶來一個 channel 訊息與寫出一個 0 到 其他更多的 channel 訊息。

Now, let’s make a channel for requests (called `http.request`), and a channel per client for responses (e.g. `http.response.o4F2h2Fd`), where the response channel is a property (`reply_channel`) of the request message. Suddenly, a view is merely another example of a consumer:

>現在讓我們針對 request 建立一個 channel(稱為 `http.request`), 與一個針對每一個客戶端回應的 channel(e.g. `http.response.04F2h2Fd`)，其中回應 channel 是一個請求訊息的屬性(`reply_channel`)。馬上，一個視圖僅為其他消費者的一例：

```python
# Listens on http.request
def my_consumer(message):
    # Decode the request from message format to a Request object
    django_request = AsgiRequest(message)
    # Run view
    django_response = view(django_request)
    # Encode the response into message format
    for chunk in AsgiHandler.encode_response(django_response):
        message.reply_channel.send(chunk)
```

In fact, this is how Channels works. The interface servers transform connections from the outside world (HTTP, WebSockets, etc.) into messages on channels, and then you write workers to handle these messages. Usually you leave normal HTTP up to Django’s built-in consumers that plug it into the view/template system, but you can override it to add functionality if you want.

>實際上，這是說 channels 如何運作。channel 上界面服務會將對應的介面(HTTP, WebSocket, etc.)轉換連結到對應訊息，接著你會編寫 worker 處理這些訊息。接口服務器將來自外部世界（HTTP，WebSockets 等）的連接轉換為通道上的消息，然後編寫 worker 以處理這些消息。

However, the crucial part is that you can run code (and so send on channels) in response to any event - and that includes ones you create. You can trigger on model saves, on other incoming messages, or from code paths inside views and forms. That approach comes in handy for push-style code - where you use WebSockets or HTTP long-polling to notify clients of changes in real time (messages in a chat, perhaps, or live updates in an admin as another user edits something).

>然而，關鍵的部分是你可以在任何 event 回應時執行程式碼(接著可以在 channel 送出) - 且包含你自己所創建的。你可以在 model 儲存，在其他訊息進入時或是當其他從程式碼路徑進入 views 或是 forms 時觸發。這個方法對於 push-style 的程式碼很有用 -在那使用 WebSockets 或 HTTP long-polling 時通知客戶的更改（聊天中的消息，或者在管理員的實時更新作為另一個用戶編輯的東西）。

## Channel Types
There are actually two major uses for channels in this model. The first, and more obvious one, is the dispatching of work to consumers - a message gets added to a channel, and then any one of the workers can pick it up and run the consumer.

>這個 model 中的 channel 主要有兩種用途。第一，且是比較明顯的一種是分派工作給消費者 - 一個訊息被得到與新增到 channel, 接著任何一個 worker 可以取得並且執行消費者。

The second kind of channel, however, is used for replies. Notably, these only have one thing listening on them - the interface server. Each reply channel is individually named and has to be routed back to the interface server where its client is terminated.

>第二種通道用途是用於回覆。值得注意是他們只有做一件事就是監聽 -介面服務。每一個回應的 channel 是各自獨立的名稱且當其 client 端被終止，必須路由回界面服務。

This is not a massive difference - they both still behave according to the core definition of a channel - but presents some problems when we’re looking to scale things up. We can happily randomly load-balance normal channels across clusters of channel servers and workers - after all, any worker can process the message - but response channels would have to have their messages sent to the channel server they’re listening on.

>這不是巨大差異 - 他們能然根據核心定義 channel 行為 - 但當我們想擴大規模時會出現一些問題。我們可以愉快的根據叢集隨機附載平衡服務正常的 channels 和 workers - 最終，任何 worker 可以處理訊息 - 但回應 channels 必須傳送訊息到它們正在監聽的 channel 服務。

For this reason, Channels treats these as two different channel types, and denotes a reply channel by having the channel name contain the character `!` - e.g. `http.response!f5G3fE21f`. Normal channels do not contain it, but along with the rest of the reply channel name, they must contain only the characters `a-z A-Z 0-9 - _`, and be less than 200 characters long.

>對於這個理由，Channels 對此區分出兩種不同類型的 channel 型態，且通過一個包含 `!` 的字符名稱來表示一個回應 channel。 -e.g. `http.response!f5G3fE21f`。通常 channels 不會包含它，但是會與其他休息中的回覆 channel 名稱一起，它們通常包含字符 `a-z A-Z 0-9 - _`，且必須少於 200 字符的長度。

It’s optional for a backend implementation to understand this - after all, it’s only important at scale, where you want to shard the two types differently — but it’s present nonetheless. For more on scaling, and how to handle channel types if you’re writing a backend or interface server, see [Scaling Up].

>這裡可以用選擇後端實現來理解他 - 畢竟，這只對於 Scale 重要，因為這邊你想要分割兩種不同類型 - 但是它仍然存在。假如你是撰寫後端或是介面服務對更多彈性與掌控 channel types 可以參考 [Scaling Up].

## Groups
Because channels only deliver to a single listener, they can’t do broadcast; if you want to send a message to an arbitrary group of clients, you need to keep track of which reply channels of those you wish to send to.

>因為 channels 只能傳送到單一個 listener 無法做廣播；假如你希望傳送一個訊息給任意的終端群組，你需要對發送的 channel 的回覆保持追蹤。

If I had a liveblog where I wanted to push out updates whenever a new post is saved, I could register a handler for the post_save signal and keep a set of channels (here, using Redis) to send updates to:

>假設我有一個實況部落格，當有一個新的 post 儲存了，我希望推送出去更新，我可以針對 post_save 訊號註冊一個標頭並且保持一個 channel 設定(這裡，使用 Redis) 去送出一個更新：

```python
redis_conn = redis.Redis("localhost", 6379)

@receiver(post_save, sender=BlogUpdate)
def send_update(sender, instance, **kwargs):
    # Loop through all reply channels and send the update
    for reply_channel in redis_conn.smembers("readers"):
        Channel(reply_channel).send({
            "text": json.dumps({
                "id": instance.id,
                "content": instance.content
            })
        })

# Connected to websocket.connect
def ws_connect(message):
    # Add to reader set
    redis_conn.sadd("readers", message.reply_channel.name)
```

While this will work, there’s a small problem - we never remove people from the readers set when they disconnect. We could add a consumer that listens to websocket.disconnect to do that, but we’d also need to have some kind of expiry in case an interface server is forced to quit or loses power before it can send disconnect signals - your code will never see any disconnect notification but the reply channel is completely invalid and messages you send there will sit there until they expire.

>雖然這樣可以運作，但有一個小的問題 - 當他們斷線時我們無法從這個 readers 設定移除連接。我們可以增加一個 consumer(消費者)可以透過監聽 `websocket.disconnect` 來處理，但我們也會需要在 interface server 有一些到期類別被迫退出或失去電源，然後才能發送斷開信號 - 你的程式碼將永遠不會看見任何斷線的提示，但 reply channel 是一個完全無效的訊息，你發送到那邊的東西將會停留直到過期。

Because the basic design of channels is stateless, the channel server has no concept of “closing” a channel if an interface server goes away - after all, channels are meant to hold messages until a consumer comes along (and some types of interface server, e.g. an SMS gateway, could theoretically serve any client from any interface server).

>因為這個 channels 的基礎設計是無狀態的，假設 channel 的介面服務消失 channel server 沒有任何 "closing" 概念 - 畢竟，channel 意味著保留訊息直到一個消費者來臨(某些介面服務的類別， 例如：一個 SMS 閘道，理論上可以服務從任意的介面服務的任何 client)

We don’t particularly care if a disconnected client doesn’t get the messages sent to the group - after all, it disconnected - but we do care about cluttering up the channel backend tracking all of these clients that are no longer around (and possibly, eventually getting a collision on the reply channel name and sending someone messages not meant for them, though that would likely take weeks).

>我們不特別關心一個斷線的 client 沒有取得發送群組的訊息 - 畢竟它已經斷線 - 但是我們關心睹塞通道後端追蹤那些已經不再存在的 client (也可能在回覆 channel 發生衝突和發送不具意義的訊息，雖然有可能是在幾週之後)

Now, we could go back into our example above and add an expiring set and keep track of expiry times and so forth, but what would be the point of a framework if it made you add boilerplate code? Instead, Channels implements this abstraction as a core concept called Groups:

>現在，我們可以回到上面的範例並且添加一個過期的集合並且持續追蹤直到一個到期時間，但什麼才是一個讓你增加程式碼到 `boilerplate` 的模板架構呢？ 相反，Channels 改善這個一個核心的抽象概念稱為 `Goups`:

```python
@receiver(post_save, sender=BlogUpdate)
def send_update(sender, instance, **kwargs):
    Group("liveblog").send({
        "text": json.dumps({
            "id": instance.id,
            "content": instance.content
        })
    })

# Connected to websocket.connect
def ws_connect(message):
    # Add to reader group
    Group("liveblog").add(message.reply_channel)

# Connected to websocket.disconnect
def ws_disconnect(message):
    # Remove from reader group on clean disconnect
    Group("liveblog").discard(message.reply_channel)
```

Not only do groups have their own send() method (which backends can provide an efficient implementation of), they also automatically manage expiry of the group members - when the channel starts having messages expire on it due to non-consumption, we go in and remove it from all the groups it’s in as well. Of course, you should still remove things from the group on disconnect if you can; the expiry code is there to catch cases where the disconnect message doesn’t make it for some reason.

>`do groups` 不僅有他們自己的 send() 方法（後端可以提供有效的實現），它們同樣可以自動化的管理到期的群組成員 - 當這個 channel 開始有訊息時直到未被消費且到期時，我們進入所有群組並且移除這些訊息。當然，假如可以你仍然應該移除群組在斷開連線時; 因為某些原因，斷線時訊息沒有辦法成功傳送，斷開連線的程式碼是抓取這個例外。

Groups are generally only useful for reply channels (ones containing the character !), as these are unique-per-client, but can be used for normal channels as well if you wish.

>`Groups` 一般來說對於 reply channels 是有用的(包含字符！), 假如你想將他們使用於一般的 channels 是可行的，因為它們都是唯一的客戶端。

## Next Steps
That’s the high-level overview of channels and groups, and how you should start thinking about them. Remember, Django provides some channels but you’re free to make and consume your own, and all channels are network-transparent.

>這是一個高級的 channels 和 groups 概覽與如何開始思考它。記住，Django 提供一些 channels 但你自由的使用與消費，所有的 channels 都是透明網路(network-transparent)

One thing channels do not, however, is guarantee delivery. If you need certainty that tasks will complete, use a system designed for this with retries and persistence (e.g. Celery), or alternatively make a management command that checks for completion and re-submits a message to the channel if nothing is completed (rolling your own retry logic, essentially).

>有件事是 channels 不是保證渠道的交付。假如你需要確定是一個將被完成任務，使用一個為此設計的系統設定去重試與保持（e.g. Celery），或是做出一個管理命令，假如檢查沒有完成，會重新送出一個訊息給 channel（自己動手去重試這個邏輯）

We’ll cover more about what kind of tasks fit well into Channels in the rest of the documentation, but for now, let’s progress to Getting Started with Channels and writing some code.

>我們將在文檔的其餘部分更詳細地介紹什麼樣的任務適合用在 Channels 中，但現在讓我們進入 `Getting Started with Channels` 並編寫一些 程式碼。

[channels in Go]:https://gobyexample.com/channels
[Scaling Up]:http://channels.readthedocs.io/en/latest/deploying.html#scaling-up
