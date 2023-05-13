import os
import datetime
import time

# fileName = "\"/Users/nadrino/Desktop/liveKROQ.m4a\""
# fileName = "\"/Users/nadrino/Downloads/The 1975  - At Their Very Best (full show) - Auckland, 2023 #the1975/The 1975  - At Their Very Best (full show) - Auckland, 2023 #the1975 (1080p_30fps_H264-128kbit_AAC).mp4\""
fileName = "\"/Users/nadrino/Desktop/temp/JDownloader2/The 1975  - At Their Very Best (full show) - Auckland, 2023 #the1975 (128kbit_AAC).m4a\""

# 23.98 fps
# 24 with premiere
# scaling = 1 * 24/23.98
scaling = 1

cutsList = [
  "00:02:56", # Oh Caroline (atpoaim)
  "00:05:28", # I Couldn't Be More In Love  (atpoaim)
  "00:07:42", # Sincerity Is Scary
  "00:12:26", # Looking for Somebody (to Love)
  "00:15:22", # Happiness
  "00:20:50", # UGH!
  "00:25:09", # Oh Caroline
  "00:29:37", # Me & You Together Song
  "00:38:30", # All I Need to Hear
  "00:42:28", # If You're Too Shy (Let Me Know)
  "00:52:08", # fallingforyou
  "00:56:00", # About You
  "01:01:20", # Robbers
  "01:06:05", # You can't always get what you want
  "01:06:42", # I Want It That Way (Backstreet Boys cover)
  "01:07:48", # She's American
  "01:13:21", # Somebody Else
  "01:18:45", # It's Not Living (If It's Not With You)
  "01:23:40", # Paris
  "01:29:05", # Love It If We Made It
  "01:34:06", # I Always Wanna Die (Sometimes)
  "01:38:56", # The Sound
  "01:43:57", # Sex
  "01:47:54", # Give Yourself a Try
]

# 00:00 Matty backstage, as Love Me Tender plays
# 02:56 Oh Caroline (atpoaim)
# 05:28 I Couldn't Be More In Love  (atpoaim)
# 07:42 Sincerity Is Scary
# 12:26 Looking for Somebody (to Love)
# 15:22 Happiness
# 20:50 UGH!
# 25:09 Oh Caroline
# 28:57 "Jamie, play me some music so I don't feel shy"
# 29:37 Me & You Together Song
# 33:30 "I do feel shy, ladies and gentleman"
# 38:10 Matty changes into "a more Truman Black-esque outfit"
# 38:30 All I Need to Hear
# 42:28 If You're Too Shy (Let Me Know)
# 47:50 I'm in Love With You
# 52:08 fallingforyou
# 56:00 About You
# 1:01:20 Robbers
# 1:06:05 "You can't always get what you want", "people don't click enough"
# 1:06:42 Matty & crowd sing I Want It That Way (Backstreet Boys cover)
# 1:07:48 She's American
# 1:12:37 "Is anybody's ex here as well?"
# 1:13:21 Somebody Else
# 1:18:20 "We've got so many bloody great songs, guys"
# 1:18:45 It's Not Living (If It's Not With You)
# 1:23:30 "We're very happy to be here"
# 1:23:40 Paris
# 1:29:05 Love It If We Made It
# 1:33:09 "Singing that song is the only thing that gives me this perfect body"
# 1:33:29 "Different chord for different generations"
# 1:33:39 The Best of Me (The Starting Line cover)
# 1:34:06 I Always Wanna Die (Sometimes)
# 1:38:56 The Sound
# 1:41:40 "Alright, Auckland, let's make Australia look stupid"
# 1:41:52 "one, two, fucking jump!"
# 1:43:05 "It's really far to be this normal, New Zealand."
# 1:43:57 Sex
# 1:47:25 "Ladies and gentleman, please give it up for the world's greatest band"
# 1:47:54 Give Yourself a Try
# 1:51:08 The end

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


