#!/bin/bash

curl -X POST -H "Content-Type: application/json" -d '{
  "text": "your mom",
  "input": "https://github.com/skeetzo/onlysnarf/blob/master/public/images/shnarf.jpg?raw=true"
}' http://13.48.136.241:5000