const spawn = require('child_process').spawn;
const http = require('http');
const port = 3000;
const extend = require('util')._extend;

let processes = [];

function launch(command, opts, cb) {
	var process = spawn(command, opts);
	var np = {
		command,
		opts,
		process,
		stdout: [],
		stderr: []
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
		data: (process) => {
			return (data) => {
				process.stdout.push(data.toString());
				//emit last data
			}
		}
	},
	stderr: {
		data: (process) => {
			return (data) => {
				const d = data.toString();
				if (d.endsWith("\r"))
					process.stderr[process.stderr.length-1] = d;
				else
					process.stderr.push(d);
			}
		}
	},
	close: function(process) {
		return function(code){
			console.log("Child exited with code", code, process.pid);
		}
	},
	error: (process) => {
		return function(err) {
			console.log(`F: Failed to start '${err.path}' with args '${err.spawnargs}', code: ${err.code}`);
		}
	}
};


//exitCode !== null
launch("/var/voctomix/voctocore/voctocore.py", ["-vv"], cb1);
setTimeout( () => {
	launch("/var/voctomix/prod_scripts/modes.sh", ["start"], cb1);
	launch("/var/voctomix/prod_scripts/source-audio-as-audio1.sh", [], cb1);
	launch("/var/voctomix/prod_scripts/source-still-image-as-background-loop.sh", [], cb1);
	launch("/var/voctomix/prod_scripts/dumb-slides.sh", [], cb1);
	launch("/var/voctomix/prod_scripts/cam-selector.py", [], cb1);
	launch("/var/voctomix/prod_scripts/stream-sd.sh", [], cb1);
	}, 1000);



const requestHandler = (request, response) => {  
	const printable = processes.map( e => {
		let ret = extend({}, e);
		ret.process = { pid: e.process.pid, exitCode: e.process.exitCode };
		return ret;
	});
	switch(request.url){
		case '/write/':
			//writeTo("cam-selector", "2\n");
			let process = processes.filter( p => { return /cam-selector/.test(p.command) } )[0].process;
			process.stdin.write("2\n");
			break;
		default:
			response.end(JSON.stringify(printable));
			break;
	}
}

const server = http.createServer(requestHandler)

server.listen(port, (err) => {  
	if (err) {
		return console.log('something bad happened', err)
	}
});
