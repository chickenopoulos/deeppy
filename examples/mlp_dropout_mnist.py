#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np
import deeppy as dp


def run():
    # Prepare data
    dataset = dp.datasets.MNIST()
    x, y = dataset.data(flat=True)
    x = x.astype(dp.float_)
    y = y.astype(dp.int_)
    train_idx, test_idx = dataset.split()
    x_train = x[train_idx]
    y_train = y[train_idx]
    x_test = x[test_idx]
    y_test = y[test_idx]

    scaler = dp.StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)

    batch_size = 128
    train_input = dp.SupervisedInput(x_train, y_train, batch_size=batch_size)
    test_input = dp.SupervisedInput(x_test, y_test)

    # Setup neural network
    net = dp.NeuralNetwork(
        layers=[
            dp.Dropout(0.2),
            dp.DropoutFullyConnected(
                n_out=800,
                dropout=0.5,
                weights=dp.Parameter(dp.NormalFiller(sigma=0.01),
                                     weight_decay=0.00001),
            ),
            dp.Activation('relu'),
            dp.DropoutFullyConnected(
                n_out=800,
                dropout=0.5,
                weights=dp.Parameter(dp.NormalFiller(sigma=0.01),
                                     weight_decay=0.00001),
            ),
            dp.Activation('relu'),
            dp.DropoutFullyConnected(
                n_out=dataset.n_classes,
                weights=dp.Parameter(dp.NormalFiller(sigma=0.01),
                                     weight_decay=0.00001),
            ),
        ],
        loss=dp.MultinomialLogReg(),
    )

    # Train neural network
    def val_error():
        return net.error(test_input)
    trainer = dp.StochasticGradientDescent(
        max_epochs=50,
        learn_rule=dp.Momentum(learn_rate=0.1, momentum=0.9),
    )
    trainer.train(net, train_input, val_error)

    # Visualize weights from first layer
    W = next(np.array(layer.W.array) for layer in net.layers
             if isinstance(layer, dp.FullyConnected))
    W = np.reshape(W.T, (-1, 28, 28))
    filepath = os.path.join('mnist', 'mlp_dropout_weights.png')
    dp.misc.img_save(dp.misc.img_tile(dp.misc.img_stretch(W)), filepath)

    # Evaluate on test data
    error = net.error(test_input)
    print('Test error rate: %.4f' % error)


if __name__ == '__main__':
    run()
