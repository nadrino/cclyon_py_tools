import os
import datetime
import time

# fileName = "\"/Users/nadrino/Desktop/liveKROQ.m4a\""
# fileName = "\"/Users/nadrino/Desktop/temp/JDownloader2/The 1975 @ Gorilla Manchester - Full Live Show 01.02.23 (192kbit_AAC).m4a\""
fileName = "\"/Users/nadrino/Desktop/temp/JDownloader2/The 1975 - Lollapalooza Sweden 2023 (1080p_60fps_H264-128kbit_AAC).mp4\""
# fileName = "\"/Users/nadrino/Desktop/BBC_Radio_1s_Big_Weekend_Live_in_Dundee_2023_-_01._The_1975_m001m2b7_original.m4a\""

# 23.98 fps
# 24 with premiere
# scaling = 1 * 24/23.98
scaling = 1

cutsList = [
  "00:00:00", # Intro
  "00:01:05", # I Couldn't Be More in Love
  "00:05:08", # I'm in Love With You
  "00:09:38", # Oh Caroline
  "00:14:26", # Happiness
  "00:19:37", # Me & You Together Song
  "00:23:57", # Looking for Somebody(to Love)
  "00:27:41", # It's Not Living (If It's Not With You)
  "00:31:52", # If You're Too Shy (Let Me Know)
  "00:37:31", # An Encounter
  "00:38:26", # Robbers
  "00:42:30", # About You
  "00:48:10", # Somebody Else
  "00:54:32", # I Always Wanna Die(Sometimes)
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


