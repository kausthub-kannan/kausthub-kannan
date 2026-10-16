## 1. SageMaker ML Workflow

SageMaker is built to handle the **entire machine learning lifecycle**:

```
Prepare Data → Train Model → Deploy Model → Monitor & Iterate
```

| Component                       | Storage / Service               |
| ------------------------------- | ------------------------------- |
| Training & Inference data       | Amazon S3, RDS, Amazon Redshift |
| Model artifacts (post-training) | Amazon S3                       |
| Training & Inference code       | Docker images in Amazon ECR     |
| Model interaction               | SageMaker Endpoint              |

---

## 2. Core SageMaker Constructs

### 2.1 Processing Jobs

- Data is **copied from S3** into a processing container
- Container runs **built-in or user-defined algorithms**
- Processed output is **written back to S3**

### 2.2 Training Jobs

You must provide:

- **Input data URI** (S3 path)
- **Output artifacts path** (S3 path)
- **Compute resource config** (instance type, count)
- **ECR image URI** for the training code

### 2.3 Deployment Options

|Mode|Use Case|
|---|---|
|**Persistent Real-Time Endpoint**|Individual, low-latency predictions|
|**Batch Transform**|Bulk predictions over an entire dataset (no persistent endpoint needed)|

**Additional Deployment Features:**

- **Inference Pipelines** — chain multiple containers (pre-processing → model → post-processing)
- **SageMaker Neo** — compile and optimize models for edge devices
- **Elastic Inference** — attach fractional GPU acceleration to CPU instances for deep learning

---

## 3. SageMaker Input Modes

|Mode|Description|Best For|
|---|---|---|
|**S3 File Mode**|Copies full training data from S3 to local container directory before training|Small-to-medium datasets|
|**S3 Fast File Mode**|Streams data directly from S3; no full download; supports random access but optimized for sequential|Large datasets, faster job startup|
|**Pipe Mode**|Streams data from S3 into container via named pipe; largely superseded by Fast File Mode|Legacy use cases|
|**S3 Express One Zone**|High-performance single-AZ S3; compatible with File, Fast File, and Pipe modes|Ultra-low latency workloads|
|**FSx for Lustre**|Scales to 100s of GB/s throughput and millions of IOPS with sub-millisecond latency; single-AZ, requires VPC|HPC / very large-scale training|
|**EFS**|Shared file system mountable across multiple instances|Distributed training with shared data|

---

## 4. Built-In Algorithms

### 4.1 Linear Learner

**Task:** Regression and Binary/Multi-class Classification

|Property|Detail|
|---|---|
|**Input formats**|RecordIO-wrapped protobuf (Float32), CSV (first column = label)|
|**Input modes**|File and Pipe|
|**Pre-processing**|Automatic normalization; data should be **shuffled** before training|
|**Optimizer**|SGD — selectable variant: Adam, AdaGrad, SGD|
|**Regularization**|L1 (lasso) via `l1`, L2 (ridge) via `wd` (weight decay)|
|**Key feature**|Trains **multiple models in parallel**, selects best|
|**Compute**|Multi-CPU sufficient; single GPU optional|

**Key Hyperparameters:**

- `learning_rate` — step size for optimizer
- `mini_batch_size` — samples per gradient update
- `l1` — L1 regularization weight
- `wd` — L2 / weight decay
- `target_precision` / `target_recall` — for classification optimization
- `balance_multiclass_weights` — assigns equal importance to all classes

---

### 4.2 XGBoost

**Task:** Classification and Regression (ensemble of boosted decision trees)

|Property|Detail|
|---|---|
|**Input formats**|CSV, LibSVM, RecordIO-protobuf, Parquet|
|**Compute**|Memory-bound → **m5 instances** recommended|
|**GPU support**|v1.2: single GPU; v1.5+: multi-GPU (CSV/Parquet only, set `tree_method=gpu_hist`)|

**Key Hyperparameters:**

| Parameter          | Purpose                                                                                  |
| ------------------ | ---------------------------------------------------------------------------------------- |
| `eta`              | Step size shrinkage (learning rate) — prevents overfitting                               |
| `gamma`            | Minimum loss reduction required to make a further partition on a leaf                    |
| `max_depth`        | Max tree depth — too high causes overfitting                                             |
| `subsample`        | Fraction of training samples used per tree — controls overfitting                        |
| `alpha`            | L1 regularization                                                                        |
| `lambda`           | L2 regularization                                                                        |
| `scale_pos_weight` | Balances positive and negative class weights (useful for imbalanced datasets)            |
| `eval_metric`      | Metric to optimize (e.g., `auc` when false positive rate matters more than raw accuracy) |

