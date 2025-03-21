Title: Debugging the Arduino WiFi Shield
Date: Tue 01 April 2014

### The Problem

After disconnecting from the internet, the Arduno WiFi shield (sitting atop an
Uno) is able to reconnect, but cannot re-start a server.

For example, here's the output of running the built-in `SimpleWebServerWiFi`
sketch (you can find it in the Arduino IDE under File > Examples > WiFi >
SimpleWebServerWiFi).

    
        Attempting to connect to Network named: <my network>
    SSID: <my network>
    IP Address: <my IP>
    signal strength (RSSI):-46 dBm
    To see this page in action, open a browser to http://<my IP>
    

Great - I think I'm connected! I can successfully ping the Arduino's IP
address:

    
        $ ping <my IP>
    PING <my IP> (<my IP>): 56 data bytes
    64 bytes from <my IP>: icmp_seq=0 ttl=255 time=4.371 ms
    64 bytes from <my IP>: icmp_seq=1 ttl=255 time=6.826 ms
    64 bytes from <my IP>: icmp_seq=2 ttl=255 time=17.500 ms
    64 bytes from <my IP>: icmp_seq=3 ttl=255 time=5.556 ms
    64 bytes from <my IP>: icmp_seq=4 ttl=255 time=7.440 ms
    ^C
    --- <my IP> ping statistics ---
    5 packets transmitted, 5 packets received, 0.0% packet loss
    round-trip min/avg/max/stddev = 4.371/8.339/17.500/4.701 ms
    

But I can’t complete HTTP requests:

    
        $ curl -G http://<my IP>
    curl: (7) Failed connect to <my IP>:80; Connection refused
    

And using telnet is just weird:

    
        $ telnet <my IP>
    Trying <my IP>...
    Connected to <my IP>.
    Escape character is '^]'.
    Hello, client!
    ^C^] Iso conf am uso confsued^Msed?? // should be 'I am so confused??'
    

### Getting started

To test what happens when the Arduino disconnects from the WiFi network, I
wrote some code to automatically disconnect every tenth time through Arduino's
event loop, `loop()`.

    
        void loop() {
      if (i % 10 == 0) {
    Serial.println("\nPurposely disconnecting WiFi\n");
    WiFi.disconnect();
    delay(5000);
    WiFiSetup();
      }
      i = i + 1;
    }
    

What happens? The server restarts every time, but on a different socket \- and
it leaves the old socket in use. This means that after 4 tries (there are 4
sockets) it can’t restart anymore. I also think it could be creating the
strange client connection problems - because socket 0 is never closed, the
client always tries to connect to it, but the server is actually on socket
1... or 2... or 3...

#### Idea #1: Call `client.stop()`

Another Hacker Schooler with more networking experience than I have thought
that calling `client.stop()` might stop the server manually. His hypothesis
was that Arduino’s 'client' is actually what most networking libraries call a
'socket', and that stopping the client might close the socket.

I wrote a simple sketch to test it, but it didn't work: `client.stop()` stops
the client, but not the server. At least that's expected behavior!

#### Idea #2: Mimic solution to Arduino issue #1720

I found a relevant-seeming issue on Github: [WiFi shield client does not
release socket on connect
fail](https://github.com/Arduino/Arduino/issues/1720). The poster fixed the
problem by editing `connect()` in WiFiClient.cpp, specifically by adding this
single line to `WiFiClient::connect()`:

    
        if (!connected())
    {
    // Add this
        WiFiClass::_state[_sock] = -1;
    // end of add
    
        return 0;
        }
    

This line runs if the client fails to connect; it resets the socket to make it
available for another client.

My problem isn't exactly the same as this one - I'm dealing with a dropped
connection, not a failed connect attempt, and with a server, not a client -
but it seems similar enough to use as inspiration.

It seems like I want something similar, but in some `disconnect()` method, so
that the socket is closed when the WiFi disconnects.

The WiFi shield does have a `disconnect()` method, located in WiFi.cpp, which
then points to a method in utility/WiFi_drv.cpp. Great. `disconnect()` issues
actual assembly commands. I really didn't want to debug Assembly (well, at
least not that day). I moved on for the moment.

