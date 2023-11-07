{-
Copyright 2023 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-}

import Development.Shake
import Development.Shake.Command
import Development.Shake.FilePath
import Development.Shake.Util

main :: IO ()
main = shakeArgs shakeOptions{shakeProgress = progressSimple} $ do
    action $ do
        mp3s <- getDirectoryFiles "" ["//*.mp3"]
        need [ "_opus" </> f -<.> "oga" | f <- mp3s ]
    {-
    action $ do
        jpgs <- getDirectoryFiles "" ["//*.jpg"]
        need [ "_opus" </> f | f <- jpgs ]
    -}
    "_opus//*.oga" %> \out -> do
        let src = dropDirectory1 $ out -<.> "mp3"
        need [src]
        cmd_ "/mnt/ext/shared/mp3/_cetba/audio_to_opus.py --bitrate=32768 --samplerate=16000" [src, out]
    "_opus//*.jpg" %> \out -> do
        let src = dropDirectory1 out
        need [src]
        Just target <- liftIO $ makeRelativeEx (takeDirectory out) src
        cmd_ "ln -s" [target, out]
