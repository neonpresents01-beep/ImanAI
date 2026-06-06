# ImanAILite/layers.py
import numpy as np
from abc import ABC, abstractmethod
from .activations import Activations

DTYPE = np.float32


class Layer(ABC):
    @abstractmethod
    def forward(self, x, training=True):
        pass

    @abstractmethod
    def backward(self, grad):
        pass

    def update(self, lr=0.001):
        pass


# ---------- لایه Dense ----------
class Dense(Layer):
    def __init__(self, in_dim, out_dim, activation='relu', lr=0.001):
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.activation_name = activation
        self.activation = getattr(Activations, activation)
        self.lr = lr

        scale = np.sqrt(1.0 / in_dim)
        self.W = (np.random.randn(in_dim, out_dim) * scale).astype(DTYPE)
        self.b = np.zeros((1, out_dim), dtype=DTYPE)

        self.dW = None
        self.db = None
        self.last_x = None
        self.last_z = None

    def forward(self, x, training=True):
        self.last_x = x.copy()
        self.last_z = np.dot(x, self.W) + self.b
        return self.activation(self.last_z)

    def backward(self, grad):
        if self.activation_name == 'relu':
            grad = grad * (self.last_z > 0)
        elif self.activation_name == 'leaky_relu':
            grad = grad * np.where(self.last_z > 0, 1, 0.01)
        elif self.activation_name == 'sigmoid':
            sig = Activations.sigmoid(self.last_z)
            grad = grad * sig * (1 - sig)
        elif self.activation_name == 'tanh':
            grad = grad * (1 - Activations.tanh(self.last_z) ** 2)

        batch_size = grad.shape[0]
        self.dW = np.dot(self.last_x.T, grad) / batch_size
        self.db = np.sum(grad, axis=0, keepdims=True) / batch_size
        return np.dot(grad, self.W.T)

    def update(self, lr=None):
        if lr is None:
            lr = self.lr
        if self.dW is not None:
            self.W -= lr * np.clip(self.dW, -0.5, 0.5)
            self.b -= lr * np.clip(self.db, -0.5, 0.5)


# ---------- Dropout ----------
class Dropout(Layer):
    def __init__(self, rate=0.3):
        self.rate = rate
        self.mask = None

    def forward(self, x, training=True):
        if not training or self.rate == 0:
            return x
        self.mask = (np.random.rand(*x.shape) > self.rate).astype(DTYPE)
        scale = 1.0 / (1.0 - self.rate)
        return x * self.mask * scale

    def backward(self, grad):
        if self.mask is None:
            return grad
        return grad * self.mask


# ---------- BatchNorm ----------
class BatchNorm(Layer):
    def __init__(self, dim, momentum=0.9):
        self.dim = dim
        self.momentum = momentum
        self.gamma = np.ones(dim, dtype=DTYPE)
        self.beta = np.zeros(dim, dtype=DTYPE)
        self.running_mean = np.zeros(dim, dtype=DTYPE)
        self.running_var = np.ones(dim, dtype=DTYPE)
        self.epsilon = 1e-5
        self.training = True
        self.last_x = None
        self.last_norm = None
        self.dgamma = None
        self.dbeta = None

    def forward(self, x, training=True):
        self.training = training
        self.last_x = x.copy()
        if training:
            mean = np.mean(x, axis=0)
            var = np.var(x, axis=0)
            self.running_mean = self.momentum * self.running_mean + (1 - self.momentum) * mean
            self.running_var = self.momentum * self.running_var + (1 - self.momentum) * var
            self.last_norm = (x - mean) / np.sqrt(var + self.epsilon)
        else:
            self.last_norm = (x - self.running_mean) / np.sqrt(self.running_var + self.epsilon)
        return self.gamma * self.last_norm + self.beta

    def backward(self, grad):
        batch_size = grad.shape[0]
        self.dbeta = np.sum(grad, axis=0)
        self.dgamma = np.sum(grad * self.last_norm, axis=0)

        dx_norm = grad * self.gamma
        var = np.var(self.last_x, axis=0)
        dx = (1.0 / batch_size) * (1.0 / np.sqrt(var + self.epsilon)) * \
             (batch_size * dx_norm - np.sum(dx_norm, axis=0) -
              self.last_norm * np.sum(dx_norm * self.last_norm, axis=0))
        return dx

    def update(self, lr=0.001):
        if self.dgamma is not None:
            self.gamma -= lr * self.dgamma
            self.beta -= lr * self.dbeta


