# ImanAILite/models.py
import numpy as np
import pickle
import os
from .activations import Activations, Losses
from .layers import Dense, Dropout, BatchNorm, Flatten, LSTM, Attention
from .tokenizer import TextTokenizer
from .utils import gradient_clipping, LearningRateScheduler, ModelCheckpoint

DTYPE = np.float32


class NeuralNetwork:
    def __init__(self, name="ImanNet"):
        self.name = name
        self.layers = []
        self.loss_history = []
        self.val_loss_history = []
        self.loss_type = 'mse'
        
        # قابلیت‌های جدید
        self.optimizer = None
        self.optimizer_name = 'sgd'
        self.clip_norm = 1.0
        self.lr_scheduler = None
        self.checkpoint = None
        self.current_epoch = 0

    def add(self, layer):
        self.layers.append(layer)
        return self

    def compile(self, loss='mse', optimizer='sgd', lr=0.001, clip_norm=1.0):
        """
        کامپایل مدل با تنظیمات پیشرفته
        
        Args:
            loss: تابع هزینه ('mse', 'mae', 'cross_entropy', 'binary_cross_entropy')
            optimizer: بهینه‌ساز ('sgd', 'adam', 'rmsprop', 'adamw')
            lr: نرخ یادگیری
            clip_norm: حداکثر نرم برای gradient clipping (0 = غیرفعال)
        """
        self.loss_type = loss
        self.clip_norm = clip_norm
        self.optimizer_name = optimizer
        
        # انتخاب بهینه‌ساز
        if optimizer == 'adam':
            from .optimizers import Adam
            self.optimizer = Adam(lr=lr)
        elif optimizer == 'rmsprop':
            from .optimizers import RMSprop
            self.optimizer = RMSprop(lr=lr)
        elif optimizer == 'adamw':
            from .optimizers import AdamW
            self.optimizer = AdamW(lr=lr)
        else:  # 'sgd'
            from .optimizers import SGD
            self.optimizer = SGD(lr=lr)
        
        print(f"🎯 Model compiled | Loss: {loss} | Optimizer: {optimizer} | LR: {lr} | Clip Norm: {clip_norm if clip_norm > 0 else 'OFF'}")
        return self
    
    def set_lr_scheduler(self, strategy='step', **kwargs):
        """
        فعال کردن Learning Rate Scheduler
        
        Args:
            strategy: 'step', 'exponential', 'plateau'
            **kwargs: پارامترهای scheduler (step_size, gamma, patience, factor)
        """
        if self.optimizer is None:
            print("⚠️ Please compile the model first!")
            return self
        
        initial_lr = self.optimizer.lr if hasattr(self.optimizer, 'lr') else 0.001
        self.lr_scheduler = LearningRateScheduler(
            self.optimizer,
            initial_lr=initial_lr,
            strategy=strategy,
            **kwargs
        )
        print(f"📉 LR Scheduler enabled: {strategy}")
        return self
    
    def set_checkpoint(self, save_dir='checkpoints', **kwargs):
        """
        فعال کردن Model Checkpoint (ذخیره خودکار بهترین مدل)
        
        Args:
            save_dir: مسیر ذخیره فایل‌ها
            **kwargs: monitor, save_best_only, save_weights_only, period
        """
        os.makedirs(save_dir, exist_ok=True)
        self.checkpoint = ModelCheckpoint(save_dir=save_dir, **kwargs)
        print(f"💾 Checkpoint enabled: {save_dir}")
        return self

    def forward(self, x, training=True):
        for layer in self.layers:
            x = layer.forward(x, training)
        return x

    def backward(self, grad):
        for layer in reversed(self.layers):
            grad = layer.backward(grad)
        return grad

    def _collect_params_and_grads(self):
        """جمع‌آوری همه پارامترها و گرادیان‌ها از لایه‌ها"""
        params = []
        grads = []
        
        for layer in self.layers:
            # لایه‌های Dense و Conv2D
            if hasattr(layer, 'W') and hasattr(layer, 'dW'):
                params.append(layer.W)
                grads.append(layer.dW)
                params.append(layer.b)
                grads.append(layer.db)
            
            # لایه‌های BatchNorm
            elif hasattr(layer, 'gamma') and hasattr(layer, 'dgamma'):
                params.append(layer.gamma)
                grads.append(layer.dgamma)
                params.append(layer.beta)
                grads.append(layer.dbeta)
            
            # لایه‌های LSTM
            elif hasattr(layer, 'cells'):
                for cell in layer.cells:
                    lstm_params = [
                        cell.W_i, cell.U_i, cell.b_i,
                        cell.W_f, cell.U_f, cell.b_f,
                        cell.W_o, cell.U_o, cell.b_o,
                        cell.W_c, cell.U_c, cell.b_c
                    ]
                    lstm_grads = [
                        cell.dW_i, cell.dU_i, cell.db_i,
                        cell.dW_f, cell.dU_f, cell.db_f,
                        cell.dW_o, cell.dU_o, cell.db_o,
                        cell.dW_c, cell.dU_c, cell.db_c
                    ]
                    params.extend(lstm_params)
                    grads.extend(lstm_grads)
        
        return params, grads
    
    def _apply_gradients(self):
        """اعمال گرادیان‌ها با بهینه‌ساز و gradient clipping"""
        params, grads = self._collect_params_and_grads()
        
        if not params or not self.optimizer:
            return
        
        # Gradient Clipping
        if self.clip_norm > 0:
            grads = gradient_clipping(grads, max_norm=self.clip_norm)
        
        # بروزرسانی با بهینه‌ساز
        updated_params = self.optimizer.update(params, grads)
        
        # برگرداندن پارامترهای بروزرسانی شده به لایه‌ها
        idx = 0
        for layer in self.layers:
            if hasattr(layer, 'W') and hasattr(layer, 'dW'):
                layer.W = updated_params[idx]; idx += 1
                layer.b = updated_params[idx]; idx += 1
            elif hasattr(layer, 'gamma') and hasattr(layer, 'dgamma'):
                layer.gamma = updated_params[idx]; idx += 1
                layer.beta = updated_params[idx]; idx += 1
            elif hasattr(layer, 'cells'):
                for cell in layer.cells:
                    cell.W_i = updated_params[idx]; idx += 1
                    cell.U_i = updated_params[idx]; idx += 1
                    cell.b_i = updated_params[idx]; idx += 1
                    cell.W_f = updated_params[idx]; idx += 1
                    cell.U_f = updated_params[idx]; idx += 1
                    cell.b_f = updated_params[idx]; idx += 1
                    cell.W_o = updated_params[idx]; idx += 1
                    cell.U_o = updated_params[idx]; idx += 1
                    cell.b_o = updated_params[idx]; idx += 1
                    cell.W_c = updated_params[idx]; idx += 1
                    cell.U_c = updated_params[idx]; idx += 1
                    cell.b_c = updated_params[idx]; idx += 1

    def _compute_loss(self, y_pred, y_true):
        if self.loss_type == 'mse':
            return Losses.mse(y_pred, y_true)
        elif self.loss_type == 'mae':
            return Losses.mae(y_pred, y_true)
        elif self.loss_type == 'cross_entropy':
            return Losses.cross_entropy(y_pred, y_true)
        return Losses.mse(y_pred, y_true)

    def _compute_grad(self, y_pred, y_true):
        if self.loss_type == 'mse':
            return 2 * (y_pred - y_true) / y_pred.shape[0]
        elif self.loss_type == 'mae':
            return np.sign(y_pred - y_true) / y_pred.shape[0]
        elif self.loss_type in ['cross_entropy', 'binary_cross_entropy']:
            return y_pred - y_true
        return (y_pred - y_true) / y_pred.shape[0]

    def fit(self, X, y, epochs=100, batch_size=32, lr=0.001, learning_rate=None, 
            validation_split=0.1, verbose=True, use_lr_scheduler=False):
        """
        آموزش شبکه عصبی با پشتیبانی از قابلیت‌های پیشرفته
        
        Args:
            use_lr_scheduler: فعال کردن Learning Rate Scheduler
        """
        # پشتیبانی از هر دو نام پارامتر
        if learning_rate is not None:
            lr = learning_rate
            
        n_samples = len(X)
        self.X_mean = np.mean(X, axis=0, keepdims=True)
        self.X_std = np.std(X, axis=0, keepdims=True) + 1e-7
        X_norm = (X - self.X_mean) / self.X_std

        val_size = int(n_samples * validation_split)
        indices = np.random.permutation(n_samples)
        X_train = X_norm[indices[val_size:]]
        X_val = X_norm[indices[:val_size]]
        y_train = y[indices[val_size:]]
        y_val = y[indices[:val_size]]

        if self.loss_type in ['mse', 'mae']:
            self.y_mean = np.mean(y_train, axis=0, keepdims=True)
            self.y_std = np.std(y_train, axis=0, keepdims=True) + 1e-7
            y_train = (y_train - self.y_mean) / self.y_std

        print(f"\n🚀 Training {self.name} (samples: {n_samples})")
        best_val_loss = float('inf')
        patience = 10
        patience_counter = 0

        for epoch in range(epochs):
            self.current_epoch = epoch
            idx = np.random.permutation(len(X_train))
            X_shuffled = X_train[idx]
            y_shuffled = y_train[idx]

            epoch_loss = 0
            n_batches = 0

            for start in range(0, len(X_train), batch_size):
                end = min(start + batch_size, len(X_train))
                X_batch = X_shuffled[start:end]
                y_batch = y_shuffled[start:end]

                y_pred = self.forward(X_batch, training=True)
                loss = self._compute_loss(y_pred, y_batch)
                epoch_loss += loss
                n_batches += 1

                grad = self._compute_grad(y_pred, y_batch)
                self.backward(grad)
                
                # استفاده از بهینه‌ساز جدید با Gradient Clipping
                self._apply_gradients()

            avg_loss = epoch_loss / n_batches
            self.loss_history.append(avg_loss)

            if val_size > 0:
                y_val_pred = self.forward(X_val, training=False)
                if self.loss_type in ['mse', 'mae']:
                    y_val_pred = y_val_pred * self.y_std + self.y_mean
                val_loss = self._compute_loss(y_val_pred, y_val)
                self.val_loss_history.append(val_loss)
                
                # بروزرسانی Learning Rate Scheduler
                if use_lr_scheduler and self.lr_scheduler:
                    self.lr_scheduler.step(current_loss=val_loss)
                
                # ذخیره checkpoint
                if self.checkpoint:
                    self.checkpoint.on_epoch_end(epoch, self, val_loss)

                if verbose and (epoch + 1) % 10 == 0:
                    lr_info = f" | LR: {self.lr_scheduler.get_lr():.6f}" if self.lr_scheduler else ""
                    print(f"  Epoch {epoch+1:3d}/{epochs} | Loss: {avg_loss:.6f} | Val Loss: {val_loss:.6f}{lr_info}")

                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= patience:
                        # بارگذاری بهترین مدل از checkpoint
                        if self.checkpoint:
                            self.checkpoint.load_best(self)
                        if verbose:
                            print(f"  🛑 Early stopping at epoch {epoch+1}")
                        break
            else:
                if verbose and (epoch + 1) % 10 == 0:
                    print(f"  Epoch {epoch+1:3d}/{epochs} | Loss: {avg_loss:.6f}")

        # بارگذاری بهترین مدل در پایان
        if self.checkpoint:
            self.checkpoint.load_best(self)
            
        print(f"✅ Training complete. Best val loss: {best_val_loss:.6f}")
        return self.loss_history

    def predict(self, X):
        X_norm = (X - self.X_mean) / self.X_std
        y_pred = self.forward(X_norm, training=False)
        if hasattr(self, 'y_mean'):
            y_pred = y_pred * self.y_std + self.y_mean
        return y_pred

    def summary(self):
        print(f"\n{'='*50}")
        print(f"🧠 {self.name}")
        print(f"{'='*50}")
        total_params = 0
        for i, layer in enumerate(self.layers):
            if hasattr(layer, 'W'):
                params = layer.W.size + layer.b.size
                total_params += params
                print(f"{i+1:2d}. {layer.__class__.__name__:12s} {params:>8,} params")
            elif hasattr(layer, 'cells'):
                params = 0
                for cell in layer.cells:
                    params += (cell.W_i.size + cell.U_i.size + cell.b_i.size +
                               cell.W_f.size + cell.U_f.size + cell.b_f.size +
                               cell.W_o.size + cell.U_o.size + cell.b_o.size +
                               cell.W_c.size + cell.U_c.size + cell.b_c.size)
                total_params += params
                print(f"{i+1:2d}. {layer.__class__.__name__:12s} {params:>8,} params")
            else:
                print(f"{i+1:2d}. {layer.__class__.__name__:12s}")
        print(f"{'-'*50}")
        print(f"   Total: {total_params:,} params")
        if self.optimizer_name:
            print(f"   Optimizer: {self.optimizer_name}")
        if self.clip_norm > 0:
            print(f"   Gradient Clipping: {self.clip_norm}")
        print(f"{'='*50}\n")

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump({
                'name': self.name,
                'layers': self.layers,
                'loss_history': self.loss_history,
                'val_loss_history': self.val_loss_history,
                'loss_type': self.loss_type,
                'optimizer_name': self.optimizer_name,
                'clip_norm': self.clip_norm,
                'X_mean': getattr(self, 'X_mean', None),
                'X_std': getattr(self, 'X_std', None),
                'y_mean': getattr(self, 'y_mean', None),
                'y_std': getattr(self, 'y_std', None),
            }, f)
        print(f"💾 Model saved to {path}")

    def load(self, path):
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self.__dict__.update(data)
        print(f"📂 Model loaded from {path}")
        return self


