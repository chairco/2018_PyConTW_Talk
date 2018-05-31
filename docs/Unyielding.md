# [Unyielding](https://glyph.twistedmatrix.com/2014/02/unyielding.html)

*Be as the reed, not the oak tree. Green threads are just threads.*

`Monday February 24, 2014`

>… that which is hard and stiff
is the follower of death
that which is soft and yielding
is the follower of life …

– the Tao Te Ching, chapter 76


## Problem: Threads Are Bad


[As we know](http://www.stanford.edu/~ouster/cgi-bin/papers/threads.pdf), threads are a bad idea, (for most purposes). Threads make local reasoning difficult, and local reasoning is perhaps the most important thing in software development.


With the word “threads”, I am referring to [shared-state multithreading](http://berb.github.io/diploma-thesis/original/052_threads.html), despite the fact that there are languages, like [Erlang](http://www.erlang.org/doc/getting_started/conc_prog.html) and [Haskell](http://hackage.haskell.org/package/threads) which refer to concurrent processes – those which do not implicitly share state, and require explicit coordination – as “threads”.


My experience is mainly (although not exclusively) with [Python](http://www.python.org/) but the ideas presented here should generalize to most languages which have global shared mutable state by default, which is to say, quite a lot of them: C (including Original Recipe, Sharp, Extra Crispy, Objective, and Plus Plus), JavaScript, Java, Scheme, Ruby, and PHP, just to name a few.


With the phrase “local reasoning”, I’m referring to the ability to understand the behavior (and thereby, the correctness) of a routine by examining the routine itself rather than examining the entire system.


When you’re looking at a routine that manipulates some state, in a single-tasking, nonconcurrent system, you only have to imagine the state at the beginning of the routine, and the state at the end of the routine. To imagine the different states, you need only to read the routine and imagine executing its instructions in order from top to bottom. This means that the number of instructions you must consider is n, where n is the number of instructions in the routine. By contrast, in a system with arbitrary concurrent execution – one where multiple threads might concurrently execute this routine with the same state – you have to read the method in every possible order, making the complexity n^n.


Therefore it is – literally – exponentially more difficult to reason about a routine that may be executed from an arbitrary number of threads concurrently. Instead, you need to consider every possible caller across your program, understanding what threads they might be invoked from, or what state they might share. If you’re writing a library desgined to be thread-safe, then you must place some of the burden of this understanding on your caller.


The importance of local reasoning really cannot be overstated. Computer programs are, at least for the time being, constructed by human beings who are thinking thoughts. Correct computer programs are constructed by human beings who can simultaneously think thoughts about all the interactions that the portion of the system they’re developing will have with other portions.


[A human being can only think about seven things at once, plus or minus two.](https://en.wikipedia.org/wiki/The_Magical_Number_Seven,_Plus_or_Minus_Two) Therefore, although we may develop software systems that contain thousands, millions, or billions of components over time, we must be able to make changes to that system while only holding in mind an average of seven things. Really bad systems will make us concentrate on nine things and we will only be able to correctly change them when we’re at our absolute best. Really good systems will require us to concentrate on only five, and we might be able to write correct code for them even when we’re tired.


## Aside: “Oh Come On They’re Not That Bad”


Those of you who actually use threads to write real software are probably objecting at this point. “Nobody would actually try to write free-threading code like this,” I can hear you complain, “Of course we’d use a lock or a queue to introduce some critical sections if we’re manipulating state.”

Mutexes can help mitigate this combinatorial explosion, but they can’t eliminate it, and they come with their own cost; you need to develop strategies to ensure consistent ordering of their acquisition. Mutexes should really be used to build queues, and to avoid deadlocks those queues should be non-blocking but eventually a system which communicates exclusively through non-blocking queues effectively becomes a set of communicating event loops, and its problems revert to those of an event-driven system; it doesn’t look like regular programming with threads any more.

But even if you build such a system, if you’re using a language like Python (or the ones detailed above) where modules, classes, and methods are all globally shared, mutable state, it’s always possible to make an error that will affect the behavior of your whole program without even realizing that you’re interacting with state at all. You have to have a level of vigilance bordering on paranoia just to make sure that your conventions around where state can be manipulated and by whom are honored, because when such an interaction causes a bug it’s nearly impossible to tell where it came from.

Of course, threads are just one source of inscrutable, brain-bending bugs, and quite often you can make workable assumptions that preclude you from actually having to square the complexity of every single routine that you touch; for one thing, many computations don’t require manipulating state at all, and you can (and must) ignore lots of things that can happen on every line of code anyway. (If you think not, when was the last time you audited your code base for correct behavior in the face of memory allocation failures?) So, in a sense, it’s possible to write real systems with threads that perform more or less correctly for the same reasons it’s possible to write any software approximating correctness at all; we all need a little [strength of will and faith in our holy cause](http://www.questia.com/library/journal/1G1-275129772/tutto-e-zuppa-making-the-superego-enjoy-in-calvino-s) sometimes.


Nevertheless I still think it’s a bad idea to make things harder for ourselves if we can avoid it.


## Solution: Don’t Use Threads


So now I’ve convinced you that if you’re programming in Python (or one of its moral equivalents with respect to concurrency and state) you shouldn’t use threads. Great. What are you going to do instead?


[There’s a lot of debate over the best way to do “asynchronous” programming](https://glyph.twistedmatrix.com/2012/01/concurrency-spectrum-from-callbacks-to.html) - that is to say, “not threads”, four options are often presented.


1. Straight callbacks: Twisted’s `IProtocol`, JavaScript’s `on<foo>` idiom, where you give a callback to something which will call it later and then return control to something (usually a main loop) which will execute those callbacks,

2. “Managed” callbacks, or Futures: Twisted’s `Deferred`, JavaScript’s `Promises/A[+]`, [E’s Promises](http://www.erights.org/talks/promises/), where you create a dedicated result-that-will-be-available-in-the-future object and return it for the caller to add callbacks to,

3. Explicit coroutines: Twisted’s `@inlineCallbacks`, Tulip’s `yield from` coroutines, C#’s `async/await`, where you have a syntactic feature that explicitly suspends the current routine,

4. and finally, implicit coroutines: [Java’s “green threads”](http://en.wikipedia.org/wiki/Green_threads#Green_threads_in_the_Java_virtual_machine), Twisted’s [Corotwine](https://github.com/radix/corotwine), [eventlet](https://pypi.python.org/pypi/eventlet), [gevent](https://pypi.python.org/pypi/gevent), where any function may switch the entire stack of the current thread of control by calling a function which suspends it.

[One of these things is not like the others; one of these things just doesn’t belong.](http://muppet.wikia.com/wiki/One_of_These_Things)


## Don’t Use Those Threads Either


Options 1-3 are all ways of representing the cooperative transfer of control within a stateful system. They are a semantic improvement over threads. Callbacks, Futures, and Yield-based coroutines all allow for local reasoning about concurrent operations.


So why does option 4 even show up in this list?


Unfortunately, “asynchronous” systems have often been evangelized by emphasizing [a somewhat dubious](http://stackoverflow.com/a/17771219/13564) optimization which allows for a higher level of I/O-bound concurrency than with preemptive threads, rather than the problems with threading as a programming model that I’ve explained above. By characterizing “asynchronousness” in this way, it makes sense to lump all 4 choices together.


I’ve been guilty of this myself, especially in years past: saying that a system using Twisted is more efficient than one using an alternative approach using threads. In many cases that’s been true, but:


1. the situation is almost always more complicated than that, when it comes to performance,
2. “context switching” is rarely a bottleneck in real-world programs, and
3. it’s a bit of a distraction from the much bigger advantage of event-driven programming, which is simply that it’s easier to write programs at scale, in both senses (that is, programs containing lots of code as well as programs which have many concurrent users).


A system that presents “implicit coroutines” – those which may transfer control to another concurrent task at any layer of the stack without any syntactic indication that this may happen – are simply the dubious optimization by itself.


Despite the fact that implicit coroutines masquerade under many different names, many of which don’t include the word “thread” – for example, “greenlets”, “coroutines”, “fibers”, “tasks” – green or lightweight threads are indeed threads, in that they present these same problems. In the long run, when you build a system that relies upon them, you eventually have all the pitfalls and dangers of full-blown preemptive threads. Which, as shown above, are bad.


When you look at the implementation of a potentially concurrent routine written using callbacks or yielding coroutines, you can visually see exactly where it might yield control, either to other routines, or perhaps even re-enter the same routine concurrently. If you are using callbacks – managed or otherwise – you will see a return statement, or the termination of a routine, which allows execution of the main loop to potentially continue. If you’re using explicit coroutines, you’ll see a yield (or await) statement which suspends the coroutine. Because you can see these indications of potential concurrency, they’re outside of your mind, in your text editor, and you don’t need to actively remember them as you’re working on them.


You can think of these explicit yield-points as places where your program may gracefully bend to the needs of concurrent inputs. [Crumple zones](https://en.wikipedia.org/wiki/Crumple_zone), or [relief valves](https://en.wikipedia.org/wiki/Relief_valve), for your logic, if you will: a single point where you have to consider the implications of a transfer of control to other parts of your program, rather than a rigid routine which might transfer (break) at any point beyond your control.


Like crumple zones, you shouldn’t have too many of them, or they lose their effectiveness. A long routine which has an explicit yield point before every single instruction requires just as much out-of-order reasoning, and is therefore just as error-prone as one which has none, but might context switch before any instruction anyway. The advantage of having to actually insert the yield point explicitly is that at least you can see when a routine has this problem, and start to clean up and consolidate the mangement of its concurrency.


But this is all pretty abstract; let me give you a specific practical example, and a small theoretical demonstration.


## The Buggiest Bug


When we wrote the very first version of [Twisted](https://www.twistedmatrix.com/) [Reality](https://launchpad.net/imaginary) in Python, the version we had previously written in Java was already using green threads; at the time, the JVM didn’t have any other kind of threads. The advantage to the new networking layer that we developed was not some massive leap forward in performance (the software in question was a multiplayer text adventure, which at the absolute height of its popularity might have been played by 30 people simultaneously) but rather the dramatic reduction in the number and severity of horrible, un-traceable concurrency bugs. One, in particular, involved a brass, mechanical cockroach which would crawl around on a timer, leaping out of a player’s hands if it was in their inventory, moving between rooms if not. In the multithreaded version, the cockroach would leap out of your hands but then also still stay in your hands. As the cockroach moved between rooms it would create [shadow copies](http://naruto.wikia.com/wiki/Shadow_Clone_Technique) of itself, slowly but inexorably creating a cockroach apocalypse as tens of thousands of pointers to the cockroach, each somehow acquiring their own timer, scuttled their way into every player’s inventory dozens of times.


Given that the feeling that this particular narrative feature was supposed to inspire was eccentric whimsy and not existential terror, the non-determinism introduced by threads was a serious problem. Our hope for the even-driven re-write was simply that we’d be able to diagnose the bug by single-stepping through a debugger; instead, the bug simply disappeared. (Echoes of this persist, in that you may rarely hear a particularly grizzled Twisted old-timer refer to a particularly intractable bug as a “[brass cockroach](http://brasscockroach.com/)”.)


The original source of the bug was so completely intractable that the only workable solution was to re-write the entire system from scratch. Months of debugging and testing and experimenting could still reproduce it only intermittently, and several “fixes” (read: random, desperate changes to the code) never resulted in anything.


I’d rather not do that ever again.


## Ca(sh|che Coherent) Money

Despite the (I hope) entertaining nature of that anecdote, it still might be somewhat hard to visualize how concurrency results in a bug like that, and the code for that example is far too sprawling to be useful as an explanation. So here's a smaller in vitro example. Take my word for it that the source of the above bug was the result of many, many intersecting examples of the problem described below.


As it happens, this is the same variety of example Guido van Rossum gives when he describes why chose to use explicit coroutines instead of green threads for the [upcoming standard library `asyncio` module](http://www.python.org/dev/peps/pep-3156/), born out of the “tulip” project, so it's happened to more than one person in real life.


Let’s say we have this program:


```python

def transfer(amount, payer, payee, server):
    if not payer.sufficient_funds_for_withdrawl(amount):
        raise InsufficientFunds()
    log("{payer} has sufficient funds.", payer=payer)
    payee.deposit(amount)
    log("{payee} received payment", payee=payee)
    payer.withdraw(amount)
    log("{payer} made payment", payer=payer)
    server.update_balances([payer, payee])
```


(I realize that the ordering of operations is a bit odd in this example, but it makes the point easier to demonstrate, so please bear with me.)


In a world without concurrency, this is of course correct. If you run transfer twice in a row, the balance of both accounts is always correct. But if we were to run transfer with the same two accounts in an arbitrary number of threads simultaneously, it is (obviously, I hope) wrong. One thread could update a payer’s balance below the funds-sufficient threshold after the check to see if they’re sufficient, but before issuing the withdrawl.


So, let’s make it concurrent, in the [PEP 3156](http://www.python.org/dev/peps/pep-3156/) style. That `update_balances` routine looks like it probably has to do some network communication and block, so let’s consider that it is as follows:


```python
@coroutine
def transfer(amount, payer, payee, server):
    if not payer.sufficient_funds_for_withdrawl(amount):
        raise InsufficientFunds()
    log("{payer} has sufficient funds.", payer=payer)
    payee.deposit(amount)
    log("{payee} received payment", payee=payee)
    payer.withdraw(amount)
    log("{payer} made payment", payer=payer)
    yield from server.update_balances([payer, payee])
```


So now we have a trivially concurrent, correct version of this routine, although we did have to update it a little. Regardless of what `sufficient_funds_for_withdrawl`, `deposit` and `withdrawl` do - even if they do network I/O - we know that we aren’t waiting for any of them to complete, so they can’t cause `transfer` to interfere with itself. For the sake of a brief example here, we’ll have to assume `update_balances` is a bit magical; for this to work our reads of the payer and payee’s balance must be consistent.


But if we were to use green threads as our “asynchronous” mechanism rather than coroutines and yields, we wouldn’t need to modify the program at all! Isn’t that better? And only `update_balances` blocks anyway, so isn’t it just as correct?


Sure: for now.

But now let’s make another, subtler code change: our hypothetical operations team has requested that we put all of our log messages into a networked log-gathering system for analysis. A reasonable request, so we alter the implementation of `log` to write to the network.

Now, what will we have to do to modify the green-threaded version of this code? Nothing! This is usually the point where fans of [various](http://eventlet.net/) [green-threading](http://gevent.org/) [systems](http://www.stackless.com/) will point and jeer, since once the logging system is modified to do its network I/O, you don’t even have to touch the code for the payments system. Separation of concerns! Less pointless busy-work! Looks like the green-threaded system is winning.


Oh well. Since I’m still a fan of explicit concurrency management, let’s do the clearly unnecessary busy-work of updating the ledger code.


```python
@coroutine
def transfer(amount, payer, payee, server):
    if not payer.sufficient_funds_for_withdrawl(amount):
        raise InsufficientFunds()
    yield from log("{payer} has sufficient funds.", payer=payer)
    payee.deposit(amount)
    yield from log("{payee} received payment", payee=payee)
    payer.withdraw(amount)
    yield from log("{payer} made payment", payer=payer)
    yield from server.update_balances([payer, payee])
```


Well okay, at least that wasn’t too hard, if somewhat tedious. Sigh. I guess we can go update all of the ledger’s callers now and update them too…


…wait a second.


In order to update this routine for a non-blocking version of `log`, we had to type a `yield` keyword between the `sufficient_funds_for_withdrawl` check and the `withdraw` call, between the `deposit` and the `withdraw` call, and between the withdraw and `update_balances` call. If we know a little about concurrency and a little about what this program is doing, we know that every one of those `yield froms` are a potential problem. If those `log` calls start to back up and block, a payer may have their account checked for sufficient funds, then funds could be deducted while a log message is going on, leaving them with a negative balance.


If we were in the middle of updating lots of code, we might have blindly added these `yield` keywords without noticing that mistake. I've certainly done that in the past, too. But just the mechanical act of typing these out is an opportunity to notice that something’s wrong, both now and later. Even if we get all the way through making the changes without realizing the problem, when we notice that balances are off, we can look only (reasoning locally!) at the `transfer` routine and realize, when we look at it, based on the presence of the `yield from` keywords, that there is something wrong with the `transfer` routine itself, regardless of the behavior of any of the things it’s calling.


In the process of making all these obviously broken modifications, another thought might occur to us: do we really need to wait before log messages are transmitted to the logging system before moving on with our application logic? The answer would almost always be “no”. A smart implementation of log could simply queue some outbound messages to the logging system, then discard if too many are buffered, removing any need for its caller to honor backpressure or slow down if the logging system can’t keep up. Consider the way syslog says “and N more” instead of logging certain messages repeatedly. That feature allows it to avoid filling up logs with repeated messages, and decreases the amount of stuff that needs to be buffered if writing the logs to disk is slow.


All the extra work you need to do when you update all the callers of `log` when you make it asynchronous is therefore a feature. Tedious as it may be, the asynchronousness of an individual function is, in fact, something that all of its callers must be aware of, just as they must be aware of its arguments and its return type.


In fact you are changing its return type: in Twisted, that return type would be `Deferred`, and in Tulip, that return type is a new flavor of generator. This new return type represents the new semantics that happen when you make a function start having concurrency implications.


Haskell does this as well, by embedding the IO monad in the return type of any function which needs to have side-effects. This is what certain people mean when they say [Deferreds are a Monad](http://static.mumak.net/Twisted-Monads.pdf).


The main difference between lightweight and heavyweight threads is that it is that, with rigorous application of strict principles like “never share any state unnecessarily”, and “always write tests for every routine at every point where it might suspend”, lightweight threads make it at least possible to write a program that will behave deterministically and correctly, assuming you understand it in its entirety. When you find a surprising bug in production, because a routine that is now suspending in a place it wasn’t before, it’s possible with a lightweight threading system to write a deterministic test that will exercise that code path. With heavyweight threads, any line could be the position of a context switch at any time, so it’s just not tractable to write tests for every possible order of execution.


However, with lightweight threads, you still can’t write a test to discover when a new yield point might be causing problems, so you're still always playing catch-up.


Although it’s possible to do this, it remains very challenging. As I described above, in languages like Python, Ruby, JavaScript, and PHP, even the code itself is shared, mutable state. Classes, types, functions, and namespaces are all shared, and all mutable. Libraries like object relational mappers commonly store state on classes.


## No Shortcuts


Despite the great deal of badmouthing of threads above, my main purpose in writing this was not to convince you that threads are, in fact, bad. (Hopefully, you were convinced before you started reading this.) What I hope I’ve demonstrated is that if you agree with me that threading has problematic semantics, and is difficult to reason about, then there’s no particular advantage to using microthreads, beyond potentially optimizing your multithreaded code for a very specific I/O bound workload.


There are no shortcuts to making single-tasking code concurrent. It's just a hard problem, and some of that hard problem is reflected in the difficulty of typing a bunch of new concurrency-specific code.


So don’t be fooled: a thread is a thread regardless of its color. If you want your program to be supple and resilient in the face of concurrency, when the storm of concurrency blows, allow it to change. Tell it to yield, just like the reed. Otherwise, just like the steadfast and unchanging oak tree in the storm, your steadfast and unchanging algorithms will break right in half.