# ---------- Flatten ----------
class Flatten(Layer):
    def forward(self, x, training=True):
        self.original_shape = x.shape
        return x.reshape(x.shape[0], -1)

    def backward(self, grad):
        return grad.reshape(self.original_shape)


# ---------- Conv2D ----------
class Conv2D(Layer):
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, padding=0, activation='relu', lr=0.001):
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.activation_name = activation
        self.activation = getattr(Activations, activation)
        self.lr = lr

        scale = np.sqrt(1.0 / (in_channels * kernel_size * kernel_size))
        self.W = (np.random.randn(out_channels, in_channels, kernel_size, kernel_size) * scale).astype(DTYPE)
        self.b = np.zeros(out_channels, dtype=DTYPE)

        self.last_x = None
        self.last_z = None
        self.dW = None
        self.db = None

    def forward(self, x, training=True):
        batch, h, w, in_c = x.shape
        self.last_x = x.copy()
        if self.padding > 0:
            x = np.pad(x, ((0, 0), (self.padding, self.padding),
                          (self.padding, self.padding), (0, 0)), mode='constant')

        out_h = (h - self.kernel_size) // self.stride + 1
        out_w = (w - self.kernel_size) // self.stride + 1
        output = np.zeros((batch, out_h, out_w, self.out_channels), dtype=DTYPE)

        for b in range(batch):
            for oc in range(self.out_channels):
                for i in range(out_h):
                    for j in range(out_w):
                        h_start = i * self.stride
                        h_end = h_start + self.kernel_size
                        w_start = j * self.stride
                        w_end = w_start + self.kernel_size
                        window = x[b, h_start:h_end, w_start:w_end, :]
                        output[b, i, j, oc] = np.sum(window * self.W[oc]) + self.b[oc]

        self.last_z = output
        return self.activation(output)

    def backward(self, grad):
        if self.activation_name == 'relu':
            grad = grad * (self.last_z > 0)

        batch, out_h, out_w, _ = grad.shape
        self.dW = np.zeros_like(self.W)
        self.db = np.sum(grad, axis=(0, 1, 2))
        dx = np.zeros_like(self.last_x)

        for b in range(batch):
            for oc in range(self.out_channels):
                for i in range(out_h):
                    for j in range(out_w):
                        h_start = i * self.stride
                        h_end = h_start + self.kernel_size
                        w_start = j * self.stride
                        w_end = w_start + self.kernel_size
                        window = self.last_x[b, h_start:h_end, w_start:w_end, :]
                        self.dW[oc] += grad[b, i, j, oc] * window
                        dx[b, h_start:h_end, w_start:w_end, :] += grad[b, i, j, oc] * self.W[oc]

        return dx

    def update(self, lr=None):
        if lr is None:
            lr = self.lr
        if self.dW is not None:
            self.W -= lr * self.dW / self.last_x.shape[0]
            self.b -= lr * self.db / self.last_x.shape[0]


# ---------- MaxPool2D ----------
class MaxPool2D(Layer):
    def __init__(self, pool_size=2, stride=2):
        self.pool_size = pool_size
        self.stride = stride
        self.last_x = None
        self.max_indices = None

    def forward(self, x, training=True):
        batch, h, w, c = x.shape
        self.last_x = x.copy()
        out_h = (h - self.pool_size) // self.stride + 1
        out_w = (w - self.pool_size) // self.stride + 1
        output = np.zeros((batch, out_h, out_w, c), dtype=DTYPE)
        self.max_indices = np.zeros((batch, out_h, out_w, c, 2), dtype=np.int32)

        for b in range(batch):
            for i in range(out_h):
                for j in range(out_w):
                    for ch in range(c):
                        h_start = i * self.stride
                        h_end = h_start + self.pool_size
                        w_start = j * self.stride
                        w_end = w_start + self.pool_size
                        window = x[b, h_start:h_end, w_start:w_end, ch]
                        max_val = np.max(window)
                        max_idx = np.unravel_index(np.argmax(window), window.shape)
                        output[b, i, j, ch] = max_val
                        self.max_indices[b, i, j, ch] = [h_start + max_idx[0], w_start + max_idx[1]]
        return output

    def backward(self, grad):
        batch, out_h, out_w, c = grad.shape
        dx = np.zeros_like(self.last_x)
        for b in range(batch):
            for i in range(out_h):
                for j in range(out_w):
                    for ch in range(c):
                        hi, wi = self.max_indices[b, i, j, ch]
                        dx[b, hi, wi, ch] += grad[b, i, j, ch]
        return dx


