from typing import Tuple

import numpy as np
import os

from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.datasets import mnist
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.initializers import RandomUniform
from tensorflow.keras.initializers import Constant
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.models import load_model

from tensorflow.keras.callbacks import TensorBoard

from tf_utils.callbacks import ConfusionMatrix

MODELS_DIR = os.path.join(os.path.curdir, "/models")
if not os.path.exists(MODELS_DIR):
    os.mkdir(MODELS_DIR)
MODEL_FILE_PATH = os.path.join(MODELS_DIR, "/mnist_model.h5")
print(f"Model directory: {MODELS_DIR}")
LOGS_DIR = os.path.join(os.path.curdir, "logs")
if not os.path.exists(LOGS_DIR):
    os.mkdir(LOGS_DIR)
MODEL_LOG_DIR = os.path.join(LOGS_DIR, "mnist_cm")
print(f"Log directory: {LOGS_DIR}")


def get_dataset(num_features: int, num_classes: int) -> Tuple[
        Tuple[np.ndarray, np.ndarray],
        Tuple[np.ndarray, np.ndarray]]:
    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    x_train = x_train.reshape(-1, num_features).astype(np.float32)
    x_test = x_test.reshape(-1, num_features).astype(np.float32)
    y_train = to_categorical(y_train, num_classes=num_classes, dtype=np.float32)
    y_test = to_categorical(y_test, num_classes=num_classes, dtype=np.float32)

    return (x_train, y_train), (x_test, y_test)


def build_model(num_features: int, num_classes: int) -> Sequential:
    """ Returns a Sequential model. """
    init_weights = RandomUniform(minval=-0.05, maxval=0.05)
    init_bias = Constant(value=0.0)
    model = Sequential()
    model.add(
        Dense(
            units=256,
            kernel_initializer=init_weights,
            bias_initializer=init_bias,
            input_shape=(num_features,)
        )
    )
    model.add(Activation('relu'))
    model.add(
        Dense(
            units=128,
            kernel_initializer=init_weights,
            bias_initializer=init_bias,
            input_shape=(num_features,)
        )
    )
    model.add(Activation('relu'))
    model.add(
        Dense(
            units=64,
            kernel_initializer=init_weights,
            bias_initializer=init_bias,
            input_shape=(num_features,)
        )
    )
    model.add(Activation('relu'))
    model.add(Dense(units=num_classes))
    model.add(Activation('softmax'))
    model.summary()
    return model


def main(epochs, batch_size, learning_rate):
    """ Main function. """
    num_features = 784
    num_classes = 10

    (x_train, y_train), (x_test, y_test) = get_dataset(num_features, num_classes)

    print(f"x_train shape: {x_train.shape}")
    print(f"y_train shape: {y_train.shape}")
    print(f"x_test shape: {x_test.shape}")
    print(f"y_test shape: {y_test.shape}")

    model = build_model(
        num_features=num_features,
        num_classes=num_classes
    )

    optimizer = Adam(lr=learning_rate)
    # optimizer = SGD()
    # optimizer = RMSprop()

    model.compile(
        loss='categorical_crossentropy',
        optimizer=optimizer,
        metrics=["accuracy"]
    )

    tb_callback = TensorBoard(
        log_dir=MODEL_LOG_DIR,
        histogram_freq=1,
        write_graph=True
    )

    classes_list = [class_idx for class_idx in range(num_classes)]

    cm_callback = ConfusionMatrix(
        model,
        x_test,
        y_test,
        classes_list=classes_list,
        log_dir=MODEL_LOG_DIR,
    )

    model.fit(
        x=x_train,
        y=y_train,
        epochs=epochs,
        batch_size=batch_size,
        verbose=1,
        validation_data=(x_test, y_test),
        callbacks=[tb_callback, cm_callback]
    )

    scores = model.evaluate(x_test, y_test)
    print(f"Scores: {scores}")


if __name__ == '__main__':
    main(epochs=5, batch_size=256, learning_rate=0.001)
