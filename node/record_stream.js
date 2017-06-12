/**
 * Created by bb on 6/7/2017.
 */
/**
 * Created by bb on 5/29/2017.
 */

'use strict';
//
// /** playback audio for mac os x*/
// var audio = require('osx-audio');
// var input = new audio.Input();

const record = require('node-record-lpcm16');
var Speech = require('@google-cloud/speech');  // Imports the Google Cloud client library
var fs = require('fs');
var net = require('net');

var speech = Speech({
    projectId: 'tenence-167415',
    keyFilename: 'credentials.json'
});

/** Set const for recording.*/
const encoding = 'LINEAR16';  // The encoding of the audio file
const sampleRateHertz = 16000;  // The sample rate of the audio file in hertz
const languageCode = 'en-US';

var request = {
    config: {
        encoding: encoding,
        sampleRateHertz: sampleRateHertz,
        languageCode: languageCode
    },
    interimResults: false // If you want interim results, set this to true
};

/**
 * Create Socket Server.
 */
var server = net.createServer(function(socket) {
    console.log('Server started: Waiting for client connection ...');
    console.log('Client connected:port,address: '+socket.remotePort,      socket.remoteAddress);

    socket.on('data', function (data) {
        console.log(data.toString());
        if (data.toString() == 'Start') {
            console.log('Listening....');
            streaming_speech(socket);
        }
    });

    socket.on('close', function(data) {
        console.log('CLOSED: ' + socket.remoteAddress +' '+ socket.remotePort);
    });
});

server.listen(10000, '127.0.0.1');


/** Main Function*/
function streaming_speech(socket) {
    try {
        /** Converting text from streaming voice using google cloud speech api.*/

        var recognizeStream = speech.createRecognizeStream(request)

            .on('error', (err) => {
                console.log("Speech API ERROR: " + err);
            })

            .on('data', (data) => {
                // input.pipe(data);
                var transcription = data.results;
                socket.write(transcription);
                console.log(`Transcription: ${transcription}`);
                record.stop();
            });

        // fs.createReadStream('audio2.raw').pipe(recognizeStream);
        /** Start recording and send the microphone input to the Speech API.*/
        record
            .start({
                sampleRateHertz: sampleRateHertz,
                threshold: 0,
                verbose: false,
                recordProgram: 'rec',
                silence: '10.0'

            })
            .on('error', console.error)
            .pipe(recognizeStream);
    }
    catch (e) {
        console.log('error ' + e);
    }
}