# ---------- LSTM Cell ----------
class LSTMCell:
    def __init__(self, input_dim, hidden_dim, lr=0.001):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.lr = lr
        limit = np.sqrt(1.0 / (input_dim + hidden_dim))

        self.W_i = (np.random.randn(input_dim, hidden_dim) * limit).astype(DTYPE)
        self.U_i = (np.random.randn(hidden_dim, hidden_dim) * limit).astype(DTYPE)
        self.b_i = np.zeros(hidden_dim, dtype=DTYPE)

        self.W_f = (np.random.randn(input_dim, hidden_dim) * limit).astype(DTYPE)
        self.U_f = (np.random.randn(hidden_dim, hidden_dim) * limit).astype(DTYPE)
        self.b_f = np.zeros(hidden_dim, dtype=DTYPE)

        self.W_o = (np.random.randn(input_dim, hidden_dim) * limit).astype(DTYPE)
        self.U_o = (np.random.randn(hidden_dim, hidden_dim) * limit).astype(DTYPE)
        self.b_o = np.zeros(hidden_dim, dtype=DTYPE)

        self.W_c = (np.random.randn(input_dim, hidden_dim) * limit).astype(DTYPE)
        self.U_c = (np.random.randn(hidden_dim, hidden_dim) * limit).astype(DTYPE)
        self.b_c = np.zeros(hidden_dim, dtype=DTYPE)

        self.cache = None

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -30, 30)))

    def _tanh(self, x):
        return np.tanh(np.clip(x, -10, 10))

    def forward(self, x, h_prev, c_prev):
        i = self._sigmoid(np.dot(x, self.W_i) + np.dot(h_prev, self.U_i) + self.b_i)
        f = self._sigmoid(np.dot(x, self.W_f) + np.dot(h_prev, self.U_f) + self.b_f)
        o = self._sigmoid(np.dot(x, self.W_o) + np.dot(h_prev, self.U_o) + self.b_o)
        g = self._tanh(np.dot(x, self.W_c) + np.dot(h_prev, self.U_c) + self.b_c)

        c_t = f * c_prev + i * g
        h_t = o * self._tanh(c_t)

        self.cache = (x, h_prev, c_prev, i, f, o, g, c_t, h_t)
        return h_t, c_t

    def backward(self, dh_next, dc_next):
        x, h_prev, c_prev, i, f, o, g, c_t, h_t = self.cache
        batch_size = x.shape[0]

        dtanh = dh_next * o * (1 - self._tanh(c_t) ** 2)
        dc_t = dc_next + dtanh

        di = dc_t * g * i * (1 - i)
        df = dc_t * c_prev * f * (1 - f)
        do = dh_next * self._tanh(c_t) * o * (1 - o)
        dg = dc_t * i * (1 - g ** 2)

        self.dW_i = np.dot(x.T, di) / batch_size
        self.dU_i = np.dot(h_prev.T, di) / batch_size
        self.db_i = np.sum(di, axis=0) / batch_size

        self.dW_f = np.dot(x.T, df) / batch_size
        self.dU_f = np.dot(h_prev.T, df) / batch_size
        self.db_f = np.sum(df, axis=0) / batch_size

        self.dW_o = np.dot(x.T, do) / batch_size
        self.dU_o = np.dot(h_prev.T, do) / batch_size
        self.db_o = np.sum(do, axis=0) / batch_size

        self.dW_c = np.dot(x.T, dg) / batch_size
        self.dU_c = np.dot(h_prev.T, dg) / batch_size
        self.db_c = np.sum(dg, axis=0) / batch_size

        dx = (np.dot(di, self.W_i.T) + np.dot(df, self.W_f.T) +
              np.dot(do, self.W_o.T) + np.dot(dg, self.W_c.T))

        dh_prev = (np.dot(di, self.U_i.T) + np.dot(df, self.U_f.T) +
                   np.dot(do, self.U_o.T) + np.dot(dg, self.U_c.T))

        dc_prev = dc_t * f
        return dx, dh_prev, dc_prev

    def update(self, lr=None):
        if lr is None:
            lr = self.lr
        self.W_i -= lr * self.dW_i
        self.U_i -= lr * self.dU_i
        self.b_i -= lr * self.db_i
        self.W_f -= lr * self.dW_f
        self.U_f -= lr * self.dU_f
        self.b_f -= lr * self.db_f
        self.W_o -= lr * self.dW_o
        self.U_o -= lr * self.dU_o
        self.b_o -= lr * self.db_o
        self.W_c -= lr * self.dW_c
        self.U_c -= lr * self.dU_c
        self.b_c -= lr * self.db_c


