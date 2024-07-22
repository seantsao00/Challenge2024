#!/bin/bash

gource \
	-s 0.2 \
	-1920x1080 \
	--stop-at-end \
	--key \
	--highlight-users \
	--hide mouse \
	--background-colour 000000 \
	--output-ppm-stream - \
	--output-framerate 60 |
	ffmpeg -y -r 60 -f image2pipe -vcodec ppm -i - -vcodec libx264 -pix_fmt yuv420p -crf 1 -threads 0 -bf 0 gource_record.mp4
