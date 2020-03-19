# Python-script
Simple scripts to use for CREDO detection analysis,<br>
autor: Sławomir Stuglik

# Start with credo packets detections
<hr>
<b>1) contact CREDO Science Coordinator</b> (credodetector@credo.science) and describe why do you want access and what are you going to do with the data. 
Remember to include your username and send the message from email address you used during registration. 
Documentation about data export is available on GitHub.


<b>2) Having access to the data, you must download the scripts to download the detection</b> described here:
https://github.com/credo-science/credo-api-tools/tree/master/data-exporter


And download data using the command from the terminal (console):
Python3 ./credo-data-exporter.py --user yourusername --password 'userr_password'


<b>3) Detections that interest you are located in the "Detections" folder.
Each detection creates 1 record consisting of 3 parts regarding:</b>


<b>a) User - detection user information</b>
  "team_id": 1,<br>
  "user_id": 1,<br>
  
<b>b) location - geographical coordinates</b>
  "latitude": 49.493,<br>
  "longitude": 19.051,<br>
  
<b>c) time - detection time information</b>
  "timestamp": detection time (in unix time, 13 char,ms)<br>
  "time_received": reception time in the detection base,<br>
 
 
<b>d) picture - detection image information</b>
  "id": unique detection id,<br>
  "frame_content": image code in base64,<br>
  "height": information about the "height" of the resolution,<br>
  "width": information about the "width" of the resolution,<br>
  "visible": Does the detection pass through the primary filter (in the application), is set to (true, false),<br>
  <br>
  position of the brightest pixel in the slice (most common size of the slice 60x60)
  "x": 400,<br>
  "y": 374<br>

<hr>
</b>Detections are grouped into json files that can be read in many programming languages,</b>
We recommend using Python3 because it is very easy to use.

The following is a simple example of loading detection and writing detection time and device id.

    with open(path_to_file) as f:
        json_from_file = json.load(f)
 
     for detection in json_from_file['detections']:
        user_id = detection['user_id']
        timestamp=detection['timestamp']
        device_id=detection['device_id']
        
        print(%d;%d;%d,%(user_id,timestamp,device_id))
<hr>        
Detections require passing through anti filter artifacts, in offline mode,
you can read the report on this filter here: (registration required)
https://credo2.cyfronet.pl/redmine/documents/28
