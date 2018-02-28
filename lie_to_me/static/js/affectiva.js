// socketIO

var faceMode = affdex.FaceDetectorMode.LARGE_FACES;

// Construct a FrameDetector and specify the image width / height and face detector mode.
var detector = new affdex.FrameDetector(faceMode)

// Affectiva timer timestamp
var startTimestamp;

var establishTimeStamp = ( () => {
  var executed = false;
  return () => {
    if (!executed) {
      startTimestamp = (new Date()).getTime() / 1000;
    }
  }
})();

var timeBetweenDrawings = 200  //20ms

var setupSockets = () => {

  socket.on('frames_ready', () => {
    console.log('Server ready to receive frames')
    socket.emit('ready_receive', {data: 'Ready Receive'});
  })

  socket.on('next_frame', (data) => {
    console.log('Received\n')
    let frame_number = data[0]
    let base64_image = btoa(String.fromCharCode(...new Uint8Array(data[1])));
    
    const video = document.getElementById("video");
    const canvas = document.getElementById("video_canvas");
    const context = canvas.getContext('2d');

    var my_image = new Image()
    my_image.src = base64_image
    context.drawImage(my_image, 0, 0)
    var imageData = context.getImageData(0, 0, 640, 480);

    console.log('Received Frame: ' + frame_number)
    console.log('Image: ' + base64_image)
    console.log('image_data: ' + imageData)
    console.log()

    var now = (new Date()).getTime() / 1000;
    var deltaTime = now - startTimestamp;
    detector.process(imageData, deltaTime);

    //socket.emit('next_frame', {data: 'Ready Receive'})
  })

  socket.on('no_more_frames', () => {
    console.log('Complete')
    stopEmotionDetection()
  })

}

function draw(v,c,w,h) 
{
  if(v.paused || v.ended) return false;
  c.drawImage(v,0,0,w,h);
  setTimeout(draw,timeBetweenDrawings,v,c,w,h);
}

// function analyzeFrames(context, video)
// {
//     if(video.paused || video.ended) return false;

//     var imageData = context.getImageData(0, 0, 640, 480);

//     //Get current time in seconds
//     var now = (new Date()).getTime() / 1000;

//     //Get delta time between the first frame and the current frame.
//     var deltaTime = now - startTimestamp;

//     //Process the frame
//     detector.process(imageData, deltaTime);
//     setTimeout(analyzeFrames, timeBetweenDrawings, context, video);
// }

function stopEmotionDetection()
{
  console.log("started stopping detector")
  if (detector && detector.isRunning) 
  {
    detector.removeEventListener();
    detector.stop();
    console.log("stopped detector")
  }
}


// function startEmotionDetection()
// {
//   if (detector && detector.isRunning) 
//   {


//     //const video = document.getElementById("video");
//     //const canvas = document.getElementById("video_canvas");
//     //const context = canvas.getContext('2d');

//     //analyzeFrames(context, video);
//   }
// }

detector.addEventListener("onInitializeSuccess", () => {
  console.log("Affectiva loaded successfully");

  $(".overlay").html("");
  $(".file-field .btn").removeClass("disabled");
  $(".file-path").prop('disabled', false);
  $(".file-path").change( () => {
    if( $(".file-path").val().length > 0)
    {
      var URL = window.URL || window.webkitURL
      var file = document.getElementById('fileItem').files[0]
      var fileURL = URL.createObjectURL(file)

      const video_player = document.getElementById("video")
      var source = document.createElement('source');
      source.setAttribute('src', fileURL);
      video_player.appendChild(source);
      video_player.load();
      $("#video").css('visibility', "visible");

    }
  });

  const video = document.getElementById("video");
  const canvas = document.getElementById("video_canvas");
  const context = canvas.getContext('2d');

  video.addEventListener('play', () => {
    console.log("video play was called")
    draw(video, context, canvas.width, canvas.height)

  }, false);

  // video.addEventListener('playing', () => {
  //   console.log("video playing is called")
  // }, false)

  // video.addEventListener('pause', () => {
  //   console.log("Video was Paused");
  // }, false)

  // video.addEventListener('ended', () => {
  //   console.log("Video Ended");
  //   detector.stop();
  // }, false)

});

detector.addEventListener("onInitializeFailure", () => {
  console.log("Affectiva failed to load");
});

/* 
  onImageResults success is called when a frame is processed successfully and receives 3 parameters:
  - Faces: Dictionary of faces in the frame keyed by the face id.
           For each face id, the values of detected emotions, expressions, appearane metrics 
           and coordinates of the feature points
  - image: An imageData object containing the pixel values for the processed frame.
  - timestamp: The timestamp of the captured image in seconds.
*/
detector.addEventListener("onImageResultsSuccess", (faces, image, timestamp) => {

  if (faces.length > 0) 
  {
    let appearance = faces[0].appearance
    let emotions = faces[0].emotions  //key value pair dictionary
    let expressions = faces[0].expressions

    // only focus on emotions
    console.log(emotions)
  }

});

/* 
  onImageResults success receives 3 parameters:
  - image: An imageData object containing the pixel values for the processed frame.
  - timestamp: An imageData object contain the pixel values for the processed frame.
  - err_detail: A string contains the encountered exception.
*/
detector.addEventListener("onImageResultsFailure", (image, timestamp, err_detail) => {
  console.log(timestamp);
  console.log(err_detail);
});

detector.addEventListener("onResetSuccess", () => {
  console.log("detector was reset successfully");
});

detector.addEventListener("onResetFailure", () => {
  console.log("failed to reset detector");
});

detector.addEventListener("onStopSuccess", () => {
  console.log("Successfully stopped detector")
});

detector.addEventListener("onStopFailure", () => {
  console.log("Failed to stop detector");
});

detector.detectAllExpressions();
detector.detectAllEmotions();
detector.detectAllEmojis();
detector.detectAllAppearance();

// ON PAGE LOAD
$( () => {
  detector.start();
  $(".file-path").val("");

});

