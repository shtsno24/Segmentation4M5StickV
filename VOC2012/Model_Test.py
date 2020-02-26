import tensorflow as tf
from tensorflow.keras.models import Model

from tensorflow.keras.layers import Input, Conv2D, DepthwiseConv2D, MaxPooling2D, Conv2DTranspose
from tensorflow.keras.layers import UpSampling2D, Activation, Concatenate, BatchNormalization, Reshape
from tensorflow.keras.layers import LeakyReLU, Add
from tensorflow.keras.losses import sparse_categorical_crossentropy


def TestNet(input_shape=(120, 160, 3), classes=21):
    inputs = Input(shape=input_shape)

    x_3 = DepthwiseConv2D((3, 3), padding="same")(inputs)
    x_5 = DepthwiseConv2D((5, 5), padding="same")(inputs)
    x_7 = DepthwiseConv2D((7, 7), padding="same")(inputs)
    x = Concatenate(axis=3)([x_3, x_5, x_7])
    x = Conv2D(64, (1, 1), activation="relu")(x)
    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(64, (1, 1), activation="relu")(x)
    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(64, (1, 1))(x)
    x = BatchNormalization()(x)
    x0 = Activation("relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x0)

    # 60 x 80 x 64

    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(128, (1, 1), activation="relu")(x)
    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(128, (1, 1), activation="relu")(x)
    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(128, (1, 1))(x)
    x = BatchNormalization()(x)
    x1 = Activation("relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x1)

    # 30 x 40 x 128

    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(256, (1, 1), activation="relu")(x)
    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(256, (1, 1), activation="relu")(x)
    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(256, (1, 1))(x)
    x = BatchNormalization()(x)
    x2 = Activation("relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x2)

    # 15 x 20 x 256

    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(256, (1, 1), activation="relu")(x)
    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(256, (1, 1), activation="relu")(x)
    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(256, (1, 1))(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(256, (1, 1), activation="relu")(x)
    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(256, (1, 1), activation="relu")(x)

    # 15 x 20 x 256

    x = Conv2DTranspose(128, (3, 3), strides=(2, 2), padding="same")(x)
    x = Concatenate(axis=3)([x, x2])
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    # 30 x 40 x 128

    x = Conv2DTranspose(64, (3, 3), strides=(2, 2), padding="same")(x)
    x = Concatenate(axis=3)([x, x1])
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    # 60 x 80 x 64

    x = Conv2DTranspose(classes, (3, 3), strides=(2, 2), padding="same")(x)
    x = Concatenate(axis=3)([x, x0])
    x = BatchNormalization()(x)

    # 120 x 160 x classes

    x = Conv2D(classes, (1, 1))(x)
    outputs = Activation("softmax")(x)

    model = Model(inputs, outputs)
    return model


def TestNet3(input_shape=(120, 160, 3), classes=21):
    # @ https://github.com/alexgkendall/SegNet-Tutorial/blob/master/Example_Models/bayesian_segnet_camvid.prototxt
    img_input = Input(shape=input_shape)
    x = img_input
    # Encoder
    x = Conv2D(64, (3, 3), padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    x = Conv2D(128, (3, 3), padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    x = Conv2D(256, (3, 3), padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    x = Conv2D(512, (3, 3), padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    # Decoder
    x = Conv2D(512, (3, 3), padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    x = UpSampling2D(size=(2, 2))(x)
    x = Conv2D(256, (3, 3), padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    x = UpSampling2D(size=(2, 2))(x)
    x = Conv2D(128, (3, 3), padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    x = UpSampling2D(size=(2, 2))(x)
    x = Conv2D(64, (3, 3), padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    x = Conv2D(classes, (1, 1), padding="valid")(x)
    x = Activation("softmax")(x)
    model = Model(img_input, x)
    return model


def TestNet4(input_shape=(120, 160, 3), classes=21):
    inputs = Input(shape=input_shape)

    x = Conv2D(16, (3, 3), padding="same")(inputs)
    x = LeakyReLU()(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    x = Conv2D(32, (3, 3), padding="same")(x)
    x = LeakyReLU()(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    x = Conv2D(64, (3, 3), padding="same")(x)
    x = LeakyReLU()(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    x = Conv2D(128, (3, 3), padding="same")(x)
    x = LeakyReLU()(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    # x = Conv2D(128, (3, 3), padding="same")(x)
    # x = LeakyReLU()(x)
    # x = MaxPooling2D(pool_size=(2, 2))(x)

    x = Conv2D(256, (3, 3), padding="same")(x)
    x = LeakyReLU()(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    x = Conv2D(512, (3, 3), padding="same")(x)
    x = LeakyReLU()(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    x = Conv2D(1024, (3, 3), padding="same")(x)
    x = LeakyReLU()(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    x = Conv2D(1024, (3, 3), padding="same")(x)
    x = LeakyReLU()(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    x = Conv2D(125, (1, 1), padding="same")(x)
    x = LeakyReLU()(x)

    outputs = Activation("softmax")(x)
    model = Model(inputs, outputs)
    return model
