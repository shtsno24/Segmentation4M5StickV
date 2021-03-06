import tensorflow as tf
from tensorflow.keras.models import Model

from tensorflow.keras.layers import Input, Conv2D, DepthwiseConv2D, MaxPooling2D, Conv2DTranspose
from tensorflow.keras.layers import UpSampling2D, Activation, Concatenate, BatchNormalization, Reshape
from tensorflow.keras.layers import LeakyReLU, Add, PReLU, SpatialDropout2D, ZeroPadding2D
from tensorflow.keras.losses import sparse_categorical_crossentropy

"""
もしかしたら，ResizeNearesetNeighbor，ResizeBilinear, TransposeConvが使えるかも．
H x W x D : 128 x 160 x 3 -> 128 x 160 x (class)
o_w = (in_w + 2 * pad - k_w - (k_w - 1)*(d_w - 1)) / s_w + 1
"""


def weighted_SparseCategoricalCrossentropy(sample_weights, classes=21):
    def loss_function(y_true, y_pred):
        y_true = tf.cast(y_true, tf.uint8)
        y_true = tf.one_hot(y_true, depth=classes)
        y_true = tf.cast(y_true, tf.float32)
        y_true = y_true * sample_weights
        # cce = tf.keras.losses.SparseCategoricalCrossentropy()
        cce = tf.keras.losses.CategoricalCrossentropy()
        return cce(y_true, y_pred)
    return loss_function


def initial_block(x, input_depth, channel, stride=(2, 2), Momentum=0.1):
    x_conv = ZeroPadding2D(padding=((1, 1), (1, 1)))(x)
    x_conv = Conv2D(channel - input_depth, (3, 3), strides=stride)(x_conv)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_conv = Activation("relu")(x_conv)

    x_pool = MaxPooling2D(pool_size=(2, 2))(x)
    y = Concatenate(axis=3)([x_conv, x_pool])

    return y


def bottleneck_downsample(x, output_depth, internal_scale=4, Momentum=0.1):
    internal_depth = int(output_depth / internal_scale)

    x_conv = Conv2D(internal_depth, (2, 2), strides=(2, 2))(x)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_conv = Activation("relu")(x_conv)

    x_conv = ZeroPadding2D(padding=((1, 1), (1, 1)))(x_conv)
    x_conv = Conv2D(internal_depth, (3, 3))(x_conv)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_conv = Activation("relu")(x_conv)

    x_conv = Conv2D(output_depth, (1, 1), use_bias=False)(x_conv)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_conv = SpatialDropout2D(0.01)(x_conv)

    x_pool = MaxPooling2D(pool_size=(2, 2))(x)

    x = Concatenate(axis=3)([x_conv, x_pool])
    x = Conv2D(output_depth, (1, 1))(x)
    x = BatchNormalization(momentum=Momentum)(x)
    y = Activation("relu")(x)
    return y


def bottleneck(x, output_depth, internal_scale=4, Momentum=0.1):
    internal_depth = int(output_depth / internal_scale)

    x_conv = Conv2D(internal_depth, (1, 1))(x)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_conv = Activation("relu")(x_conv)

    x_conv = ZeroPadding2D(padding=((1, 1), (1, 1)))(x_conv)
    x_conv = Conv2D(internal_depth, (3, 3))(x_conv)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_conv = Activation("relu")(x_conv)

    x_conv = Conv2D(output_depth, (1, 1), use_bias=False)(x_conv)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_conv = SpatialDropout2D(0.01)(x_conv)

    x_pool = MaxPooling2D(pool_size=(2, 2))(x)
    x_pool = UpSampling2D(size=(2, 2))(x_pool)

    x = Concatenate()([x_conv, x_pool])
    x = Conv2D(output_depth, (1, 1))(x)
    x = BatchNormalization(momentum=Momentum)(x)
    y = Activation("relu")(x)
    return y


def bottleneck_asymmetric(x, asymmetric, output_depth, internal_scale=4, Momentum=0.1):
    internal_depth = int(output_depth / internal_scale)
    pad_half = int(asymmetric / 2)

    x_conv = Conv2D(internal_depth, (1, 1))(x)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_conv = Activation("relu")(x_conv)

    x_conv = ZeroPadding2D(padding=((0, 0), (pad_half, pad_half)))(x_conv)
    x_conv = Conv2D(internal_depth, (1, asymmetric), use_bias=False)(x_conv)
    x_conv = ZeroPadding2D(padding=((pad_half, pad_half), (0, 0)))(x_conv)
    x_conv = Conv2D(internal_depth, (asymmetric, 1))(x_conv)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_conv = Activation("relu")(x_conv)

    x_conv = Conv2D(output_depth, (1, 1), use_bias=False)(x_conv)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_conv = SpatialDropout2D(0.01)(x_conv)

    x_pool = MaxPooling2D(pool_size=(2, 2))(x)
    x_pool = UpSampling2D(size=(2, 2))(x_pool)

    x = Concatenate()([x_conv, x_pool])
    x = Conv2D(output_depth, (1, 1))(x)
    x = BatchNormalization(momentum=Momentum)(x)
    y = Activation("relu")(x)
    return y


