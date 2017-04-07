const spawn = require('child_process').spawn;
const extend = require('util')._extend;
const os = require("os");
const WebSocket = require('ws');

const ROOTPATH = '/var/voctomix/';
const HOSTNAME = os.hostname();

let processes = [];

function launch(command, opts, cb) {
	var process = spawn(command, opts);
	if ( opts === undefined || opts === null )
		opts = [];

	var np = {
		command,
		opts,
		process,
		stdout: [],
		stderr: [],
		hostname: HOSTNAME
	};

	for( key in cb ) {
		if ( typeof cb[key] === "function" ) {
			process.on(key, cb[key](np));
			continue;
		}
		for ( ev in cb[key] ) {
			process[key].on(ev, cb[key][ev](np));
		}
	}
	processes.push(np);
}


const cb1 = {
	stdout: {
		data: (meta) => {
			return (data) => {
				const d = data.toString();
				meta.stdout.push(d);
				ws.sendObj({ type: 'append', pid: meta.process.pid, data: d, 'stream': 'stdout'});
			}
		}
	},
	stderr: {
		data: (meta) => {
			return (data) => {
				const d = data.toString();
				ws.sendObj({ type: 'append', pid: meta.process.pid, data: d, 'stream': 'stderr'});

				if (d.endsWith("\r"))
					meta.stderr[meta.stderr.length-1] = d;
				else
					meta.stderr.push(d);
			}
		}
	},
	close: function(meta) {
		return function(code){
			ws.sendObj({ type: 'close', 'pid': meta.process.pid, 'code': code });
			console.log("Child exited with code", code, meta.process.pid);
		}
	},
	error: (meta) => {
		return function(err) {
			ws.sendObj({ type: 'error', pid: meta.process.pid, 'error': err });
			console.log(`F: Failed to start '${err.path}' with args '${err.spawnargs}', code: ${err.code}`);
		}
	}
};


function launchCore() {
	launch(ROOTPATH + "voctocore/voctocore.py", ["-vv"], cb1);
	setTimeout( () => {
			launch(ROOTPATH + "prod_scripts/modes.sh", ["start"], cb1);
			launch(ROOTPATH + "prod_scripts/source-audio-as-audio1.sh", [], cb1);
			launch(ROOTPATH + "prod_scripts/source-still-image-as-background-loop.sh", [], cb1);
			launch(ROOTPATH + "prod_scripts/dumb-slides.sh", [], cb1);
			launch(ROOTPATH + "prod_scripts/cam-selector.py", [], cb1);
			launch(ROOTPATH + "prod_scripts/stream-sd.sh", [], cb1);
		}, 1000);
}

//setTimeout(launchCore, 1000);


const ws = new WebSocket('ws://192.168.2.123:8888');

ws.on('open', function open() {
	ws.sendObj({type: "node", hostname: HOSTNAME});
});

function printableProcesses() {
	return processes.map( e => {
		let ret = extend({}, e);
		ret.process = { pid: e.process.pid, exitCode: e.process.exitCode };
		return ret;
	});
}

ws.on('message', function incoming(data, flags) {
	console.log("Got data:", data);
	const json = JSON.parse(data);
	if ( json.type === undefined ) {
		console.log("No type");
		return;
	}
	switch(json.type) {
		case "launch":
			launch(json.command, json.args, cb1);
			break;
		default:
			console.log("Got invalid data!!");
			break;
	}
	
});

ws.sendObj = function(o) {
	ws.send(JSON.stringify(o));
}
//let process = processes.filter( p => { return /cam-selector/.test(p.command) } )[0].process;
//process.stdin.write("2\n");
