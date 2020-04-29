import numpy as np

class FeedForwardNN:

    def __init__(self, input_size, output_size, individual, config):
        self.hidden_size1 = config["number_neurons_layer1"]
        self.hidden_size2 = config["number_neurons_layer2"]

        self.input_size = input_size
        self.output_size = output_size

        self.use_biases = config["use_biases"]

        W1_size = self.input_size*self.hidden_size1
        W2_size = self.hidden_size1*self.hidden_size2
        W3_size = self.hidden_size2*self.output_size

        self.W1 = np.array([[float(element)] for element in individual[0:W1_size]], dtype=np.single)
        self.W2 = np.array([[float(element)] for element in individual[W1_size:W1_size + W2_size]], dtype=np.single)
        self.W3 = np.array([[float(element)] for element in individual[W1_size + W2_size:W1_size + W2_size + W3_size]],
                           dtype=np.single)

        # self.W1 = np.array([element for element in individual[0:W1_size]], dtype=np.float32)
        # self.W2 = np.array([element for element in individual[W1_size:W1_size + W2_size]], dtype=np.float32)
        # self.W3 = np.array([element for element in individual[W1_size + W2_size:W1_size + W2_size + W3_size]],
        #                    dtype=np.float32)

        self.W1 = self.W1.reshape([self.hidden_size1, input_size])
        self.W2 = self.W2.reshape([self.hidden_size2, self.hidden_size1])
        self.W3 = self.W3.reshape([output_size, self.hidden_size2])

        # self.W1 = self.W1.reshape([input_size, self.hidden_size1])
        # self.W2 = self.W2.reshape([self.hidden_size1, self.hidden_size2])
        # self.W3 = self.W3.reshape([self.hidden_size2, output_size])

        # Biases
        if self.use_biases:
            index_b = W1_size + W2_size + W3_size
            self.B1 = np.array([float(element) for element in individual[index_b:index_b + self.hidden_size1]],
                               dtype=np.single)
            self.B2 = np.array([float(element) for element in
                                individual[
                                index_b + self.hidden_size1:index_b + self.hidden_size1 + self.hidden_size2]],
                               dtype=np.single)
            self.B3 = np.array(
                [float(element) for element in individual[index_b + self.hidden_size1 + self.hidden_size2:]],
                dtype=np.single)

    def layer_step(self, layer_weights, a, bias=None):
        x = np.dot(layer_weights, a)

        if bias is not None:
            x += bias

        return x

    def relu(self, x):
        return np.maximum(0, x)

    def step(self, ob):

        bias = None

        if bias:
            bias = self.B1
        x = self.layer_step(self.W1, ob, bias)
        x = self.relu(x)

        if bias:
            bias = self.B2
        x = self.layer_step(self.W2, x, bias)
        x = self.relu(x)

        if bias:
            bias = self.B3
        x = self.layer_step(self.W3, x, bias)
        x = self.relu(x)

        return x

    @staticmethod
    def get_individual_size(input_size, output_size, config):

        hidden_size1 = config["number_neurons_layer1"]
        hidden_size2 = config["number_neurons_layer2"]

        individual_size = input_size * hidden_size1 + hidden_size1 * hidden_size2 + hidden_size2 * output_size

        if config["use_biases"]:
            individual_size += hidden_size1 + hidden_size2 + output_size

        return individual_size
