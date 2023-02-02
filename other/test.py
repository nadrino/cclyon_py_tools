import os
import datetime
import time

fileName = "\"/Users/nadrino/Downloads/The 1975 At Their Very Best.mkv\""

# 23.98 fps
# 24 with premiere
scaling = 1 * 24/23.98

cutsList = [ # premiere time codes
  "00:00:00",
  "00:03:14",
  "00:05:37", # Somebody
  "00:08:42", # Happiness
  "00:14:18",
  "00:18:38",
  "00:22:53",
  "00:27:32",
  "00:31:56",
  "00:35:05",
  "00:39:06",
  "00:44:06",
  "00:49:35",
  "00:55:43",
  "01:03:33",
  "01:09:27",
  "01:12:57",
  "01:16:44",
  "01:21:50",
  "01:26:50",
  "01:32:36",
  "01:37:54", # I Always Wanna Die (Sometimes)
  "01:43:06", # Love it if we
  "01:47:02", # Sound
  "01:51:01",
  "01:54:59"
]

timeCodes = list()
for timeCode in cutsList:
  x = time.strptime(timeCode,'%H:%M:%S')
  timeCodes.append( scaling * float( datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds() ) )

print(timeCodes)

for iCut in range(len(cutsList)):
  cmdList = list()
  cmdList.append("ffmpeg")
  cmdList.append("-i")
  cmdList.append(fileName)

  cmdList.append("-ss")
  # cmdList.append(cutsList[iCut])
  cmdList.append(str( timeCodes[iCut] ))
  if iCut+1 < len(cutsList):
    cmdList.append("-to")
    # cmdList.append(cutsList[iCut+1])
    cmdList.append(str(timeCodes[iCut+1]))


  cmdList.append("-async 1")
  cmdList.append("-y")

  outName = "Track_" + str(iCut+1)

  # cmdVideo = " ".join(cmdList) + " -strict -2 -codec copy " + outName + ".mp4"
  # cmdAudio = " ".join(cmdList) + " -strict -2 -vn -acodec  " + outName + ".aac"
  cmdAudio = " ".join(cmdList) + " -vn -acodec flac -sample_fmt s16 -ab 512k -ar 48000 " + outName + ".flac"
  # cmdAudio = " ".join(cmdList) + " -vn -acodec aac -ab 384k -ar 48000 " + outName + ".aac"

  # print(cmdVideo)
  # print(cmdAudio)
  os.system(cmdAudio)


