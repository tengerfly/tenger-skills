# 同类「动作生成型」原型 Skill 结构样本（Agent Skill Samples）

> 用途：优化本 Skill 结构时的借鉴范本。原型设计类已有一批「直接生成 HTML 原型」的生产级范本，重点照抄其工作流/生命周期/反馈闭环（只借鉴，不搬运）。

---

## 一、kurenn/claude-prototype（生命周期黄金范式）

- 四阶段：Discover（Q&A→PRODUCT.md/DESIGN.md）→ Build → Assess（audit/critique/detect）→ Ship。
- **生命周期状态**：persona 切换换数据不换外壳（new/active/power、empty/busy）。
- **URL 状态分享**：theme+layout+persona+modal 写进 URL，精确复现画面。
- **apply-feedback 反馈闭环**：评审点元素 pin 评论 → 导出 JSON → 一条命令原位应用 → 归档 + 重新评估。
- 反 AI-slop：禁紫色渐变/lorem ipsum，单一强调色。

## 二、qubernetic/wireframe-agent-skill（设计语言规范）

- DESIGN-LANGUAGE.md（21 节）穷尽设计规范 + 11 可复用组件模板（Navbar/Footer/PlaceholderBox/ProductCard/StatCard/FormField/Button…）。

## 三、verachen1988/claude-wireframe-skill（UX 方法决策树）

- 9 种 UX 方法（Progressive Disclosure/Dashboard-First/Wizard/Hub-and-Spoke/Card-Based/Kanban…）+ 并行变体生成。

## 四、jiji262/claude-design-skill（产物骨架）

- output-formats（deck/canvas/prototype/animation/wireframe 骨架）+ device-frames CSS + 设计哲学库。

## 五、cirton86/huashu-design（中文友好）

- 高保真原型/幻灯片/动画；20 设计哲学 + 5 维评审。

> 出处：github.com/kurenn/claude-prototype、github.com/qubernetic/wireframe-agent-skill、github.com/verachen1988/claude-wireframe-skill。
