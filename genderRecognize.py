from inaSpeechSegmenter import Segmenter


def recognize(audioFile):
    gender = []
    seg = Segmenter()
    segmentation = seg(audioFile)
    for i in segmentation:
        if 'noEnergy' not in i[0]:
            gender.append(i[0])
    return (max(set(gender), key=gender.count))
