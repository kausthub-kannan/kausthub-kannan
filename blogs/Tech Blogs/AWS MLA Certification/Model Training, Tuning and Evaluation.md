## 1. Activation Functions

Activation functions introduce **non-linearity** into a neural network, allowing it to learn complex patterns. Without them, any deep network collapses to a single linear transformation.

|Function|Formula|Output Range|Use Case|Notes|
|---|---|---|---|---|
|**Sigmoid**|`1 / (1 + e^-x)`|(0, 1)|Binary output layer|Suffers from vanishing gradient; saturates at extremes|
|**Tanh**|`(e^x - e^-x) / (e^x + e^-x)`|(-1, 1)|Hidden layers (RNNs)|Zero-centered; still suffers vanishing gradient|
|**ReLU**|`max(0, x)`|[0, ∞)|Hidden layers (CNNs, DNNs)|Fast, sparse activation; suffers dying ReLU problem|
|**Leaky ReLU**|`max(0.01x, x)`|(-∞, ∞)|Hidden layers|Fixes dying ReLU by allowing small negative gradient|
|**ELU**|`x if x>0, α(e^x - 1) if x≤0`|(-α, ∞)|Hidden layers|Smooth negative side; better than Leaky ReLU in practice|
|**Softmax**|`e^xi / Σe^xj`|(0, 1), sums to 1|Multi-class output layer|Converts logits to probability distribution|
|**Linear**|`x`|(-∞, ∞)|Regression output layer|No non-linearity — only for final output in regression|

### Key Exam Points

- **Sigmoid / Tanh** → vanishing gradient risk; avoid in deep hidden layers
- **ReLU** → default choice for hidden layers; fast convergence
- **Dying ReLU** → neuron output stuck at 0 permanently; fix with Leaky ReLU or ELU
- **Softmax** → always used in multi-class classification output
- **Output layer rule:** Sigmoid (binary), Softmax (multi-class), Linear (regression)

---

## 2. Convolutional Neural Networks (CNN)

CNNs are designed for **grid-structured data** (images, time series with spatial locality). They exploit local patterns via weight sharing and spatial hierarchy.

### 2.1 Core Components

|Layer|What It Does|
|---|---|
|**Convolutional Layer**|Applies learned filters (kernels) that slide over the input — detects local features (edges, textures, shapes)|
|**Activation (ReLU)**|Applied after convolution to introduce non-linearity|
|**Pooling Layer**|Downsamples feature maps — reduces spatial dimensions and controls overfitting|
|**Fully Connected Layer**|Flattened feature maps are fed into a standard DNN for final classification/regression|
|**Flatten**|Converts 2D/3D feature maps to a 1D vector before FC layers|

### 2.2 Pooling Types

|Type|Behavior|
|---|---|
|**Max Pooling**|Takes the maximum value in each pooling window — preserves strongest feature activations|
|**Average Pooling**|Takes the mean — smoother, preserves overall feature presence|
|**Global Average Pooling**|Reduces each feature map to a single value — replaces FC layers in modern architectures|

### 2.3 Key Concepts

- **Filter / Kernel** — small learnable weight matrix (e.g., 3×3, 5×5) that detects a specific pattern
- **Stride** — how many pixels the filter moves at each step; larger stride = smaller output feature map
- **Padding** — adds zeros around the border; `same` padding preserves input dimensions, `valid` reduces them
- **Feature Map** — output of a convolutional layer; each filter produces one feature map
- **Depth / Channels** — stacking multiple filters produces a feature map with multiple channels
- **Receptive Field** — region of the input that influences a particular neuron; grows with depth

### 2.4 Exam-Relevant Architectures

|Architecture|Key Innovation|
|---|---|
|**LeNet**|First practical CNN; small scale|
|**AlexNet**|Deep CNN with ReLU and Dropout; won ImageNet 2012|
|**VGG**|Very deep with 3×3 convolutions only|
|**ResNet**|**Skip connections** (residual connections) — solves vanishing gradient in very deep networks|
|**Inception / GoogLeNet**|Parallel convolutions at different scales concatenated|
|**MobileNet**|Depthwise separable convolutions — lightweight, for edge/mobile devices|

### 2.5 When to Use CNN

- Image classification, object detection, semantic segmentation
- 1D CNNs: time series feature extraction, NLP (character-level models)

