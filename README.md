# Python-script
Simple scripts to use for CREDO detection analysis,<br>
autor: Sławomir Stuglik

# How start with credo packets detections
1) contact CREDO Science Coordinator (credodetector@credo.science) and describe why do you want access and what are you going to do with the data. 
Remember to include your username and send the message from email address you used during registration. 
Documentation about data export is available on GitHub.

2) Having access to the data, you must download the scripts to download the detection described here:
https://github.com/credo-science/credo-api-tools/tree/master/data-exporter

And download data using the command from the terminal (console):
Python3 ./credo-data-exporter.py --user yourusername --password 'userr_password'

3) Detections that interest you are located in the "Detections" folder.
Each detection creates 1 record consisting of 3 parts regarding:
# a) User - detection user information
  "team_id": 1,
  "user_id": 1,
  
# b) location - geographical coordinates
  "latitude": 49.493,
  "longitude": 19.051,
  
# c) time - detection time information
  "timestamp": 1577834324993,
  "time_received": 1577866929774,
 
  
# d) picture - detection image information
  "id": unique detection id,
  "frame_content": image code in base64,
  "height": information about the "height" of the resolution,
  "width": information about the "width" of the resolution,
  "visible": true,
  
  position of the brightest pixel in the slice (most common size of the slice 60x60)
  "x": 400,
  "y": 374