def bottleneck_dilated(x, dilated, output_depth, internal_scale=4, Momentum=0.1):
    internal_depth = int(output_depth / internal_scale)

    x_conv = Conv2D(internal_depth, (1, 1))(x)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_conv = Activation("relu")(x_conv)

    x_conv = Conv2D(internal_depth, (3, 3), dilation_rate=(dilated, dilated), padding="same")(x_conv)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_conv = Activation("relu")(x_conv)
    # dilation_rate = 2 : padding = 2
    # dilation_rate = 4 : padding = 4
    # dilation_rate = 8 : padding = 8
    # dilation_rate = 16: padding = 16

    x_conv = Conv2D(output_depth, (1, 1), use_bias=False)(x_conv)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_conv = SpatialDropout2D(0.01)(x_conv)

    x_pool = MaxPooling2D(pool_size=(2, 2))(x)
    x_pool = UpSampling2D(size=(2, 2))(x_pool)

    x = Concatenate()([x_conv, x_pool])
    x = Conv2D(output_depth, (1, 1))(x)
    x = BatchNormalization(momentum=Momentum)(x)
    y = Activation("relu")(x)
    return y


def bottleneck_upsampling(x, output_depth, internal_scale=4, Momentum=0.1):
    internal_depth = int(output_depth / internal_scale)

    x_conv = Conv2D(internal_depth, (1, 1))(x)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_conv = Activation("relu")(x_conv)
    x_conv = Conv2DTranspose(internal_depth, (3, 3), strides=(2, 2), padding="same")(x_conv)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_conv = Activation("relu")(x_conv)
    x_conv = Conv2D(output_depth, (1, 1), use_bias=False)(x_conv)
    # x_conv = Conv2D(output_depth, (1, 1))(x_conv)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_conv = SpatialDropout2D(0.01)(x_conv)

    x_pool = Conv2D(output_depth, (1, 1), use_bias=False)(x)
    # x_pool = Conv2D(output_depth, (1, 1))(x)
    x_conv = BatchNormalization(momentum=Momentum)(x_conv)
    x_pool = UpSampling2D(size=(2, 2))(x_pool)

    x = Concatenate()([x_conv, x_pool])
    x = Conv2D(output_depth, (1, 1))(x)
    x = BatchNormalization(momentum=Momentum)(x)
    y = Activation("relu")(x)
    return y


def TestNet(input_shape=(128, 128, 3), classes=21):

    inputs = Input(shape=input_shape)
    x = initial_block(inputs, 4, 16)
    x_skip_0 = x
    # 64 x 80 x 16

    x = bottleneck_downsample(x, 64)

    # 32 x 40 x 64

    for _ in range(4):
        x = bottleneck(x, 64)
    x_skip_1 = x
    x = bottleneck_downsample(x, 128)

    # 16 x 20 x 128

    for _ in range(2):
        x = bottleneck(x, 128)
        x = bottleneck_dilated(x, 2, 128)
        x = bottleneck_asymmetric(x, 5, 128)
        x = bottleneck_dilated(x, 4, 128)
        x = bottleneck(x, 128)
        x = bottleneck_dilated(x, 8, 128)
        x = bottleneck_asymmetric(x, 5, 128)
        x = bottleneck_dilated(x, 16, 128)

    x = bottleneck_upsampling(x, 64)
    x = Concatenate(axis=3)([x, x_skip_1])
    x = bottleneck(x, 64)
    x = bottleneck(x, 64)

    # 32 x 40 x 64

    x = bottleneck_upsampling(x, 16)
    x = Concatenate(axis=3)([x, x_skip_0])
    x = bottleneck(x, 16)

    # 64 x 80 x 16

    x = Conv2DTranspose(classes, kernel_size=(2, 2), strides=(2, 2), padding="same")(x)

    # 128 x 160 x 16

    outputs = Activation("softmax")(x)
    model = Model(inputs, outputs)
    return model