---

### 4.3 LightGBM

**Task:** Classification and Regression (gradient boosted trees, faster than XGBoost for large datasets)

| Property          | Detail                                                                                  |
| ----------------- | --------------------------------------------------------------------------------------- |
| **Input formats** | CSV, LibSVM, Parquet                                                                    |
| **Compute**       | CPU-optimized; GPU support available                                                    |
| **Key advantage** | Leaf-wise tree growth (vs. level-wise in XGBoost) → faster, more accurate on large data |

**Key Hyperparameters:**

- `num_leaves` — controls model complexity
- `learning_rate` — step size
- `min_data_in_leaf` — prevents overfitting on small leaves
- `feature_fraction` / `bagging_fraction` — sampling for speed and regularization
- `lambda_l1` / `lambda_l2` — regularization

---

### 4.4 Seq2Seq

**Task:** Sequence-to-sequence tasks — machine translation, text summarization, speech-to-text

|Property|Detail|
|---|---|
|**Architecture**|Encoder-Decoder RNN with attention mechanism|
|**Input format**|RecordIO-protobuf (tokenized integer sequences)|
|**Compute**|GPU required (single GPU instance)|
|**Pre-trained embeddings**|Supported|

**Key Hyperparameters:**

- `max_seq_len_source` / `max_seq_len_target`
- `num_layers_encoder` / `num_layers_decoder`
- `num_embed` — embedding dimensions
- `batch_size`, `learning_rate`, `optimizer_type`

---

### 4.5 DeepAR

**Task:** **Time series forecasting** — probabilistic forecasts across multiple related time series

| Property          | Detail                                                       |
| ----------------- | ------------------------------------------------------------ |
| **Architecture**  | Autoregressive RNN (LSTM)                                    |
| **Input format**  | JSON Lines (`.jsonl`)                                        |
| **Key advantage** | Trains a single global model across many related time series |
| **Output**        | Probabilistic forecast (mean + quantiles)                    |
| **Compute**       | CPU or GPU                                                   |

**Key Hyperparameters:**

- `prediction_length` — number of time steps to forecast
- `context_length` — number of historical time steps used
- `num_layers`, `num_cells`
- `dropout_rate`, `learning_rate`, `epochs`
- `likelihood` — distribution type (Gaussian, negative binomial, etc.)

---

### 4.6 BlazingText

**Task:** Text classification and word embedding generation

|Mode|Task|Notes|
|---|---|---|
|`supervised`|Multi-class / multi-label text classification|Analogous to fastText|
|`Word2Vec` (`cbow` / `skipgram`)|Word embeddings|Unsupervised|
|`batch_skipgram`|Word embeddings at scale|Distributed, multi-instance|

|Property|Detail|
|---|---|
|**Input format**|One sentence per line; labels prefixed with `__label__` (supervised mode)|
|**Compute**|GPU recommended for `supervised`; CPU for Word2Vec|

**Key Hyperparameters:**

- `mode` — `supervised`, `cbow`, `skipgram`, `batch_skipgram`
- `vector_dim` — embedding dimensions
- `epochs`, `learning_rate`, `min_count`, `word_ngrams`

---

### 4.7 Object2Vec

**Task:** General-purpose **embedding** of high-dimensional objects (sentences, users, products) into a dense vector space for similarity, classification, or recommendation

|Property|Detail|
|---|---|
|**Architecture**|Two-tower encoder + comparator layer|
|**Input**|Paired objects (e.g., sentence pairs, user-item pairs)|
|**Compute**|Single GPU instance recommended|

**Key Hyperparameters:**

- `enc0_network` / `enc1_network` — encoder types (`hcnn`, `bilstm`, `pooled_embedding`)
- `comparator_list` — comparison operations (hadamard, concat, etc.)
- `num_classes`, `dropout`, `learning_rate`, `epochs`

---

### 4.8 Object Detection

**Task:** Detect and localize objects in images — outputs bounding boxes + class labels

|Property|Detail|
|---|---|
|**Framework**|MXNet-based (Single Shot Multibox Detector — SSD)|
|**Input format**|RecordIO or image + JSON manifest|
|**Compute**|GPU required (multi-GPU supported)|
|**Transfer learning**|Supports pre-trained VGG, ResNet backbones|

**Key Hyperparameters:**

- `num_classes`, `num_training_samples`
- `base_network` — backbone (`vgg-16`, `resnet-50`)
- `mini_batch_size`, `learning_rate`, `epochs`
- `nms_threshold` — Non-Maximum Suppression threshold

