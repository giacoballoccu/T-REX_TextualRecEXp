# T-REX_TextualRecEXp
This is the repository for the paper "Knowledge is Power, Understanding is Impact: Utility and Beyond Goals, Explanation Quality, and Fairness in Path Reasoning Recommendation".

# Overview
The base workflow is:
1. Dataset creation
2. Dataset **preprocessing** and **formatting** with respect to the selected model
3. Training(or hyperparameter search) of the **TransE embedding model**
4. Training(or hyperparameter search) of the **Recommender model**
5. Test of the quality of the recommender model
6. Evaluation of the metrics

## Dependencies and Installation
Required **pytorch** and **tensorflow**, both with gpu version.
Clone the repo, enter into it.
All other dependencies can then be installed by means of the env_setup.sh script located at the top level of the project
```bash
bash env_setup.sh
```
The above environment setup includes download of the datasets and their preliminary setup.

Alternatively, the data can be downloaded from the following drive:
```bash
https://drive.google.com/file/d/1VUVkU1RLaJWUVqReox6cT6N9dcQ6nTd7/view?usp=sharing
```
The setup also downloads automatically the pretrained weights for the embeddings.

# Usage
To **facilitate the use of the codebase**, a set of scripts are provided to seamlessly execute all stages of the machine learning pipeline described above.
The top level of the project contains all such scripts.

### 1. Bulk dataset creation
```bash
./build_datasets.sh
```
### 2. Bulk dataset preprocessing
```python
python3 prepare_datasets.py
```
### 3. Models
Available DATASET_NAME values **{lfm1m, ml1m}**
Available MODEL_NAME values:
- path based methods **{cafe, pgpr, ucpr}**
- knowledge aware methods **{kgat, cfkg, cke}**
- embedding methods **{transe}**

The following variables can be used. Alternatively the provided dataset and model names can be manually written as command line arguments to the scripts that follow (thus substituting the $x expression with the actual name)
```bash
export DATASET_NAME=...
export MODEL_NAME=...
```
#### 3.1 Training

```python
python3 train.py --model $MODEL_NAME --dataset $DATASET_NAME
```
#### 3.2 Hyper parameter tuning

```python
python3 gridsearch.py --model $MODEL_NAME --dataset $DATASET_NAME
```

#### 4. Test
Note, the test phase does not support testing of the embedding models, although their metrics are gathered during training.
The main purpose of the test phase is to evaluate the metrics on each embedding model.
```python
python3 test.py --model $MODEL_NAME --dataset $DATASET_NAME
```


#### 5. Evaluation
As last step, with the computed top-k or the paths predicted by the models, evaluation can be run to obtain the evaluation metrics.

Note that this step requires training of the models and at least a testing phase for path reasoning models.

This is because the path-based ones require pre-computation of paths before the topK items can be obtained. 

After paths are computed, creation of the topK is computationally inexpensive.

Knowledge aware models generate the topK by default after each epoch of training.

```python
python3 evaluate.py --model $MODEL_NAME --dataset $DATASET_NAME
```

Flags such as `evaluate_overall_fidelity` and `evaluate_path_quality` decide whether or not evaluate the path quality prospectives, this prospectives can be computed only for methods capable of producing reasoning paths. By default the recommendation quality metrics are evaluated. In the following section we collect the metrics currently adopted by our evaluate.py

#### 6. Metrics 
This list collects the formulas and short descriptions of the metrics currently implemented by our evaluation module. All recommendation metrics are calculated for a user top-k and the results reported on the paper are obtained as the average value across all the user base.

##### 6.1 Recommendation Quality
- **NDCG:** The extent to which the recommended products are useful for the user. Weights the position of the item in the top-k.
$$NDCG@k=\frac{DCG@k}{IDCG@k}$$ where:
$$DCG@k=\sum_{i=1}^{k}\frac{rel_i}{log_2(i+1)}=rel_1+\sum_{i=2}^{k}\frac{rel_i}{log_2(i+1)}$$
$$IDCG@k = \text{sort descending}(rel)$$
- **MMR:** The extent to which the first recommended product is useful for the user.
$$MMR = \frac{1}{\text{first hit position}}$$
- **Coverage:** Proportion of items recommended among all the item catalog.
$$\frac{| \text{Unique Recommended items}|}{| \text{Items in Catalog} |}$$
- **Diversity:** Proportion of genres covered by the recommended items among the recommended items. 
$$\frac{| \text{Unique Genres} |}{| \text{Recommended items} |}$$
- **Novelty:** Inverse of popularity of the items recommended to the user
$$\frac{\sum_{i \in I}| 1 - \text{Pop}(i) |}{| \text{Recommended items} |}$$
- **Serendipity:** Proportion of items which may be surprising for the user, calculated as the the proportion of items recommended by the benchmarked models that are not recommended by a prevedible baseline. In our case the baseline was MostPop.
$$\frac{| \text{Recommended items} \cup \text{Recommended items by most pop} |}{| \text{Recommended items} |}$$
##### 6.1 Explanation (Path) Quality
For the explanation quality metrics we suggest to refer to the original papers which provide detailed formalizations of the prospectives.
- **LIR, SEP, ETD:** [Post Processing Recommender Systems with Knowledge Graphs for Recency, Popularity, and Diversity of Explanations](https://dl.acm.org/doi/10.1145/3477495.3532041)
- **LID, SED, PTC:** [Reinforcement Recommendation Reasoning through Knowledge Graphs for Explanation Path Quality
](https://arxiv.org/abs/2209.04954)
- **PPC** (named by us, refered in the paper as path diversity): [Fairness-Aware Explainable Recommendation over Knowledge Graphs](https://dl.acm.org/doi/10.1145/3397271.3401051)
- **Fidelity:** [Explanation Mining: Post Hoc Interpretability of Latent Factor Models for Recommendation Systems](https://dl.acm.org/doi/10.1145/3219819.3220072)

#### 7. Hyper parameters
# lfm1m
## Ucpr
## pgpr
## cafe

# ml1m
## kgat 
## cke
## cfkg