# ============================================================
# ImanTransformer (ساده شده برای 32-bit)
# ============================================================

class ImanTransformer:
    """Transformer ساده برای تولید متن (بهینه برای 32-bit)"""
    
    def __init__(self, vocab_size=10000, embed_dim=128, num_heads=8, num_layers=4, ff_dim=512):
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.ff_dim = ff_dim
        self.max_len = 100
        self.optimizer_name = 'adam'
        self.learning_rate = 0.001
        
        # لایه‌های ساده (نسخه سبک)
        scale = np.sqrt(1.0 / vocab_size)
        self.token_embedding = (np.random.randn(vocab_size, embed_dim) * scale).astype(DTYPE)
        
        from .layers import Dense
        self.fc1 = Dense(embed_dim, ff_dim, 'relu')
        self.fc2 = Dense(ff_dim, embed_dim, 'linear')
        self.output_layer = Dense(embed_dim, vocab_size, 'linear')
        
        self.loss_history = []
    
    def forward(self, x, training=True):
        batch, seq_len = x.shape
        x = self.token_embedding[x]
        x = self.fc1.forward(x, training)
        x = self.fc2.forward(x, training)
        x = self.output_layer.forward(x, training)
        return x
    
    def train(self, tokenizer, texts, epochs=50, batch_size=8, lr=0.001):
        data = []
        for text in texts:
            tokens = tokenizer.encode(text, max_len=self.max_len)
            if len(tokens) > 1:
                for i in range(1, len(tokens)):
                    data.append((tokens[:i], tokens[i]))
        
        if len(data) < 5:
            print(f"⚠️ Not enough data: {len(data)} samples")
            return []
        
        print(f"🚀 Training Transformer on {len(data)} samples")
        
        for epoch in range(epochs):
            idx = np.random.permutation(len(data))
            epoch_loss = 0
            n_batches = 0
            
            for start in range(0, len(data), batch_size):
                end = min(start + batch_size, len(data))
                batch_X = []
                batch_y = []
                
                for i in idx[start:end]:
                    X_seq, y_seq = data[i]
                    padded_X = X_seq + [0] * (self.max_len - len(X_seq))
                    batch_X.append(padded_X[:self.max_len])
                    batch_y.append(y_seq)
                
                X_batch = np.array(batch_X, dtype=np.int32)
                y_batch = np.array(batch_y, dtype=np.int32)
                
                logits = self.forward(X_batch, training=True)
                logits_flat = logits.reshape(-1, self.vocab_size)
                y_flat = y_batch.reshape(-1)
                
                probs = Activations.softmax(logits_flat)
                loss = -np.mean(np.log(probs[np.arange(len(y_flat)), y_flat] + 1e-7))
                
                grad = probs.copy()
                grad[np.arange(len(y_flat)), y_flat] -= 1
                grad = grad.reshape(logits.shape)
                
                grad = self.output_layer.backward(grad)
                grad = self.fc2.backward(grad)
                grad = self.fc1.backward(grad)
                
                self.output_layer.update(lr)
                self.fc2.update(lr)
                self.fc1.update(lr)
                
                epoch_loss += loss
                n_batches += 1
            
            avg_loss = epoch_loss / max(n_batches, 1)
            self.loss_history.append(avg_loss)
            
            if (epoch + 1) % 10 == 0:
                print(f"  Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}")
        
        print("✅ Transformer training complete")
        return self.loss_history
    
    def generate(self, tokenizer, start_text, max_new_tokens=50, temperature=0.8):
        tokens = tokenizer.encode(start_text, max_len=self.max_len)
        generated = list(tokens)
        
        for _ in range(max_new_tokens):
            context = np.array([generated[-self.max_len:]], dtype=np.int32)
            logits = self.forward(context, training=False)[0, -1, :]
            logits = logits / max(temperature, 0.1)
            exp_logits = np.exp(np.clip(logits - np.max(logits), -30, 30))
            probs = exp_logits / (np.sum(exp_logits) + 1e-7)
            next_token = np.random.choice(self.vocab_size, p=probs)
            generated.append(next_token)
            if next_token == tokenizer.word_to_idx.get('<END>', 3):
                break
        
        return tokenizer.decode(generated)
    
    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump({
                'vocab_size': self.vocab_size,
                'embed_dim': self.embed_dim,
                'num_heads': self.num_heads,
                'num_layers': self.num_layers,
                'ff_dim': self.ff_dim,
                'max_len': self.max_len,
                'token_embedding': self.token_embedding,
                'loss_history': self.loss_history,
                'optimizer_name': self.optimizer_name,
            }, f)
        print(f"💾 Transformer saved to {path}")
    
    def load(self, path):
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.vocab_size = data['vocab_size']
            self.embed_dim = data['embed_dim']
            self.num_heads = data['num_heads']
            self.num_layers = data['num_layers']
            self.ff_dim = data['ff_dim']
            self.max_len = data.get('max_len', 100)
            self.token_embedding = data['token_embedding']
            self.loss_history = data.get('loss_history', [])
            self.optimizer_name = data.get('optimizer_name', 'adam')
            
            from .layers import Dense
            self.fc1 = Dense(self.embed_dim, self.ff_dim, 'relu')
            self.fc2 = Dense(self.ff_dim, self.embed_dim, 'linear')
            self.output_layer = Dense(self.embed_dim, self.vocab_size, 'linear')
        print(f"📂 Transformer loaded from {path}")
        return self