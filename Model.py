import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, DepthwiseConv2D, MaxPooling2D, UpSampling2D, Activation, Concatenate, BatchNormalization, Reshape
from tensorflow.keras.layers import LeakyReLU
from tensorflow.keras.losses import sparse_categorical_crossentropy

"""
もしかしたら，ResizeNearesetNeighbor，ResizeBilinear, TransposeConvが使えるかも．
H x W x D : 240 x 320 x 3 -> 240 x 320 x (class)
"""


"""
def TestNet(input_shape=(240, 320, 3), classes=151):
    inputs = Input(shape=input_shape)

    x = DepthwiseConv2D((3, 3), padding="same")(inputs)
    x = Conv2D(32, (1, 1), activation="relu")(x)
    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(32, (1, 1), activation="relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    x1 = MaxPooling2D(pool_size=(4, 4))(x)

    # 56 x 56 x 32

    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(64, (1, 1), activation="relu")(x)
    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(64, (1, 1), activation="relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    x2 = MaxPooling2D(pool_size=(2, 2))(x)

    # 28 x 28 x 64

    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(128, (1, 1), activation="relu")(x)
    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(128, (1, 1), activation="relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    # 14 x 14 x 128

    x = Concatenate()([x, x1, x2])
    x = Conv2D(128, (1, 1), activation="relu")(x)

    # 14 x 14 x 224

    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(64, (1, 1), activation="relu")(x)
    x = UpSampling2D(size=(2, 2))(x)

    # 28 x 28 x 64

    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(32, (1, 1), activation="relu")(x)
    x = UpSampling2D(size=(2, 2))(x)

    # 56 x 56 x 32

    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(classes, (1, 1), activation="relu")(x)
    x = UpSampling2D(size=(2, 2))(x)

    # 112 x 112 x 151
    x = DepthwiseConv2D((3, 3), padding="same")(x)
    outputs = Activation("softmax")(x)

    model = Model(inputs, outputs)
    return model
"""