# ---------- LSTM (چندلایه) ----------
class LSTM(Layer):
    def __init__(self, input_dim, hidden_dim, num_layers=1, lr=0.001):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.lr = lr
        self.cells = [LSTMCell(input_dim if i == 0 else hidden_dim, hidden_dim, lr) for i in range(num_layers)]
        self.caches = []

    def forward(self, x, training=True):
        batch, seq_len, _ = x.shape
        outputs = x
        self.caches = []
        for layer_idx, cell in enumerate(self.cells):
            h = np.zeros((batch, self.hidden_dim), dtype=DTYPE)
            c = np.zeros((batch, self.hidden_dim), dtype=DTYPE)
            layer_outputs = np.zeros((batch, seq_len, self.hidden_dim), dtype=DTYPE)
            layer_caches = []
            for t in range(seq_len):
                h, c = cell.forward(outputs[:, t, :], h, c)
                layer_outputs[:, t, :] = h
                layer_caches.append((h, c))
            outputs = layer_outputs
            self.caches.append(layer_caches)
        return outputs

    def backward(self, grad):
        batch, seq_len, _ = grad.shape
        for layer_idx in range(self.num_layers - 1, -1, -1):
            cell = self.cells[layer_idx]
            caches = self.caches[layer_idx]
            dh_next = np.zeros((batch, self.hidden_dim), dtype=DTYPE)
            dc_next = np.zeros((batch, self.hidden_dim), dtype=DTYPE)
            for t in range(seq_len - 1, -1, -1):
                grad_t = grad[:, t, :] + dh_next
                dx, dh_next, dc_next = cell.backward(grad_t, dc_next)
                if layer_idx > 0:
                    grad[:, t, :] = dx
        return grad

    def update(self, lr=None):
        for cell in self.cells:
            cell.update(lr)


# ---------- Attention (ساده) ----------
class Attention(Layer):
    def __init__(self, hidden_dim):
        self.hidden_dim = hidden_dim
        self.W = (np.random.randn(hidden_dim, hidden_dim) * 0.1).astype(DTYPE)
        self.v = (np.random.randn(hidden_dim, 1) * 0.1).astype(DTYPE)
        self.last_weights = None

    def forward(self, encoder_outputs, decoder_hidden=None, training=True):
        batch, seq_len, hidden_dim = encoder_outputs.shape
        if decoder_hidden is None:
            decoder_hidden = np.mean(encoder_outputs, axis=1)
        scores = np.zeros((batch, seq_len), dtype=DTYPE)
        for b in range(batch):
            for t in range(seq_len):
                energy = Activations.tanh(encoder_outputs[b, t] @ self.W + decoder_hidden[b] @ self.W)
                scores[b, t] = (energy @ self.v).item()
        self.last_weights = Activations.softmax(scores)
        context = np.zeros((batch, hidden_dim), dtype=DTYPE)
        for b in range(batch):
            for t in range(seq_len):
                context[b] += self.last_weights[b, t] * encoder_outputs[b, t]
        return context, self.last_weights

    def backward(self, grad_context):
        return grad_context
# ImanAILite/layers.py - اضافه کردن لایه Embedding در انتهای فایل

# ========== اضافه کنید به انتهای فایل ==========

# ---------- Embedding ----------
class Embedding(Layer):
    """لایه Embedding برای تبدیل کلمات به بردار"""
    
    def __init__(self, vocab_size, embed_dim, lr=0.001):
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.lr = lr
        
        scale = np.sqrt(1.0 / vocab_size)
        self.W = (np.random.randn(vocab_size, embed_dim) * scale).astype(DTYPE)
        self.dW = None
        self.last_input = None
    
    def forward(self, x, training=True):
        self.last_input = x
        return self.W[x]
    
    def backward(self, grad):
        self.dW = np.zeros_like(self.W)
        # برای هر نمونه در batch
        for i, idx in enumerate(self.last_input.flatten()):
            if 0 <= idx < self.vocab_size:
                self.dW[idx] += grad[i]
        return None
    
    def update(self, lr=None):
        if lr is None:
            lr = self.lr
        if self.dW is not None:
            self.W -= lr * self.dW        