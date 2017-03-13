(
var notes;

SynthDef(\rhodey_sc, {
    |
	// «FM Rhodes» by snappizz
	// http://sccode.org/1-522
    // standard meanings
    out = 0, freq = 440, gate = 1, pan = 0, amp = 0.1,
    // all of these range from 0 to 1
    vel = 0.8, modIndex = 0.2, mix = 0.2, lfoSpeed = 0.4, lfoDepth = 0.1
    |
    var env1, env2, env3, env4;
    var osc1, osc2, osc3, osc4, snd;

    lfoSpeed = lfoSpeed * 12;

    freq = freq * 2;

    env1 = EnvGen.ar(Env.adsr(0.001, 1.25, 0.0, 0.04, curve: \lin));
    env2 = EnvGen.ar(Env.adsr(0.001, 1.00, 0.0, 0.04, curve: \lin));
    env3 = EnvGen.ar(Env.adsr(0.001, 1.50, 0.0, 0.04, curve: \lin));
    env4 = EnvGen.ar(Env.adsr(0.001, 1.50, 0.0, 0.04, curve: \lin));

    osc4 = SinOsc.ar(freq * 0.5) * 2pi * 2 * 0.535887 * modIndex * env4 * vel;
    osc3 = SinOsc.ar(freq, osc4) * env3 * vel;
    osc2 = SinOsc.ar(freq * 15) * 2pi * 0.108819 * env2 * vel;
    osc1 = SinOsc.ar(freq, osc2) * env1 * vel;
    snd = Mix((osc3 * (1 - mix)) + (osc1 * mix));
    snd = snd * (SinOsc.ar(lfoSpeed) * lfoDepth + 1);

    // using the doneAction: 2 on the other envs can create clicks (bc of the linear curve maybe?)
    snd = snd * EnvGen.ar(Env.asr(0, 1, 0.1), gate, doneAction: 2);
    snd = Pan2.ar(snd, pan, amp);

    Out.ar(out, snd);
}).add;


n = NetAddr.new("127.0.0.1", 57120);    // create the NetAddr
// create the OSCresponderNode
f = {
	arg msg, time, addr;
	if(msg[0] == '/cnn_midi') {
		notes = msg.asInteger;
		notes[1..5].postln;
		(

			Pbind(
				\instrument, \rhodey_sc,
				\midinote, Pseq([notes[1..5]]),
				\mix, 0.2,
				\modIndex, 0.2,
				\lfoSpeed, 0.5,
				\lfoDepth, 0.4,
				\dur, 0.5,
				\amp, 0.3,
			).play;

		)
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