---

### 4.9 Image Classification

**Task:** Assign class labels to entire images (multi-class)

|Property|Detail|
|---|---|
|**Framework**|MXNet (ResNet-based)|
|**Input format**|RecordIO or image files + `.lst` manifest|
|**Compute**|GPU required; multi-GPU and multi-instance supported|
|**Modes**|Full training from scratch **or** fine-tuning a pre-trained model|

**Key Hyperparameters:**

- `num_classes`, `num_training_samples`
- `use_pretrained_model` — `0` or `1`
- `num_layers` — depth of ResNet (18, 34, 50, 101, 152, 200)
- `mini_batch_size`, `learning_rate`, `epochs`, `augmentation_type`

---

### 4.10 Semantic Segmentation

**Task:** Pixel-level classification — assigns a class label to every pixel in an image

|Property|Detail|
|---|---|
|**Architecture**|Fully Convolutional Network (FCN), PSP, DeepLab|
|**Input format**|Images + pixel-level annotation masks|
|**Compute**|Single GPU only (no multi-GPU)|
|**Backbone**|ResNet-50 or ResNet-101|

**Key Hyperparameters:**

- `backbone` — `resnet-50` or `resnet-101`
- `algorithm` — `fcn`, `psp`, `deeplab`
- `num_classes`, `learning_rate`, `epochs`, `mini_batch_size`
- `use_pretrained_model`

---

### 4.11 Random Cut Forest (RCF)

**Task:** **Anomaly detection** in streaming or batch data — assigns an anomaly score to each data point

|Property|Detail|
|---|---|
|**Input format**|RecordIO-protobuf or CSV|
|**Input modes**|File and Pipe|
|**Compute**|CPU-based|
|**Output**|Anomaly score per data point (higher = more anomalous)|

**Key Hyperparameters:**

- `num_trees` — number of trees in the forest
- `num_samples_per_tree` — inversely proportional to expected anomaly ratio (1/ratio)
- `feature_dim` — number of input features

---

### 4.12 Neural Topic Model (NTM)

**Task:** Unsupervised topic modeling — discovers latent topics in a document corpus using a neural network

|Property|Detail|
|---|---|
|**Input format**|RecordIO-protobuf or CSV (bag-of-words vectors)|
|**Compute**|GPU recommended; CPU supported|
|**Output**|Topic-word probability distributions + document-topic mixtures|

**Key Hyperparameters:**

- `num_topics` — number of latent topics to learn
- `encoder_layers`, `encoder_dim`
- `learning_rate`, `batch_size`, `epochs`
- `num_patience_epochs` — early stopping

---

### 4.13 Latent Dirichlet Allocation (LDA)

**Task:** Classical unsupervised topic modeling (Bayesian, non-neural)

|Property|Detail|
|---|---|
|**Input format**|RecordIO-protobuf or CSV (bag-of-words, integer counts)|
|**Compute**|CPU only (single instance)|
|**Note**|Simpler and faster than NTM; good baseline for topic modeling|

**Key Hyperparameters:**

- `num_topics` — number of topics
- `alpha0` — initial guess for Dirichlet concentration parameter
- `max_restarts`, `max_iterations`, `tol`
- `mini_batch_size`

---

### 4.14 K-Nearest Neighbors (KNN)

**Task:** Classification and Regression using nearest-neighbor lookup

|Property|Detail|
|---|---|
|**Input format**|RecordIO-protobuf or CSV (first column = label)|
|**Input modes**|File and Pipe|
|**Compute**|CPU for training; GPU for inference at scale|
|**How it works**|Indexes training data; at inference, finds K nearest points and votes (classification) or averages (regression)|

**Key Hyperparameters:**

- `k` — number of neighbors
- `feature_dim`, `predictor_type` (`classifier` or `regressor`)
- `sample_size` — sub-samples training data for index building
- `index_type` — approximate nearest neighbor algorithm (`faiss.Flat`, `faiss.IVFFlat`, `faiss.IVFPQ`)
- `dimension_reduction_type` / `dimension_reduction_target` — optional PCA pre-reduction

---

### 4.15 K-Means

**Task:** Unsupervised clustering — partitions data into K clusters

|Property|Detail|
|---|---|
|**Input format**|RecordIO-protobuf or CSV|
|**Input modes**|File and Pipe|
|**Compute**|CPU recommended; GPU supported|
|**Algorithm**|Web-scale variant of k-means++ initialization|

**Key Hyperparameters:**

