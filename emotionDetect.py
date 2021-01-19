import librosa
import soundfile
import os, glob
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score

emotionsRavdessData = {
    '01': 'neutral',
    '02': 'calm',
    '03': 'happy',
    '04': 'sad',
    '05': 'angry',
    '06': 'fearful',
    '07': 'disgust',
    '08': 'surprised'
}

observed_emotions = ['neutral', 'calm', 'happy', 'disgust', 'sad', 'angry']


def extract_feature(file_name, mfcc, chroma, mel):
    with soundfile.SoundFile(file_name) as file:
        X = file.read(dtype="float32")
        sample_rate = file.samplerate
        if chroma:
            stft = np.abs(librosa.stft(X))
        result = np.array([])
        if mfcc:
            mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T, axis=0)
            result = np.hstack((result, mfccs))
        if chroma:
            chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T, axis=0)
            result = np.hstack((result, chroma))
        if mel:
            mel = np.mean(librosa.feature.melspectrogram(X, sr=sample_rate).T, axis=0)
            result = np.hstack((result, mel))
    return result


def load_dataset(test_size=0.15):
    x, y = [], []
    # Ravdess Dataset
    for file in glob.glob("DataSets/ravdessData/Actor_*/*.wav"):
        file_name = os.path.basename(file)
        emotion = emotionsRavdessData[file_name.split("-")[2]]
        if emotion not in observed_emotions:
            continue
        feature = extract_feature(file, mfcc=True, chroma=True, mel=True)
        x.append(feature)
        y.append(emotion)
    # TESS Toronto Dataset
    for file in glob.glob("DataSets/TESS_Toronto_emotional_speech_set_data/OAF_*/*.wav"):
        file_name = os.path.basename(file)
        emotion = file_name.split("_")[2].split(".")[0]
        if emotion not in observed_emotions:
            continue
        feature = extract_feature(file, mfcc=True, chroma=True, mel=True)
        x.append(feature)
        y.append(emotion)
    return train_test_split(np.array(x), y, test_size=test_size, random_state=9)


x_train, x_test, y_train, y_test = load_dataset(test_size=0.15)
model = MLPClassifier(alpha=0.01, batch_size=256, epsilon=1e-08, hidden_layer_sizes=(300,), learning_rate='adaptive',
                      max_iter=500)
model.fit(x_train, y_train)
y_pred = model.predict(x_test)
accuracy = accuracy_score(y_true=y_test, y_pred=y_pred)


## Train info
# print((x_train.shape[0], x_test.shape[0]))
# print(f'Features extracted: {x_train.shape[1]}')
# print("Accuracy: {:.2f}%".format(accuracy*100))


def emotionRecognize(file):
    try:
        new_emotion = extract_feature(file, mfcc=True, chroma=True, mel=True)
        new_emotion = new_emotion.tolist()
        new_emotion = [new_emotion]
        new_emotion = np.array(new_emotion)
        return model.predict(new_emotion)[0]
    except:
        return None