---

## 3. Recurrent Neural Networks (RNN)

RNNs are designed for **sequential data** where order and temporal dependencies matter. The output at each time step depends on both the current input and a **hidden state** carried from the previous step.

### 3.1 How It Works

```
h_t = tanh(W_h * h_{t-1} + W_x * x_t + b)
y_t = W_y * h_t
```

- `x_t` — input at time t
- `h_t` — hidden state at time t (memory of past)
- `y_t` — output at time t
- Weights `W_h`, `W_x`, `W_y` are **shared across all time steps** (parameter efficiency)

### 3.2 RNN Variants

|Variant|Description|
|---|---|
|**Vanilla RNN**|Basic recurrent unit; struggles with long sequences due to vanishing gradient|
|**Bidirectional RNN**|Two RNNs — one processes forward, one backward; captures both past and future context|
|**Deep / Stacked RNN**|Multiple RNN layers stacked; increases representational capacity|

### 3.3 RNN Limitations

- **Vanishing gradient** — gradients shrink exponentially as they propagate back through many time steps; early inputs have little influence
- **Exploding gradient** — gradients grow exponentially; fixed with **gradient clipping**
- **Short memory** — vanilla RNN struggles to retain information across long sequences (>10–20 steps)

### 3.4 Use Cases

- Language modeling, text generation, speech recognition, time series prediction, machine translation (early approaches)

---

## 4. Long Short-Term Memory (LSTM)

LSTM is a special RNN architecture designed to solve the **vanishing gradient / long-term dependency problem** through a gated memory cell.

### 4.1 LSTM Gates

|Gate|Role|Controls|
|---|---|---|
|**Forget Gate** (`f_t`)|Decides what to remove from cell state|How much of previous cell state `C_{t-1}` to retain|
|**Input Gate** (`i_t`)|Decides what new information to store|Which new values from `x_t` and `h_{t-1}` to add to cell state|
|**Cell State Update** (`C̃_t`)|Candidate values to add|New content proposed for the cell state|
|**Output Gate** (`o_t`)|Decides what part of cell state to expose as hidden state|What `h_t` reveals from `C_t`|

### 4.2 LSTM vs GRU

|Feature|LSTM|GRU|
|---|---|---|
|Gates|3 (forget, input, output)|2 (reset, update)|
|Cell state|Separate cell state + hidden state|Merged into single hidden state|
|Parameters|More|Fewer|
|Performance|Slightly better on complex tasks|Faster training; comparable on many tasks|
|When to use|Long, complex sequences|Shorter sequences; resource-constrained|

### 4.3 Key Properties

- Cell state (`C_t`) acts as a **long-term memory highway** — gradients flow through it with minimal decay
- Forget gate initialized with a **bias of 1** so the network starts by remembering everything
- Bidirectional LSTM → processes sequence in both directions; standard for NLP tasks

### 4.4 Use Cases

- Text classification, named entity recognition, sentiment analysis, time series forecasting, speech recognition, machine translation

---

## 5. Regularization Techniques

Regularization prevents **overfitting** — when the model performs well on training data but poorly on unseen data.

### 5.1 L1 and L2 Regularization

|Type|Penalty Added to Loss|Effect|Use When|
|---|---|---|---|
|**L1 (Lasso)**|`λ Σ|w|`|
|**L2 (Ridge / Weight Decay)**|`λ Σw²`|Shrinks weights toward zero but rarely to exactly zero → **dense small weights**|Default choice for neural networks|
|**Elastic Net**|Combination of L1 + L2|Balance between sparsity and shrinkage|When both effects are desired|

- `λ` (lambda) is the regularization strength hyperparameter
- Too high `λ` → underfitting; too low → overfitting

### 5.2 Dropout

- Randomly **sets a fraction `p` of neurons to zero** during each forward pass in training
- Forces the network to learn **redundant representations** — no single neuron can be relied upon
- At inference, all neurons are active but scaled by `(1 - p)` to maintain expected values
- Typical `p`: 0.2–0.5 for hidden layers; 0.1–0.2 closer to input
- **Spatial Dropout** — drops entire feature maps in CNNs (more effective than per-pixel)

### 5.3 Batch Normalization

