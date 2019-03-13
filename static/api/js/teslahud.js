'use strict';
let graph_size = 300;
let dev = false;
var c = document.getElementById("canvas");
c.width = graph_size;
c.height = graph_size;
var ctx = c.getContext("2d");
ctx.scale(1, 1);
var speedGradient = ctx.createLinearGradient(0, graph_size, 0, 0);
speedGradient.addColorStop(0, '#00b8fe');
speedGradient.addColorStop(1, '#41dcf4');
var rpmGradient = ctx.createLinearGradient(0, graph_size, 0, 0);
rpmGradient.addColorStop(0, '#f7b733');
rpmGradient.addColorStop(1, '#fc4a1a');

function speedNeedle(rotation)
{
	ctx.lineWidth = 2;
	ctx.save();
	ctx.translate( graph_size / 2,  graph_size / 2 );
	ctx.rotate(rotation);
	ctx.strokeRect(-( graph_size / ( 50 / 13 ) ) / 2 + ( graph_size / ( 50 / 17 ) ), -1 / 2, ( graph_size / ( 100 / 27 ) ), 1);
	ctx.restore();
	rotation += Math.PI / 180;
}

function rpmNeedle(rotation)
{
	ctx.lineWidth = 2;
	ctx.save();
	ctx.translate( graph_size / 2,  graph_size / 2 );
	ctx.rotate(rotation);
	ctx.strokeRect(-( graph_size / ( 50 / 13 ) ) / 2 + ( graph_size / ( 50 / 17 ) ), -1 / 2, ( graph_size / ( 100 / 27 ) ), 1);
	ctx.restore();
	rotation += Math.PI / 180;
}

function drawMiniNeedle(rotation, width, speed)
{
	ctx.lineWidth = width;
	ctx.save();
	ctx.translate( graph_size / 2, graph_size / 2);
	ctx.rotate(rotation);
	ctx.strokeStyle = "#333";
	ctx.fillStyle = "#333";
	ctx.strokeRect(-20 / 2 + ( graph_size / ( 25 / 11 ) ), -1 / 2, graph_size / 25, 1);
	ctx.restore();
	let x = ( ( graph_size / 2 ) + ( graph_size / ( 25 / 8 ) ) * Math.cos(rotation));
	let y = ( ( graph_size / 2 ) + ( graph_size / ( 25 / 8 ) ) * Math.sin(rotation));
	ctx.font = `${graph_size / 20}px MuseoSans_900-webfont`;
	ctx.fillText(speed, x, y);
	rotation += Math.PI / 180;
}

function calculateSpeedAngle(x, a, b)
{
	let degree = (a - b) * (x) + b;
    let radian = (degree * Math.PI) / 180;
    let res = radian <= 1.45 ? radian : 1.45;
    //console.log(`calculateSpeedAngle(${x}, ${a}, ${b}): ${res}`);
	return res;
}

function calculateRPMAngle(x, a, b)
{
	let degree = (a - b) * (x) + b;
	let radian = (degree * Math.PI) / 180;
    let res = radian >= -0.46153862656807704 ? radian : -0.46153862656807704;
    //console.log(`calculateRPMAngle(${x}, ${a}, ${b}): ${res}`);
    return res;
}

function drawSpeedo(speed, gear, rpm, topSpeed)
{
	if (speed == undefined)
	{
		return false;
	}
	else
	{
		speed = Math.floor(speed);
		rpm = rpm * 10;
	}
	ctx.clearRect(0, 0, graph_size, graph_size);
	ctx.beginPath();
	ctx.fillStyle = 'rgba(0, 0, 0, .9)';
	ctx.arc(graph_size /2 , graph_size /2 , graph_size / ( 25 / 12 ), 0, 2 * Math.PI);
	ctx.fill();
	ctx.save()
	ctx.restore();
	ctx.fillStyle = "#FFF";
	ctx.stroke();
	ctx.beginPath();
	ctx.strokeStyle = "#333";
	ctx.lineWidth = graph_size / 80;
	ctx.arc(graph_size / 2, graph_size / 2, graph_size / 5, 0, 2 * Math.PI);
	ctx.stroke();
	ctx.beginPath();
	ctx.lineWidth = 1;
	ctx.arc(graph_size / 2 , graph_size / 2 , graph_size / ( 25 / 12 ), 0, 2 * Math.PI);
	ctx.stroke();
	ctx.font = `${graph_size / ( 80 / 7 )}px MuseoSans_900-webfont`;
	ctx.textAlign = "center";
	ctx.fillText(speed, graph_size / 2, graph_size / ( 50 / 23 ) );                                          // Pinta la velocidad en el centro
	ctx.font = `${graph_size / ( 160 / 9 )}px MuseoSans_900-webfont`;
	ctx.fillText("%", graph_size / 2, graph_size / ( 25 / 13 ) );                                            // Pinta %
	ctx.fillStyle = "#FFF";
	for (var i = 10; i <= Math.ceil(topSpeed / 20) * 20; i += 10)
	{
		console.log();
		drawMiniNeedle(calculateSpeedAngle(i / topSpeed, 83.07888, 34.3775) * Math.PI, i % 20 == 0 ? 3 : 1, i % 20 == 0 ? i : '');
		if (i <= 100)                                                       // Para pintar los pasos del RPM
		{
			drawMiniNeedle(calculateSpeedAngle(i / 47, 0, 22.9183) * Math.PI, i % 20 == 0 ? 3 : 1, i % 20 == 0 ? i / 10 : '');
		}
	}
	ctx.beginPath();
	ctx.strokeStyle = "#41dcf4";
	ctx.lineWidth = graph_size / 20;
	ctx.shadowBlur = graph_size / 25;
	ctx.shadowColor = "#00c6ff";
	ctx.strokeStyle = speedGradient;
	ctx.arc( graph_size / 2, graph_size / 2, graph_size / ( 125 / 57 ), .6 * Math.PI, calculateSpeedAngle(speed / topSpeed, 83.07888, 34.3775) * Math.PI);
	ctx.stroke();
	ctx.beginPath();
	ctx.lineWidth = graph_size / 20;
	ctx.strokeStyle = rpmGradient;
	ctx.shadowBlur = graph_size / 25;
	ctx.shadowColor = "#f7b733";
	ctx.arc(graph_size / 2, graph_size / 2, graph_size / ( 125 / 57 ), .4 * Math.PI, calculateRPMAngle(rpm / 4.7, 0, 22.9183) * Math.PI, true);
	ctx.stroke();
	ctx.shadowBlur = 0;
	ctx.strokeStyle = '#41dcf4';
	speedNeedle(calculateSpeedAngle(speed / topSpeed, 83.07888, 34.3775) * Math.PI);
	ctx.strokeStyle = rpmGradient;
	rpmNeedle(calculateRPMAngle(rpm / 4.7, 0, 22.9183) * Math.PI);
	ctx.strokeStyle = "#000";
}