var faceMode = affdex.FaceDetectorMode.LARGE_FACES;

// Construct a FrameDetector and specify the image width / height and face detector mode.
var detector = new affdex.FrameDetector(faceMode)

// Affectiva timer timestamp
var startTimestamp; 
var myChart;
var timeBetweenDrawings = 2000  //20ms

function draw(v,c,w,h) 
{
  if(v.paused || v.ended) return false;
  c.drawImage(v,0,0,w,h);
  setTimeout(draw,timeBetweenDrawings,v,c,w,h);
}

function analyzeFrames(context, video)
{
    if(video.paused || video.ended) return false;

    var imageData = context.getImageData(0, 0, 640, 480);

    //Get current time in seconds
    var now = (new Date()).getTime() / 1000;

    //Get delta time between the first frame and the current frame.
    var deltaTime = now - startTimestamp;

    //Process the frame
    detector.process(imageData, deltaTime);
    setTimeout(analyzeFrames, timeBetweenDrawings, context, video);
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

function startEmotionDetection()
{
  if (detector && detector.isRunning) 
  {
    startTimestamp = (new Date()).getTime() / 1000;
    const video = document.getElementById("video");
    const canvas = document.getElementById("video_canvas");
    const context = canvas.getContext('2d');

    analyzeFrames(context, video);
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
  
  const video = document.getElementById("video");
  const canvas = document.getElementById("video_canvas");
  const context = canvas.getContext('2d');

  video.addEventListener('play', () => {
    console.log("video play was called")
    draw(video, context, canvas.width, canvas.height)

    $("#start_button").removeClass("disabled");
    $("#stop_button").removeClass("disabled");

  }, false);

  video.addEventListener('playing', () => {
    console.log("video playing is called")
  }, false)

  video.addEventListener('pause', () => {
    console.log("Video was Paused");
  }, false)

  video.addEventListener('ended', () => {
    console.log("Video Ended");
    detector.stop();
  }, false)

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
    var emotions_labels = []
    var emotion_vals = []
    Object.entries(emotions).forEach(
      ([key, value]) => {
        if (value < 0 ) value = 0; 
        emotions_labels.push(key);
        emotion_vals.push(value);
    });

    myChart.data.labels = emotions_labels
    myChart.data.datasets[0].data = emotion_vals
    myChart.update();
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

// CONFIGURE CHART JS
var ctx = document.getElementById("myChart").getContext('2d');
myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'Emotion Values',
            data: [],
            backgroundColor: [
                'rgba(255,99,132,1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)',
                'rgba(110, 102, 255, 1)',
                'rgba(255,10,132,1)',
                'rgba(154, 162, 235, 1)'
            ],
            borderColor: [
              'rgba(255,99,132,0.2)',
              'rgba(54, 162, 235, 0.2)',
              'rgba(255, 206, 86, 0.2)',
              'rgba(75, 192, 192, 0.2)',
              'rgba(153, 102, 255, 0.2)',
              'rgba(255, 159, 64, 0.2)',
              'rgba(110, 102, 255, 0.2)',
              'rgba(255,10,132,0.2)',
              'rgba(154, 162, 235, 0.2)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero:true
                }
            }]
        }
    }
});


// ON PAGE LOAD
$( () => {
  detector.start();
  $(".file-path").val("");
});

