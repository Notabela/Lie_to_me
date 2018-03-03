// socketIO

var faceMode = affdex.FaceDetectorMode.LARGE_FACES;

// Construct a FrameDetector and specify the image width / height and face detector mode.
var detector = new affdex.FrameDetector(faceMode)

// Affectiva timer timestamp
var startTimestamp;

//Canvas properties
var canvas_width = 640;
var canvas_height = 480;

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

  socket.on('canvas_width_height', (data) => {
    console.log('Server ready to receive frames')
    console.log('width, height: ', data)

    canvas_width = parseInt(data['width'])
    canvas_height = parseInt(data['height'])

    // Adjust canvas size to match video
    document.getElementById("video_canvas").width = canvas_width
    document.getElementById("video_canvas").height = canvas_height

    socket.emit('ready_receive', {data: 'Ready Receive'});
  })

  socket.on('next_frame', (data) => {
    let frame_number = data[0]

    console.log('Received Frame: ' + frame_number)

    let base64_image = btoa(String.fromCharCode(...new Uint8Array(data[1])));
    base64_image = 'data:image/jpg;base64,' + base64_image

    const canvas = document.getElementById("video_canvas");
    const context = canvas.getContext('2d');

    let image = new Image()
    image.onload = function() {
      console.log('Image loaded sucessfully')
      context.drawImage(image, 0, 0)
      let imgData = context.getImageData(0, 0, canvas_width, canvas_height);

      establishTimeStamp()
      var now = (new Date()).getTime() / 1000;
      var deltaTime = now - startTimestamp;
      detector.process(imgData, deltaTime);
      //socket.emit('next_frame', {data: 'Ready Receive'})
    };
    
    img.src = base64_image

  })

  socket.on('no_more_frames', () => {
    console.log('Complete')
    stopEmotionDetection()
  })

}

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
  console.log("Success processing image")

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

