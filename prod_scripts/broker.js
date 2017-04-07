const WebSocket = require('ws');

const wss = new WebSocket.Server({
  perMessageDeflate: false,
  port: 8888
});

let data = {};

wss.on('connection', function conn(ws) {
	ws.type = "";

	ws.on('message', function incoming(msg) {
		console.log("Got: ", msg);
		try {
			json = JSON.parse(msg);
		} catch(e)  {
			console.log("Invalid JSON!");
			return;
		}

		switch(json.type) {
			case "launch":
				if (json.command == undefined || json.args == undefined){
					console.log("Invalid launch message");
					break;
				}
				launch(json.command, json.args, cb1);
				break;
			case "node":
				if (json.type == undefined || json.hostname == undefined) {
					console.log("Invalid node message");
					break;
				}
				ws.type = "node";
				ws.hostname = json.hostname;
				break;
			case "data":
				//Group by hostname?
				if (json.hostname == undefined) {
					console.log("Invalid data message");
					break;
				}
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