### Some success! The server re-starts

With the help of #1720 above, I figured out that the state of the WiFi
object's sockets is stored in an array called `_state`, and the port running
on each socket is stored in an array called `_server_port`.

If a socket is not in use, its state is -1 and its port is 0. If it's being
used, its state is equal to the socket number and the port is the number of of
whatever port it's running on. So if `_state` is `[-1, -1, 2, -1]` and
`_server_port` is `[0, 0, 80, 0]`, that indicates that a server is using
socket 2 and listening on port 80.

These numbers weren't being reset when the WiFi disconnected, which meant that
the server couldn't restart properly. To fix it, I created a `disconnect()`
method in WiFiServer.cpp:

    
        void WiFiServer::disconnect() {
      WiFiClass::_state[_sock] = -1;
      WiFiClass::_server_port[_sock] = 0;
    }
    

This frees the socket the server was listening on by setting its state to -1
and shuts down the port by resetting it from 80 to 0.

Cool! That worked! Sort of. Now I can release the socket and port, and re-
connect to them. The problem is that the server doesn’t actually restart.

Fortunately, I discovered that this problem had a simple fix: delaying before
restarting the WiFi. Adding the line `delay(10000);` before running
`WiFiSetup()` does the trick:

    
        void loop() {
    Serial.println("\nPurposely disconnecting WiFi\n");
    server.disconnect();
    WiFi.disconnect();
    delay(10000);
    WiFiSetup();
    }
    

### Big problem: the client doesn't restart

This is where I got stuck: restarting the server after a client has connected
to it. Even though `client.stop()` is always called before the WiFi is
disconnected, things don't go smoothly.

In my test sketches, I always examine the Arduino's sockets, ports, and server
and client states before reconnecting, just to make sure they were reset
properly. When I examine the client using `serverDrv.getClientState()`,
everything - _everything_ \- hangs indefinitely:

    
        Purposely disconnecting WiFi
    
    ********************************
    
    Initial socket status (before new connection):
    -1  0  s=0  c=
    

Even weirder is that the client doesn’t _always_ get in the way - a couple of
times, things have worked 100% perfectly (started server, sent message from
client, disconnected WiFi, reconnected server, successfully sent a new message
from client).

Every time I mentioned to people that I was experiencing a non-deterministic
bug, they started chanting, "Memory leak! Memory leak!". Fortunately, Arduino
has a function, `freeMemory()`, for reporting its available memory. I added
print statements everywhere to keep track of this, but found it never changed
significantly.

#### The big problem: no handshake!

I added print statements to that `serverDrv.getClientState()` so I could see
precisely where it got stuck. It's during the line
`SpiDrv::waitForSlaveReady()`. All this does is instruct the Arduino to wait
while a pin called `SLAVEREADY` \- the Arduino-WiFi Shield handshake pin - is
high.

    
        #define waitSlaveReady() (digitalRead(SLAVEREADY) == LOW)
    void SpiDrv::waitForSlaveReady()
    {
        while (!waitSlaveReady());
    }
    

No matter how long I wait, that friggin slave just isn't ready. If this is the
problem, I'm going to have to throw in the towel. There's no more code to
debug - I'd have to get out datasheets and begin from there.

* * *

###### Category: [misc](/category/misc.html).

* * *

![](/theme/img/headshot.png)

##### Links

[LinkedIn](http://www.linkedin.com/in/katrinaellison)

[GitHub](http://www.github.com/katrinae)

[SlideShare](http://www.slideshare.net/kellison00)

##### Monthly Archives

[December 2015 (1)](/posts/2015/12/)

[May 2014 (2)](/posts/2014/05/)

[April 2014 (3)](/posts/2014/04/)

[March 2014 (2)](/posts/2014/03/)

[February 2014 (2)](/posts/2014/02/)

* * *

Powered by Pelican and based on a theme by [Kenton
Hamaluik](http://hamaluik.com).

