(
SynthDef(\sinewave,{|freq = 440|
var output = SinOsc.ar(freq, 0 ,0.1);
Out.ar([0,1], output);
}).send;
)

(

var note;

x = Synth(\sinewave);

n = NetAddr.new("127.0.0.1", 57120);    // create the NetAddr
// create the OSCresponderNode
f = {
	arg msg, time, addr;
	if(msg[0] == '/cnn_midi') {
		note = msg.asInteger;
		x.set(\freq, note[1].midicps);
	}
};
thisProcess.addOSCRecvFunc(f);
)



(
MIDIClient.init;
MIDIIn.connectAll;
MIDIdef.noteOn(\noteOn, {
	arg vel, note, chan, src;
	[vel, note].postln;
	{
		var sig, env;
		sig = SinOsc.ar(note.midicps)!2;
		env = EnvGen.kr(Env.perc, doneAction:2);
		sig = sig * env * vel.linexp(1,127,0.01,0.3);
	}.play;
});
)

s.boot;