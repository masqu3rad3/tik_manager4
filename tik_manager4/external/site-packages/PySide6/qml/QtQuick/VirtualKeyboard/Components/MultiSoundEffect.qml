// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtMultimedia

Item {
    id: multiSoundEffect
    property url source
    property int maxInstances: 2
    property var __cachedInstances
    property int __currentIndex: 0
    property real soundVolume: 1.0

    signal playingChanged(url source, bool playing)

    Component {
        id: soundEffectComp
        SoundEffect {
            source: multiSoundEffect.source
            onPlayingChanged: multiSoundEffect.playingChanged(source, playing)
        }
    }

    onSourceChanged: {
        __cachedInstances = []
        __currentIndex = 0
        if (source != Qt.resolvedUrl("")) {
            var i
            for (i = 0; i < maxInstances; i++) {
                var soundEffect = soundEffectComp.createObject(multiSoundEffect)
                if (soundEffect === null)
                    return
                __cachedInstances.push(soundEffect)
            }
        }
    }

    function play() {
        if (__cachedInstances === undefined || __cachedInstances.length === 0)
            return
        if (__cachedInstances[__currentIndex].playing) {
            __cachedInstances[__currentIndex].stop()
            __currentIndex = (__currentIndex + 1) % __cachedInstances.length
        }
        __cachedInstances[__currentIndex].volume = soundVolume
        __cachedInstances[__currentIndex].play()
    }
}
