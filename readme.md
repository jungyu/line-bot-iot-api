1.確認你的 Heroku 有沒有 ffmpeg
$ heroku run "ffmpeg -version"

2.登入 Heroku 網站頁面->到「Settings」，找到 Buildpacks ，按下「Add Buildpack」，新增以下連結：
https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git

註：可以到： https://elements.heroku.com/buildpacks 找到最新及正確的連結

3.重新佈置你的 app 
$ git push heroku main

