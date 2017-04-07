
(
var notes;

SynthDef.new(\sineSynth, {|freq=#[1,2,3,4,5]|
	var sig, env;
	sig = SinOsc.ar(freq, 5, 0.2)!2;
	env = EnvGen.kr(Env.perc(0.1, 1, 1, -8), doneAction:2);
	Out.ar([0,1], sig * env * 0.4);
}).add;


n = NetAddr.new("127.0.0.1", 57120);    // create the NetAddr
// create the OSCresponderNode
f = {
	arg msg, time, addr;
	if(msg[0] == '/cnn_midi') {
		notes = msg.asInteger;
		notes[1..5].postln;
		x = Synth.new(\sineSynth, [\freq, notes.midicps]);
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