- **Normalizes activations** within a mini-batch to zero mean and unit variance, then applies learnable scale (`γ`) and shift (`β`)
- Reduces **internal covariate shift** — stabilizes and accelerates training
- Acts as a mild regularizer (reduces need for Dropout)
- Applied **before** activation function (typically)
- **Layer Normalization** — normalizes across features rather than batch; used in Transformers/RNNs where batch size may be 1

### 5.4 Early Stopping

- Monitor **validation loss** during training; stop when it stops improving
- Saves the model at the **best validation checkpoint**
- Prevents wasted compute and overfitting to training data
- `patience` hyperparameter defines how many epochs to wait before stopping

### 5.5 Data Augmentation

- Artificially expands the training set by applying **label-preserving transformations**
- Images: random crop, flip, rotation, color jitter, cutout, mixup
- Text: synonym replacement, back-translation, random insertion/deletion
- Time series: time warping, jittering, window slicing

### 5.6 Other Techniques

|Technique|Mechanism|
|---|---|
|**Max-Norm Constraint**|Clips weight vector norm to a maximum value|
|**Label Smoothing**|Softens hard labels (e.g., 1.0 → 0.9) to prevent overconfident predictions|
|**Gradient Clipping**|Clips gradient norm to a threshold; prevents exploding gradients|
|**Weight Initialization**|Xavier/Glorot (tanh), He/Kaiming (ReLU) — prevents vanishing/exploding at init|

---

## 6. Vanishing Gradient Problem

### 6.1 What It Is

During **backpropagation**, gradients are multiplied through each layer via the chain rule. If the gradients are repeatedly multiplied by values < 1 (common with Sigmoid and Tanh), they shrink **exponentially** as they travel to earlier layers — those layers learn extremely slowly or not at all.

**Exploding gradient** is the reverse: gradients grow exponentially, causing unstable updates (NaN loss).

### 6.2 Causes

- **Sigmoid / Tanh activations** — derivatives max out at 0.25 (sigmoid) and 1.0 (tanh) and approach 0 at saturated extremes
- **Very deep networks** — more layers = more multiplications = more shrinkage
- **Poor weight initialization** — weights too small compound the problem

### 6.3 Solutions

|Problem|Solution|
|---|---|
|Vanishing gradient|Use **ReLU** or variants (Leaky ReLU, ELU)|
|Vanishing in deep networks|**ResNet skip connections** — gradient bypasses layers via identity path|
|Vanishing in RNNs|Use **LSTM / GRU** gating mechanisms|
|Both|**Batch Normalization** — keeps activations in a healthy range|
|Both|**Proper weight initialization** — He init for ReLU, Xavier for Tanh|
|Exploding gradient|**Gradient clipping** — clip gradient norm to a max value (e.g., 1.0)|
|Exploding in RNNs|Gradient clipping is standard practice|

---

## 7. Evaluation Metrics

### 7.1 Confusion Matrix

For binary classification (Positive = P, Negative = N):

```
                  Predicted Positive    Predicted Negative
Actual Positive       TP (True Pos)        FN (False Neg)   ← Type II Error
Actual Negative       FP (False Pos)       TN (True Neg)    ← Type I Error
```

|Metric|Formula|Meaning|
|---|---|---|
|**Accuracy**|`(TP + TN) / Total`|Overall correctness — misleading on imbalanced datasets|
|**Precision**|`TP / (TP + FP)`|Of all predicted positives, how many were correct? (Minimize false alarms)|
|**Recall (Sensitivity)**|`TP / (TP + FN)`|Of all actual positives, how many did we catch? (Minimize misses)|
|**Specificity**|`TN / (TN + FP)`|Of all actual negatives, how many did we correctly reject?|
|**F1 Score**|`2 × (P × R) / (P + R)`|Harmonic mean of Precision and Recall — balanced metric|
|**F-Beta**|`(1+β²) × (P × R) / (β²P + R)`|β > 1 weights Recall more; β < 1 weights Precision more|

### 7.2 Precision vs Recall Trade-off

- **High Precision, Low Recall** → conservative model; catches fewer positives but with high confidence
- **High Recall, Low Precision** → aggressive model; catches most positives but with many false alarms
- Adjust by **shifting the decision threshold** (default 0.5)

**When to prioritize:**

