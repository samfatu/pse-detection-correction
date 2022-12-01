const EXTENSION_ID = 'gbdknfbioonlhgmfgfbjfienkjdbkfng'

const video = document.getElementById('screen-view');
const getScreen = document.getElementById('get-screen');
const stopScreen = document.getElementById('stop-screen');
const request = { sources: ['window', 'screen', 'tab'] };
let stream;

getScreen.addEventListener('click', event => {
  chrome.runtime.sendMessage(EXTENSION_ID, request, response => {
    if (response && response.type === 'success') {
      navigator.mediaDevices.getUserMedia({
        video: {
          mandatory: {
            chromeMediaSource: 'desktop',
            chromeMediaSourceId: response.streamId,
          }
        }
      }).then(returnedStream => {
        stream = returnedStream;
        video.srcObject = stream;
        getScreen.style.display = "none";
        stopScreen.style.display = "inline";
      }).catch(err => {
        console.error('Could not get stream: ', err);
      });
    } else {
      console.error('Could not get stream');
    }
  });
});

stopScreen.addEventListener('click', event => {
  stream.getTracks().forEach(track => track.stop());
  video.src = '';
  stopScreen.style.display = "none";
  getScreen.style.display = "inline";
});

let c1,ctx1,c_tmp,ctx_tmp;
function init() {
  c1 = document.getElementById('output-canvas');
  ctx1 = c1.getContext('2d');

  c_tmp = document.createElement('canvas');
  c_tmp.setAttribute('width', 300);
  c_tmp.setAttribute('height', 250);
  ctx_tmp = c_tmp.getContext('2d');

  c_tmp2 = document.createElement('canvas');
  c_tmp2.setAttribute('width', 300);
  c_tmp2.setAttribute('height', 250);
  ctx_tmp2 = c_tmp2.getContext('2d');

  video.addEventListener('play', computeFrame);
}


function computeFrame() {
  ctx_tmp.drawImage(video, 0, 0, 300 , 300*video.videoHeight/video.videoWidth);
  let frame = ctx_tmp.getImageData(0, 0, 300 , 300*video.videoHeight/video.videoWidth);
  let frame2 = ctx_tmp2.getImageData(0, 0, 300 , 300*video.videoHeight/video.videoWidth);
  for (let i = 0; i < frame.data.length /4; i++) {
    frame.data[i * 4 + 0]  = frame.data[i * 4 + 0] - frame2.data[i * 4 + 0];
    frame.data[i * 4 + 1]  = frame.data[i * 4 + 1] - frame2.data[i * 4 + 1];
    frame.data[i * 4 + 2]  = frame.data[i * 4 + 2] - frame2.data[i * 4 + 2];
  }
  ctx_tmp2.drawImage(video, 0, 0, 300 , 300*video.videoHeight/video.videoWidth);
  ctx1.putImageData(frame, 0, 0);
  setTimeout(computeFrame, 0);
}

document.addEventListener("DOMContentLoaded", () => {
  init();
});