def TestNet2(input_shape=(240, 320, 3), classes=151):
    inputs = Input(shape=input_shape)

    x0 = DepthwiseConv2D((3, 3), padding="same")(inputs)
    x1 = DepthwiseConv2D((5, 5), padding="same")(inputs)
    x2 = DepthwiseConv2D((7, 7), padding="same")(inputs)
    x3 = DepthwiseConv2D((9, 9), padding="same")(inputs)
    x = Concatenate()([x0, x1, x2, x3])
    x = Conv2D(64, (1, 1), activation="relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    # 56 x 56 x 64

    x0 = DepthwiseConv2D((3, 3), padding="same")(x)
    x1 = DepthwiseConv2D((7, 7), padding="same")(x)
    x = Concatenate()([x0, x1])
    x = Conv2D(128, (1, 1), activation="relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    # 28 x 28 x 128

    x0 = DepthwiseConv2D((3, 3), padding="same")(x)
    x1 = DepthwiseConv2D((7, 7), padding="same")(x)
    x = Concatenate()([x0, x1])
    x = Conv2D(256, (1, 1), activation="relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    # 14 x 14 x 256

    x0 = DepthwiseConv2D((3, 3), padding="same")(x)
    x1 = DepthwiseConv2D((7, 7), padding="same")(x)
    x = Concatenate()([x0, x1])
    x = Conv2D(256, (1, 1), activation="relu")(x)

    # 14 x 14 x 256

    x0 = DepthwiseConv2D((3, 3), padding="same")(x)
    x1 = DepthwiseConv2D((7, 7), padding="same")(x)
    x = Concatenate()([x0, x1])
    x = Conv2D(128, (1, 1), activation="relu")(x)
    x = UpSampling2D(size=(2, 2))(x)                # move UpSampling to top of this block

    # 28 x 28 x 128

    x0 = DepthwiseConv2D((3, 3), padding="same")(x)
    x1 = DepthwiseConv2D((7, 7), padding="same")(x)
    x = Concatenate()([x0, x1])
    x = Conv2D(64, (1, 1), activation="relu")(x)
    x = UpSampling2D(size=(2, 2))(x)                # move UpSampling to top of this block

    # 56 x 56 x 64

    x0 = DepthwiseConv2D((3, 3), padding="same")(x)
    x1 = DepthwiseConv2D((7, 7), padding="same")(x)
    x = Concatenate()([x0, x1])
    x = Conv2D(64, (1, 1), activation="relu")(x)
    x = UpSampling2D(size=(2, 2))(x)                # move UpSampling to top of this block

    # 112 x 112 x 151
    x = DepthwiseConv2D((3, 3), padding="same")(x)
    x = Conv2D(classes, (1, 1), activation="relu")(x)  # remove "relu"
    outputs = Activation("softmax")(x)

    model = Model(inputs, outputs)
    return model


def TestNet(input_shape=(240, 320, 3), classes=151):
    inputs = Input(shape=input_shape)

    x_3 = DepthwiseConv2D((3, 3), padding="same")(inputs)
    x_5 = DepthwiseConv2D((5, 5), padding="same")(inputs)
    x_7 = DepthwiseConv2D((7, 7), padding="same")(inputs)
    x = Concatenate()([x_3, x_5, x_7])
    x = Conv2D(64, (1, 1), activation="relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(inputs)

    # 120 x 160 x 64

    x_3 = DepthwiseConv2D((3, 3), padding="same")(x)
    x_5 = DepthwiseConv2D((5, 5), padding="same")(x)
    x_7 = DepthwiseConv2D((7, 7), padding="same")(x)
    x = Concatenate()([x_3, x_5, x_7])
    x = Conv2D(128, (1, 1), activation="relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    # 60 x 80 x 128

    x_3 = DepthwiseConv2D((3, 3), padding="same")(x)
    x_5 = DepthwiseConv2D((5, 5), padding="same")(x)
    x = Concatenate()([x_3, x_5])
    x = Conv2D(256, (1, 1), activation="relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    # 30 x 40 x 256

    x_3 = DepthwiseConv2D((3, 3), padding="same")(x)
    x_5 = DepthwiseConv2D((5, 5), padding="same")(x)
    x = Concatenate()([x_3, x_5])
    x = Conv2D(256, (1, 1), activation="relu")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    # 15 x 20 x 256

    x_3 = DepthwiseConv2D((3, 3), padding="same")(x)
    x_5 = DepthwiseConv2D((5, 5), padding="same")(x)
    x = Concatenate()([x_3, x_5])
    x = Conv2D(256, (1, 1), activation="relu")(x)

    # 15 x 20 x 256

    x_3 = DepthwiseConv2D((3, 3), padding="same")(x)
    x_5 = DepthwiseConv2D((5, 5), padding="same")(x)
    x = Concatenate()([x_3, x_5])
    x = Conv2D(256, (1, 1), activation="relu")(x)

    # 15 x 20 x 256

    x_3 = DepthwiseConv2D((3, 3), padding="same")(x)
    x_5 = DepthwiseConv2D((5, 5), padding="same")(x)
    x = Concatenate()([x_3, x_5])
    x = Conv2D(256, (1, 1), activation="relu")(x)

    # 15 x 20 x 256

    x = UpSampling2D(size=(2, 2))(x)
    x_3 = DepthwiseConv2D((3, 3), padding="same")(x)
    x_5 = DepthwiseConv2D((5, 5), padding="same")(x)
    x = Concatenate()([x_3, x_5])
    x = Conv2D(256, (1, 1), activation="relu")(x)

    # 30 x 40 x 256

    x = UpSampling2D(size=(2, 2))(x)
    x_3 = DepthwiseConv2D((3, 3), padding="same")(x)
    x_5 = DepthwiseConv2D((5, 5), padding="same")(x)
    x = Concatenate()([x_3, x_5])
    x = Conv2D(128, (1, 1), activation="relu")(x)

    # 60 x 80 x 128

    x = UpSampling2D(size=(2, 2))(x)
    x_3 = DepthwiseConv2D((3, 3), padding="same")(x)
    x_5 = DepthwiseConv2D((5, 5), padding="same")(x)
    x = Concatenate()([x_3, x_5])
    x = Conv2D(64, (1, 1), activation="relu")(x)

    # 120 x 160 x 64

    x = UpSampling2D(size=(2, 2))(x)
    x_3 = DepthwiseConv2D((3, 3), padding="same")(x)
    x_5 = DepthwiseConv2D((5, 5), padding="same")(x)
    x = Concatenate()([x_3, x_5])
    x = Conv2D(classes, (1, 1))(x)

    # 240 x 320 x classes

    outputs = Activation("softmax")(x)

    model = Model(inputs, outputs)
    return model


def TestNet3(input_shape=(240, 320, 3), classes=151):
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
    x = Reshape((input_shape[0] * input_shape[1], classes))(x)
    x = Activation("softmax")(x)
    model = Model(img_input, x)
    return model


def TestNet4(input_shape=(240, 320, 3), classes=151):
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