|Priority|Example|
|---|---|
|Precision|Spam detection (don't want legit email in spam)|
|Recall|Cancer screening (don't want to miss a true case)|
|F1|Balanced classification tasks|

### 7.3 AUC-ROC

- **ROC Curve** — plots True Positive Rate (Recall) vs False Positive Rate at every threshold
- **AUC** (Area Under the Curve) — single scalar summary of ROC; ranges 0 to 1
- AUC = 0.5 → random classifier; AUC = 1.0 → perfect classifier
- **AUC is threshold-independent** — useful when the operating threshold is not fixed
- Prefer AUC over accuracy for **imbalanced datasets**
- **PR-AUC** (Precision-Recall AUC) — better than ROC-AUC when the positive class is very rare

### 7.4 Regression Metrics

|Metric|Formula|Meaning|Notes|
|---|---|---|---|
|**MAE** (Mean Absolute Error)|`(1/n) Σ|y - ŷ|`|
|**MSE** (Mean Squared Error)|`(1/n) Σ(y - ŷ)²`|Penalizes large errors heavily; differentiable|Sensitive to outliers; used in loss functions|
|**RMSE** (Root MSE)|`√MSE`|Same unit as target; penalizes large errors|More interpretable than MSE; still outlier-sensitive|
|**R² (R-Squared)**|`1 - SS_res/SS_tot`|Proportion of variance explained by the model|1 = perfect; 0 = predicts mean; can be negative|
|**MAPE**|`(1/n) Σ|(y-ŷ)/y|`|

**When to use:**

- MAE → outliers present, want robust metric
- RMSE → large errors are disproportionately bad
- R² → want to communicate explained variance to stakeholders
- MAPE → comparing models across different scales

---

## 8. Ensemble Methods

Ensemble methods combine multiple models to produce a **stronger prediction** than any individual model.

### 8.1 Bagging (Bootstrap Aggregating)

- Train multiple models **independently** on different **bootstrap samples** (random subsets with replacement) of the training data
- Aggregate predictions: **majority vote** (classification) or **mean** (regression)
- Reduces **variance** without increasing bias
- **Example:** Random Forest — bagging of decision trees with random feature subsets at each split

### 8.2 Boosting

- Train models **sequentially** — each model focuses on the errors (residuals) of the previous
- Reduces both **bias and variance**
- Examples:

|Algorithm|Mechanism|
|---|---|
|**AdaBoost**|Reweights misclassified samples; later models focus more on hard examples|
|**Gradient Boosting**|Each tree fits the **residuals** of the previous ensemble (gradient descent in function space)|
|**XGBoost**|Regularized gradient boosting with second-order gradients; very fast|
|**LightGBM**|Leaf-wise tree growth; faster than XGBoost on large datasets|
|**CatBoost**|Native categorical feature handling; ordered boosting|

### 8.3 Stacking (Stacked Generalization)

- Train **Level 0 models** (diverse base learners) on training data
- Use their **out-of-fold predictions** as features for a **Level 1 meta-learner**
- Meta-learner learns how to best combine the base model predictions
- More complex than bagging/boosting but often highest performance

### 8.4 Voting & Averaging

|Method|Description|
|---|---|
|**Hard Voting**|Majority class label wins|
|**Soft Voting**|Average predicted probabilities; class with highest average probability wins|
|**Weighted Averaging**|Different models get different weights based on validation performance|

---

## 9. Automated Model Tuning (AMT) in SageMaker

### 9.1 Overview

SageMaker AMT (also called **Hyperparameter Tuning**) automatically searches the hyperparameter space to find the best configuration, without manual grid search.

### 9.2 Search Strategies

|Strategy|How It Works|Best For|
|---|---|---|
|**Random Search**|Randomly samples hyperparameter combinations|Fast, simple baseline; surprisingly effective|
|**Bayesian Optimization**|Builds a probabilistic surrogate model of the objective function; balances exploration and exploitation|Best performance; default recommendation|
|**Hyperband**|Runs many configurations briefly; early-terminates poor performers and allocates more compute to promising ones|Large search spaces; compute efficiency|
|**Grid Search**|Exhaustively tries every combination|Only feasible for very small search spaces|

### 9.3 Hyperparameter Types

|Type|Example|
|---|---|
|**Continuous**|Learning rate: [0.0001, 0.1]|
|**Integer**|Batch size: [16, 256]|
|**Categorical**|Optimizer: ["adam", "sgd", "rmsprop"]|

### 9.4 Key Configuration

- **Objective metric** — define the metric to maximize/minimize (e.g., `validation:rmse`, `validation:auc`)
- **Max training jobs** — total budget of training runs
- **Max parallel jobs** — how many to run simultaneously (too high reduces Bayesian efficiency)
- **Early stopping** — `Auto` mode stops jobs that are not improving relative to the best so far
- **Warm starting** — initialize a new tuning job with results from a previous job (`IDENTICAL_DATA_AND_ALGORITHM` or `TRANSFER_LEARNING`)

### 9.5 Best Practices

- Use logarithmic scale for learning rate (`log` scale in continuous range)
- Limit parallel jobs when using Bayesian (parallel jobs reduce its effectiveness — it needs sequential feedback)
- Use Hyperband for large budgets and many hyperparameters
- Start with wide ranges, then narrow with a warm-start job

---

## 10. SageMaker Autopilot / AutoML

### 10.1 What It Does

SageMaker Autopilot automates the **entire ML pipeline** — from raw tabular data to a deployable model — with full transparency.

### 10.2 Autopilot Pipeline Steps

```
Data Analysis → Feature Engineering → Algorithm Selection → Training + Tuning → Model Leaderboard
```

### 10.3 Key Features

|Feature|Detail|
|---|---|
|**Input**|CSV or Parquet in S3; specify target column|
|**Mode**|`Auto` (Autopilot decides), `Ensembling`, `HPO` (hyperparameter optimization)|
|**Explainability**|Generates **SageMaker Clarify** SHAP-based feature importance reports|
|**Notebooks**|Produces two editable notebooks: Data Exploration and Candidate Generation|
|**Leaderboard**|Ranks all tried models by objective metric|
|**Deployment**|Best model deployable directly to a real-time endpoint|

### 10.4 Supported Problem Types

- Binary classification, multi-class classification, regression
- **Time series forecasting** (newer addition)
- Text classification (using pre-trained Transformers)

---

## 11. SageMaker Studio & Experiments

### 11.1 SageMaker Studio

- Fully integrated, web-based **IDE for ML** — runs in a browser
- Provides a unified interface for: data prep, notebooks, training, tuning, deployment, monitoring
- Supports **JupyterLab**, Code Editor (VS Code-like), and JupyterHub
- **Domains** and **User Profiles** control access isolation
- **Studio Classic** vs **Studio** (newer unified experience)

### 11.2 SageMaker Experiments

- Tracks and organizes **training runs** as experiments → trials → trial components
- Automatically captures: hyperparameters, metrics, artifacts, code version
- Enables comparison of runs across different model configurations
- Integrates with SageMaker Autopilot and AMT automatically
- Use the **Experiments UI** in Studio or query via SDK (`smexperiments` library)

**Hierarchy:**

```
Experiment
  └── Trial (one training run or pipeline execution)
        └── Trial Component (individual processing/training/evaluation step)
```

---

## 12. SageMaker Debugger

### 12.1 What It Does

SageMaker Debugger captures **internal model state** (tensors, gradients, weights) during training without modifying training code, and automatically detects training issues.

### 12.2 Components

|Component|Role|
|---|---|
|**Hook**|Intercepts and saves tensor data to S3 at specified intervals|
|**Rules**|Analyses saved tensors in real time; triggers alerts or stops training on issues|
|**ProfilerRule**|Monitors system resource utilization (CPU, GPU, memory, I/O)|
|**Report**|Auto-generates a profiling report after training|

### 12.3 Built-In Rules (Exam Relevant)

|Rule|Detects|
|---|---|
|`VanishingGradient`|Gradients approaching zero in early layers|
|`ExplodingTensor`|Tensor values becoming NaN or Inf|
|`OvertrainedModel`|Training accuracy keeps improving while validation plateaus|
|`OverfittingDetection`|Growing gap between train and validation loss|
|`PoorWeightInitialization`|Weights/activations concentrated near zero|
|`LossNotDecreasing`|Loss stagnant over several steps|
|`LowGPUUtilization`|GPU underutilized — possible data loading bottleneck|
|`StepOutlier`|Individual training steps taking unusually long|

### 12.4 Debugger Actions

- `StopTraining` — automatically terminates a job when a rule fires (saves compute cost)
- Emit CloudWatch events for custom alerting

---

## 13. SageMaker Model Registry

### 13.1 Purpose

Central catalog for **versioning, tracking, and approving ML models** before deployment. Core MLOps governance component.

### 13.2 Concepts

|Concept|Description|
|---|---|
|**Model Group**|Logical collection of model versions for the same use case|
|**Model Version**|A specific trained model artifact registered in a group|
|**Approval Status**|`Approved`, `Rejected`, `PendingManualApproval`|

### 13.3 Workflow

```
Training Job completes
        ↓
Register model version in Model Group (with metrics, artifacts, lineage)
        ↓
Manual or automated approval (EventBridge triggers CodePipeline on approval)
        ↓
Approved model deployed to endpoint via CDK / CFT / SageMaker Pipeline
```

### 13.4 Key Features

- Stores model metadata: training metrics, hyperparameters, data version, framework
- **Model lineage tracking** — traces back to the dataset and code used
- Integrates with **SageMaker Pipelines** for end-to-end CI/CD
- IAM policies control who can approve/reject versions

---

## 14. Analyzing Training Jobs with TensorBoard

### 14.1 Overview

TensorBoard is a visualization toolkit (from TensorFlow, but works with PyTorch too) for analyzing training dynamics.

### 14.2 What It Visualizes

|Panel|Content|
|---|---|
|**Scalars**|Loss and metric curves across steps/epochs (train vs validation)|
|**Histograms**|Weight and bias distribution evolution across training|
|**Graphs**|Computational graph of the model|
|**Images**|Sample predictions, attention maps, augmented inputs|
|**Embeddings** (Projector)|t-SNE or PCA visualization of learned embeddings|
|**Profiler**|Step-by-step timeline of operations (CPU/GPU)|
|**HParams**|Hyperparameter comparison across runs|

### 14.3 SageMaker + TensorBoard

- SageMaker Debugger can output TensorBoard-compatible event files to S3
- SageMaker Studio supports TensorBoard natively — launch from the Studio UI
- Use `smdebug` hook to capture tensors and write TensorBoard summaries simultaneously

---

## 15. SageMaker Training at Large Scale

### 15.1 SageMaker Training Compiler

- Converts your DL model's training computation into **optimized machine code** for the specific GPU
- Works with TensorFlow and PyTorch via Hugging Face Transformers
- Can reduce training time by **up to 50%** with no code changes beyond enabling the compiler
- Enabled via `TrainingCompilerConfig(enabled=True)` in the Estimator
- **Not compatible** with SageMaker Distributed Training libraries — choose one or the other

### 15.2 Managed Warm Pools

- After a training job completes, the **compute instances remain warm** for a configurable period
- Next training job that matches the same instance configuration **reuses the warm pool** — skips instance provisioning (~2–3 min startup savings)
- Useful for **iterative development** and hyperparameter tuning where many short jobs run sequentially
- Billed for the warm pool idle time — set `KeepAlivePeriodInSeconds` appropriately
- Configure with `ResourceConfig.KeepAlivePeriodInSeconds`

### 15.3 SageMaker Checkpointing

- Periodically saves model weights and optimizer state to **S3 during training**
- Allows **resuming** a training job from the last checkpoint after interruption (spot instance termination)
- Configure `checkpoint_s3_uri` and `checkpoint_local_path` in the Estimator
- Framework-specific: PyTorch uses `torch.save()`, TF uses `tf.train.Checkpoint`
- Critical for **Managed Spot Training** to avoid losing progress on interruption

---

## 16. SageMaker Distributed Training

### 16.1 Why Distributed Training

Single GPU / instance becomes a bottleneck when:

- Model is too large to fit in a single GPU's memory (**Model Parallelism**)
- Dataset is too large and training is too slow (**Data Parallelism**)

### 16.2 Data Parallelism

- **Replicate the full model** on each GPU/worker
- Each worker processes a **different mini-batch** (shard of training data)
- Gradients are **aggregated across all workers** after each forward/backward pass
- Effective batch size = `per-GPU batch size × number of GPUs`

**SageMaker Distributed Data Parallelism (SMDDP):**

- AWS-optimized AllReduce implementation using **EFA** (Elastic Fabric Adapter)
- Outperforms Horovod on large clusters
- Enable via `distribution={"smdistributed": {"dataparallel": {"enabled": True}}}`
- Supports PyTorch (DDP) and TensorFlow (MirroredStrategy)

**AllReduce Algorithms:**

|Algorithm|Description|
|---|---|
|**Ring AllReduce**|Gradients passed in a ring; each node sends to next and receives from previous; bandwidth-efficient|
|**Tree AllReduce**|Hierarchical gradient aggregation; lower latency for small clusters|
|**Recursive Halving Doubling**|Used in SMDDP; efficient for large message sizes|

### 16.3 Model Parallelism

- **Partition the model** itself across multiple GPUs — different layers on different devices
- Used when the model is too large to fit in a single GPU (e.g., LLMs, very deep networks)

**SageMaker Model Parallelism Library (SMP):**

- Automatically or manually partitions model layers across GPUs
- Implements **pipeline parallelism** — divides each mini-batch into **micro-batches** that flow through the pipeline of devices
- Implements **tensor parallelism** — splits individual layers (e.g., attention heads) across GPUs
- **Activation checkpointing** — recomputes activations during backward pass instead of storing them, reducing GPU memory at the cost of extra compute
- Enable via `distribution={"smdistributed": {"modelparallel": {"enabled": True, "parameters": {...}}}}`

**Pipeline Parallelism:**

```
GPU 0: Layers 0-3    → micro-batch 1 → micro-batch 2 → ...
GPU 1: Layers 4-7              → micro-batch 1 → micro-batch 2 → ...
GPU 2: Layers 8-11                       → micro-batch 1 → ...
```

- Interleaving micro-batches keeps GPUs busy and reduces pipeline bubbles

### 16.4 Hybrid Parallelism (3D Parallelism)

- Combine data, tensor, and pipeline parallelism simultaneously
- Required for training largest models (100B+ parameters)

---

## 17. Elastic Fabric Adapter (EFA) & MiCS

### 17.1 Elastic Fabric Adapter (EFA)

|Property|Detail|
|---|---|
|**What it is**|A network interface for EC2 instances that provides **OS-bypass networking** — data moves directly between application and network hardware without the OS kernel|
|**Benefit**|Dramatically lower latency and higher throughput for inter-node communication during distributed training|
|**Bandwidth**|Up to **400 Gbps** on `p4d.24xlarge` instances|
|**Protocols**|**RDMA** (Remote Direct Memory Access) — writes directly to remote GPU memory|
|**Use with**|SMDDP, NCCL, Horovod — any collective communication library|
|**Requirement**|Must use EFA-compatible instances (`p3dn`, `p4d`, `p4de`, `p5`, `trn1`) in a **cluster placement group**|
|**Not EFA** → Bottleneck|Standard ENA (Ethernet Network Adapter) becomes the bottleneck at scale; gradient communication is slower than GPU compute|

### 17.2 MiCS (Minimizing Communication Scale)

|Property|Detail|
|---|---|
|**What it is**|AWS-developed technique (part of SMP) that **minimizes the communication overhead** during large-scale model parallelism|
|**Problem it solves**|In naive model parallelism, activations and gradients are frequently transmitted between GPUs — this inter-GPU communication becomes the bottleneck at scale|
|**Mechanism**|Partitions the model such that communication only occurs between **nearest neighbor** GPUs; exploits NVLink (within a node) before EFA (between nodes) — keeping fast communication local|
|**Benefit**|Near-linear scaling of model training across hundreds of GPUs; reduces idle GPU time waiting for communication|
|**Works with**|SageMaker Model Parallelism Library + EFA|
|**Use case**|Training LLMs (10B–100B+ parameters) on SageMaker|

### 17.3 Communication Hierarchy (Exam Relevant)

```
Within a GPU:          Tensor cores (fastest)
Between GPUs (same node): NVLink (~600 GB/s)
Between nodes:         EFA with RDMA (~400 Gbps) — replaces standard Ethernet
Standard Ethernet:     ENA (~25 Gbps) — bottleneck at scale; avoid for distributed DL
```

---

## 18. Quick Reference Summary

### Model Architecture Selection

|Data Type|Architecture|
|---|---|
|Images|CNN (ResNet, EfficientNet, MobileNet)|
|Sequences (text, time series)|RNN → LSTM/GRU → Transformer|
|Tabular|XGBoost, LightGBM, Linear Learner|
|Both image + text|Multi-modal (CNN + Transformer)|

### Fixing Common Training Problems

|Problem|Fix|
|---|---|
|Overfitting|Dropout, L1/L2, early stopping, data augmentation, more data|
|Underfitting|Larger model, more epochs, reduce regularization, better features|
|Vanishing gradient|ReLU, LSTM, skip connections (ResNet), batch norm, He init|
|Exploding gradient|Gradient clipping, weight init, lower learning rate|
|Slow convergence|Adaptive optimizer (Adam), LR scheduling, batch norm|
|GPU OOM (out of memory)|Smaller batch, model parallelism, mixed precision (FP16), activation checkpointing|
|High loss variance|Reduce LR, increase batch size, gradient clipping|

### SageMaker Training Scale Toolkit

|Scale|Tool|
|---|---|
|Single GPU, faster code|SageMaker Training Compiler|
|Multi-GPU, one machine|SMDDP (intra-node via NVLink)|
|Multi-node, data parallel|SMDDP + EFA|
|Model too large for one GPU|SMP (Model Parallelism) + MiCS + EFA|
|Iterative development|Managed Warm Pools|
|Spot instance training|Managed Spot + Checkpointing|
|Hyperparameter search|AMT (Bayesian Optimization + Hyperband)|

### Validation Types

| Scenario / Signal in Question                                                                                                   | Strategy                                                                                            | Why                                                                                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Balanced classes, reasonably large dataset**                                                                                  | Simple **k-fold cross-validation** (k=5 or k=10)                                                    | No imbalance to worry about; k-fold gives a stable performance estimate by rotating validation folds                                                            |
| **Imbalanced classes** (rare disease, fraud, churn, etc.)                                                                       | **Stratified k-fold cross-validation**                                                              | Ensures each fold preserves the original class ratio — prevents folds with 0 or very few minority-class samples                                                 |
| **Small dataset + imbalanced classes**                                                                                          | **Stratified k-fold** (not a single split)                                                          | Cross-validation reuses all data across folds → more reliable estimate when minority class samples are scarce                                                   |
| **Very small dataset** (e.g., <100 samples)                                                                                     | **Leave-One-Out Cross-Validation (LOOCV)**                                                          | Maximizes training data per fold (train on n-1, test on 1); computationally expensive but justified when data is extremely limited                              |
| **Time-series / sequential data** (stock prices, sensor streams, forecasting)                                                   | **Time-series split / rolling-window / forward-chaining CV** (NOT k-fold)                           | Prevents **data leakage** — you must never train on future data to predict the past. Each fold's validation set comes _after_ its training set chronologically  |
| **Large dataset, class balance not a concern, compute cost matters**                                                            | **Simple train/validation/test split** (e.g., 70/15/15 or 80/20)                                    | With enough data, a single split is statistically reliable and far cheaper than k-fold; k-fold's main benefit (data reuse) matters less when data is abundant   |
| **Grouped/clustered data** (e.g., multiple records per patient/customer, must avoid same entity appearing in both train & test) | **Group k-fold**                                                                                    | Prevents leakage — same patient/customer's data shouldn't span both train and validation sets                                                                   |
| **Need robust performance estimate + want to reduce variance from a single k-fold run**                                         | **Repeated k-fold cross-validation** (e.g., k=5, repeated 3×)                                       | Reduces variance in performance estimate by averaging over multiple randomized fold splits — used when a single k-fold run is noisy, NOT as a fix for imbalance |
| **Hyperparameter tuning required alongside evaluation**                                                                         | **Nested cross-validation** (outer loop = performance estimate, inner loop = hyperparameter tuning) | Prevents overfitting to the validation set during tuning; gives an unbiased final performance estimate                                                          |
| **Multi-class imbalance** (not just binary)                                                                                     | **Stratified k-fold** (stratification generalizes to multi-class)                                   | Same logic — preserves the proportion of _each_ class across folds                                                                                              |
| **Regression problems (continuous target)**                                                                                     | **Plain k-fold** (stratification typically N/A, unless target is binned)                            | Stratified k-fold isn't standard for continuous targets unless you bucket the target into quantile bins first ("stratified regression")                         |