import numpy as np

class LinearRegressionScratch:
    def __init__(self):
        self.weights = None
        self.bias = None
    
    def fit(self, X, y):
        X = np.array(X, dtype=np.float64)
        y = np.array(y, dtype=np.float64)
        n_samples, n_features = X.shape
        
        X_b = np.c_[np.ones((n_samples, 1)), X]
        
        try:
            theta = np.linalg.lstsq(X_b, y, rcond=None)[0]
        except:
            theta = np.linalg.pinv(X_b).dot(y)
        
        self.bias = theta[0]
        self.weights = theta[1:]
    
    def predict(self, X):
        X = np.array(X, dtype=np.float64)
        return X.dot(self.weights) + self.bias


class SVMScratch:
    def __init__(self, learning_rate=0.001, n_iters=1000):
        self.lr = learning_rate
        self.n_iters = n_iters
        self.w = None
        self.b = None
    
    def fit(self, X, y):
        X = np.array(X, dtype=np.float64)
        y = np.array(y, dtype=np.float64)
        n_samples, n_features = X.shape
        
        self.w = np.random.randn(n_features) * 0.01
        self.b = 0
        
        y_mean = np.mean(y)
        y_std = np.std(y)
        y_normalized = (y - y_mean) / (y_std + 1e-8)
        
        for _ in range(self.n_iters):
            y_pred = np.dot(X, self.w) + self.b
            
            dw = (1/n_samples) * np.dot(X.T, (y_pred - y_normalized))
            db = (1/n_samples) * np.sum(y_pred - y_normalized)
            
            self.w -= self.lr * dw
            self.b -= self.lr * db
        
        self.y_mean = y_mean
        self.y_std = y_std
    
    def predict(self, X):
        X = np.array(X, dtype=np.float64)
        y_pred = np.dot(X, self.w) + self.b
        return y_pred * self.y_std + self.y_mean


class DecisionTreeScratch:
    def __init__(self, max_depth=10, min_samples_split=10):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree = None
    
    def fit(self, X, y):
        X = np.array(X, dtype=np.float64)
        y = np.array(y, dtype=np.float64)
        self.tree = self._grow_tree(X, y)
    
    def _grow_tree(self, X, y, depth=0):
        n_samples, n_features = X.shape
        
        if depth >= self.max_depth or n_samples < self.min_samples_split or len(np.unique(y)) == 1:
            return np.mean(y)
        
        best_feature, best_threshold = self._best_split(X, y, n_features)
        
        if best_feature is None:
            return np.mean(y)
        
        left_idxs = X[:, best_feature] <= best_threshold
        right_idxs = ~left_idxs
        
        if np.sum(left_idxs) == 0 or np.sum(right_idxs) == 0:
            return np.mean(y)
        
        left = self._grow_tree(X[left_idxs], y[left_idxs], depth + 1)
        right = self._grow_tree(X[right_idxs], y[right_idxs], depth + 1)
        
        return {'feature': best_feature, 'threshold': best_threshold, 'left': left, 'right': right}
    
    def _best_split(self, X, y, n_features):
        best_gain = -float('inf')
        best_feature, best_threshold = None, None
        parent_mse = np.var(y)
        
        for feature in range(n_features):
            thresholds = np.percentile(X[:, feature], [10, 25, 50, 75, 90])
            
            for threshold in thresholds:
                left_idxs = X[:, feature] <= threshold
                right_idxs = ~left_idxs
                
                n_left = np.sum(left_idxs)
                n_right = np.sum(right_idxs)
                
                if n_left < self.min_samples_split or n_right < self.min_samples_split:
                    continue
                
                left_mse = np.var(y[left_idxs]) if n_left > 0 else 0
                right_mse = np.var(y[right_idxs]) if n_right > 0 else 0
                
                weighted_mse = (n_left * left_mse + n_right * right_mse) / len(y)
                gain = parent_mse - weighted_mse
                
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature
                    best_threshold = threshold
        
        return best_feature, best_threshold
    
    def predict(self, X):
        X = np.array(X, dtype=np.float64)
        return np.array([self._traverse_tree(x, self.tree) for x in X])
    
    def _traverse_tree(self, x, node):
        if not isinstance(node, dict):
            return node
        
        if x[node['feature']] <= node['threshold']:
            return self._traverse_tree(x, node['left'])
        return self._traverse_tree(x, node['right'])
