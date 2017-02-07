(
var test;

n = NetAddr.new("127.0.0.1", 7771);    // create the NetAddr
// create the OSCresponderNode
test = 1;
o = OSCFunc({
	arg msg, time, addr, recvPort;
	[msg, time, addr, recvPort].postln;
	test = msg;
}, '/goodbye', n);
OSCFunc.trace(true); // Turn posting on

MIDIClient.init;
MIDIIn.connectAll;

(
MIDIdef.noteOn(\noteOn, {
	arg vel, note, chan, src;
	[vel, note].postln;
	{
		var sig, env;
		sig = SinOsc.ar(note.midicps)!2;
		env = EnvGen.kr(Env.perc, doneAction:2);
		sig = sig * env * vel.linexp(1,127,0.01,0.3) * test;
	}.play;
});
)

)

s.boot;