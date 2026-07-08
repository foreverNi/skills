---
name: mental-models-framework
description: Multidisciplinary mental models lattice for structured analysis, decision-making, strategy, risk review, root-cause thinking, trend judgment, product or technical choices, and self-critique. Use when Codex is asked to analyze a complex question with mental models, first principles, systems thinking, decision theory, incentives, uncertainty, second-order effects, or phrases such as 思维模型, 格栅框架, 第一性原理, 逆向思维, 二阶思维, 贝叶斯, 黑天鹅, 反脆弱, or 我可能错在哪.
---

# Mental Models Framework

## Core Rule

Use multiple lenses to reduce single-model bias. Do not mechanically apply all models. Classify the problem, select the 3-5 most relevant models, integrate the key insights, and include explicit self-critique.

For the full 38-model lattice and recommended model combinations, read `references/mental-models-framework.md` when the task requires detailed model selection or the user explicitly asks for the full framework.

## Workflow

1. **Classify the problem**
   - Identify whether the request is about truth, causality, system evolution, decision choice, action strategy, risk, uncertainty, trend prediction, or self-correction.
   - State the classification in one sentence.

2. **Select models**
   - Choose only the most relevant 3-5 models unless the user asks for a full lattice scan.
   - Prefer cross-domain coverage: epistemology, systems, decision theory, incentives, strategy, uncertainty, and cognitive limits.
   - If the problem is high-stakes or uncertain, include at least one model for downside risk or self-critique.

3. **Analyze concretely**
   - For each selected model, explain the insight and what it means for the current problem.
   - Avoid generic model definitions unless the user asks for education.
   - Distinguish facts, assumptions, inferences, and unknowns.

4. **Integrate findings**
   - Extract 3-5 key insights by impact:
     - biggest blind spot
     - highest leverage point
     - most overlooked risk
     - deepest structural cause
     - most counterintuitive finding

5. **Recommend action**
   - Give the highest-leverage action.
   - Use inversion to identify what would make the plan fail.
   - Include second-order effects and opportunity costs where relevant.

6. **Self-critique**
   - End with "我可能错在哪" or an equivalent section.
   - Name the assumptions that could be false, evidence that would change the conclusion, and where more data is needed.

## Output Template

Use this structure by default for substantive analysis:

```markdown
## 问题定性
[一句话描述问题类型]

## 核心分析

### 模型1：[名称]
- **洞察**：[这个模型揭示了什么]
- **含义**：[对当前问题的具体影响]

### 模型2：[名称]
- **洞察**：[...]
- **含义**：[...] 

## 被忽略的风险
- [认知偏差、不确定性、极端事件或二阶效应]

## 行动建议
- **最高杠杆**：[最有效的干预点]
- **避免失败**：[逆向思维得到的失败条件]
- **二阶效应**：[行动后的后续影响]

## 我可能错在哪
- [关键假设、可证伪点、需要补充的信息]
```

## Guardrails

- Do not force every answer into all 12 domains or all 38 models.
- Do not use mental models as decoration. Each selected model must change the analysis.
- Do not hide uncertainty. If evidence is weak, say so.
- Do not present analogies as proof. Use first principles or evidence when the claim requires rigor.
- For user-facing advice in legal, medical, financial, or safety-sensitive domains, keep recommendations bounded and identify where expert verification is needed.
