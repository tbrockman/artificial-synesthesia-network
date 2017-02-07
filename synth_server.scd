NetAddr.langPort;
NetAddr.localAddr;

n = NetAddr.new("127.0.0.1", 7771);    // create the NetAddr
// create the OSCresponderNode
o = OSCFunc({ arg msg, time, addr, recvPort; [msg, time, addr, recvPort].postln; }, '/goodbye', n);
o.free;    // remove the OSCFunc when you are done.
OSCFunc.trace(true); // Turn posting on