const WebSocket = require('ws');

const wss = new WebSocket.Server({
  perMessageDeflate: false,
  port: 8888
});

let data = {};

wss.on('connection', function conn(ws) {
	ws.type = "";
	ws.send(JSON.stringify(data));
	ws.on('message', function incoming(msg) {
		console.log("Got: ", msg, " from: ", ws.hostname);
		try {
			json = JSON.parse(msg);
		} catch(e)  {
			console.log("Invalid JSON!");
			return;
		}

		switch(json.type) {
			case "launch":
				if (json.command == undefined || json.args == undefined || json.hostname == undefined){
					console.log("Invalid launch message");
					break;
				}
				sendTo(json.hostname, json);
				break;
			case "node":
				if (json.type == undefined || json.hostname == undefined) {
					console.log("Invalid node message");
					break;
				}
				ws.type = "node";
				ws.hostname = json.hostname;
				data[ws.hostname] = [];
				break;
			case "close":
				break;
			case "error":
				break;
			case "append":
				let el = data[ws.hostname].find( (e) => { e.pid === json.pid } );
				if ( el !== undefined ) {
					el[json.stream].push(json.data);	
				} else {
					data[ws.hostname].push(json);
				}
				wss.broadcast(json);
				break;
		}
	});
});

wss.broadcast = function broadcast(data) {
	wss.clients.forEach(function each(client) {
		if (client.readyState === WebSocket.OPEN && 
			client.type !== "node") {
			client.send(JSON.stringify(data));
		}
	});
};

function sendTo(hostname, data) {
	wss.clients.forEach((client) => {

		if ( client.hostname !== hostname ||
			 client.readyState !== WebSocket.OPEN ||
			 client.type !== "node") 
			 return;

		client.send(JSON.stringify(data));
	});
}
