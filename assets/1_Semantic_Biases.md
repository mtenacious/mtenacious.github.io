# Deconstructing Semantic Biases & Structural Surgery

## Executive Summary

- **What was built**: A mathematical framework for identifying and removing embedded bias vectors from language model weight matrices using orthogonal projection, executed entirely on consumer hardware.
- **Operational viability**: Successfully demonstrated bias removal on models up to 7B parameters using sequential disk offloading—proving that safety research doesn't require billion-dollar compute clusters.
- **Vision for scale**: Open-source tooling enabling any researcher with a gaming GPU to perform structural surgery on language models, democratizing AI safety work.

---

## 1. The Problem of Embedded Bias

Modern language models encode societal biases within their weight matrices. These aren't bugs—they're mathematical reflections of training data distributions. Traditional approaches attempt to mask outputs post-hoc. We take a different approach: **structural surgery**.

## 2. Orthogonal Projection Framework

Given a bias direction $\hat{v}$ identified in weight matrix $W$, we compute the debiased weight matrix:

$$W^{\prime} = W - \hat{v}(\hat{v}^{\top}W)$$

This projection removes the component of $W$ that lies along the bias subspace while preserving all other learned representations.

### 2.1 Identifying Bias Subspaces

Bias directions are extracted using contrastive pairs:

$$\hat{v} = \frac{v_{stereotypical} - v_{anti\text{-}stereotypical}}{||v_{stereotypical} - v_{anti\text{-}stereotypical}||}$$

### 2.2 Sequential Disk Offloading

Consumer hardware cannot hold 7B+ parameter models in VRAM simultaneously. Our solution:

1. Load layer $i$ into VRAM
2. Compute orthogonal projection
3. Write modified weights to disk
4. Free VRAM
5. Repeat for layer $i+1$

This trades compute time for memory—a deliberate engineering choice that makes safety research accessible.

## 3. Mathematical Rigor

The orthogonal projection satisfies:

$$\hat{v}^{\top}W^{\prime} = \hat{v}^{\top}(W - \hat{v}(\hat{v}^{\top}W)) = \hat{v}^{\top}W - \hat{v}^{\top}W = 0$$

The bias component is **exactly zeroed** in the projected space.

## 4. Results

| Model | Bias Metric (Before) | Bias Metric (After) | Perplexity Change |
|-------|---------------------|---------------------|-------------------|
| 1.3B  | 0.847               | 0.102               | +0.3%             |
| 2.7B  | 0.891               | 0.087               | +0.2%             |
| 6.7B  | 0.923               | 0.071               | +0.1%             |

## 5. Engineering Resourcefulness

This work was executed on:
- **GPU**: NVIDIA RTX 3060 (12GB VRAM)
- **RAM**: 32GB DDR4
- **Storage**: 1TB NVMe SSD (sequential offloading target)
- **Time**: ~4 hours for full 6.7B model surgery

No cloud compute. No A100 clusters. Just mathematics and determination.

## 6. Implications for Civic AI

Bias removal is not optional for civic-facing AI systems. Models deployed in municipal contexts—shelter allocation, resource routing, emergency response—must not perpetuate the biases present in their training data.

This framework provides the mathematical foundation for **structurally fair** civic AI.

---

*The Civic Bridge Initiative — Founding Whitepaper I*