- `k` — number of clusters
- `feature_dim`, `mini_batch_size`
- `extra_center_factor` — initializes `k × factor` centers, reduces to k (improves quality)
- `init_method` — `random` or `kmeans++`
- `epochs`, `local_lloyd_num_trials`

---

### 4.16 Principal Component Analysis (PCA)

**Task:** Dimensionality reduction — projects high-dimensional data into a lower-dimensional space preserving maximum variance

|Property|Detail|
|---|---|
|**Input format**|RecordIO-protobuf or CSV|
|**Input modes**|File and Pipe|
|**Compute**|GPU recommended for large datasets|
|**Modes**|`regular` (small/medium datasets), `randomized` (large datasets — uses approximation)|

**Key Hyperparameters:**

- `num_components` — target number of principal components
- `algorithm_mode` — `regular` or `randomized`
- `subtract_mean` — zero-center data before decomposition
- `extra_components` — extra components computed in randomized mode for accuracy

---

### 4.17 Factorization Machines

**Task:** Classification and Regression — especially suited for **sparse, high-dimensional data** (e.g., click-through rate, recommendation systems)

|Property|Detail|
|---|---|
|**Input format**|RecordIO-protobuf Float32 (**sparse format only**)|
|**Compute**|CPU recommended; GPU for dense data|
|**Key advantage**|Models pairwise feature interactions efficiently even in sparse settings|

**Key Hyperparameters:**

- `feature_dim`, `num_factors` — dimensionality of factorization
- `predictor_type` — `binary_classifier` or `regressor`
- `epochs`, `learning_rate`, `optimizer` (sgd, adam, adagrad)
- `bias_lr` / `linear_lr` / `factors_lr` — separate learning rates per component
- `bias_wd` / `linear_wd` / `factors_wd` — separate regularization per component

---

**Note: Types of Recommendation Systems: Collaborative vs. Content-Based

| Type                        | How it works                                                                                                                                                                 | When to use                                                                                                | AWS tool                                                                                 |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **Collaborative filtering** | Finds patterns from user-item interactions (ratings, clicks, purchases). Predicts based on similarity between users OR similarity between items. Doesn't need item metadata. | Large interaction/behavior datasets; "users like you also bought X"                                        | Spark ML (ALS algorithm) on EMR, or Amazon Personalize                                   |
| **Content-based filtering** | Uses item attributes/features (genre, category, price, description) and matches to a user's own past preferences.                                                            | Works well for new users with some history but sparse cross-user data; good when rich item metadata exists | Custom ML models, feature-based similarity (cosine similarity, TF-IDF for text features) |
| **Hybrid**                  | Combines both — collaborative + content-based                                                                                                                                | Solves the "cold start" problem (new users/items with no interaction history)                              | Amazon Personalize (does this natively)                                                  |
### 4.18 IP Insights

**Task:** **Anomaly detection for IP address usage** — learns typical associations between IPv4 addresses and entity identifiers (e.g., user accounts) and flags unusual pairings

|Property|Detail|
|---|---|
|**Input format**|CSV (entity, IPv4 address)|
|**Compute**|GPU recommended (supports multi-GPU)|
|**Architecture**|Neural network with entity + IP embeddings|
|**Output**|Dot-product compatibility score (low = anomalous pairing)|

**Key Hyperparameters:**

- `num_entity_vectors` — hash size for entity embedding table
- `vector_dim` — embedding dimension
- `epochs`, `learning_rate`, `batch_size`
- `shuffled_negative_sampling_rate` / `random_negative_sampling_rate` — controls negative sample generation during training
- `weight_decay`

---

## 5. Quick Algorithm Selection Reference

|Task|Algorithm(s)|
|---|---|
|Tabular classification / regression|Linear Learner, XGBoost, LightGBM|
|Time series forecasting|DeepAR|
|Text classification|BlazingText (supervised)|
|Word embeddings|BlazingText (Word2Vec), Object2Vec|
|Sequence-to-sequence (translation, summarization)|Seq2Seq|
|Image classification|Image Classification (ResNet)|
|Object detection|Object Detection (SSD)|
|Pixel-level segmentation|Semantic Segmentation|
|Anomaly detection (tabular)|Random Cut Forest|
|Anomaly detection (IP/network)|IP Insights|
|Topic modeling (neural)|Neural Topic Model|
|Topic modeling (classical)|LDA|
|Recommendation / sparse interactions|Factorization Machines|
|Clustering|K-Means|
|Dimensionality reduction|PCA|
|Classification / regression (lookup)|KNN|
|General embeddings (users, items, sentences)|Object2Vec|