# 🤖 SoccerLab 架构设计文档 (基于 IsaacLab)

## 1. 核心思想与目标 🎯

### 1.1. 核心控制范式：基于状态机的技能切换
**SoccerLab** 的核心控制逻辑基于**有限状态机 (FSM)**。这使得单个机器人能够在高层策略（如射门、追球、防御）之间进行可靠且模块化的切换。

* **技能 (Skill) 模块化：** 每个单一技能（如 `locomotion`、`chasing`）都被视为 FSM 中的一个状态，可以独立开发和训练。
* **切换逻辑：** FSM 负责根据环境观测（球的位置、对手位置、自身状态）来决定下一个要执行的技能状态。

### 1.2. 环境支持：多智能体与单一技能训练
项目支持两种主要环境类型，均作为独立的 IsaacLab 任务 (Task) 实现：

* **训练模式 (Train Tasks):** 专注于单个机器人习得特定、原子化的技能（如跑动、射门）。
* **竞技模式 (Battle Tasks):** 支持多智能体环境，用于训练团队协作和对抗策略。

## 2. SoccerLab 架构概览 🏗️

SoccerLab 的架构严格遵循 IsaacLab 的 **Task/Env/Simulation** 层次结构，并在 **Source** 目录下通过自定义库和配置进行扩展。

| 模块 | 目的 | IsaacLab 对应组件 | 路径/实现 |
| :--- | :--- | :--- | :--- |
| **控制核心** | 实现 FSM 逻辑，管理技能切换。 | Task/Controller | `soccerLab/source/fsmLab` |
| **机器人库** | 定义机器人物理、关节、传感器配置。 | Assets/Configuration | `soccerLab/source/robotlib` |
| **训练任务** | 实现原子技能的 RL 任务（观测、动作、奖励）。 | Task/TaskBase | `soccerLab/source/soccerTask/soccerTask/train/` |
| **竞技任务** | 实现多智能体、团队对抗的 RL 任务。 | Task/TaskBase | `soccerLab/source/soccerTask/soccerTask/battle/` |
| **资产管理** | 存储机器人和场景的 USD 模型及物理参数。 | Data/Assets | `soccerLab/data/assets/assetslib` |
| **策略/策略** | 存储训练好的策略文件（Checkpoints）。 | Data/Checkpoints | `soccerLab/data/ckpts` |

---

## 3. 核心组件详解 ⚙️

### 3.1. 控制核心：并行状态机 (`fsmLab`)

**路径:** `soccerLab/source/fsmLab`

该模块是整个控制系统的核心，负责将高维动作（技能选择）转化为低维控制输入。

* **FSM 实现：** 采用并行状态机（Parallel FSMs）或层级状态机（Hierarchical FSMs），允许同时处理运动（Locomotion）、目标跟踪（Targeting）和自稳（Balance）等子任务。
* **状态/技能定义：**
    * 每个单一技能任务 (Train Task) 对应 FSM 中的一个**叶子状态 (Leaf State)**。
    * 状态机的输入是 IsaacLab 的 **Observation** 集合。
    * 状态机的输出是机器人的 **Action** 集合（关节目标位置/力矩）。
* **切换逻辑 (`Transition`):** 定义在 FSM 中，根据观测（例如，球是否进入射程、自身是否跌倒）触发状态切换。

### 3.2. 机器人与资产管理

#### 3.2.1. 机器人参数定义 (`robotlib`)
**路径:** `soccerLab/source/robotlib`

这个模块包含了所有自定义机器人的配置类，这些类继承自 IsaacLab 的配置基类。

* **`RobotCfg` (配置):** 定义关节参数、物理属性、控制器配置（例如，PD 控制器增益 $K_p, K_d$）。
* **`ObservationCfg`:** 定义机器人专有的观测空间，例如 IMU 读数、关节编码器、历史动作等。
* **`ActionCfg`:** 定义机器人的动作空间类型（例如，关节位置、关节力矩或速度）。

#### 3.2.2. 机器人资产 (`assetslib`)
**路径:** `soccerLab/data/assets/assetslib`

包含机器人的 3D 模型和物理描述。

* **USD 文件：** 机器人及其环境元素（如足球、球场边界）的 Universal Scene Description 文件。
* **碰撞体/刚体定义：** 在 USD 中定义精确的碰撞体和惯性属性，确保仿真物理的准确性。

### 3.3. 任务实现：Train 与 Battle

所有任务都继承自 IsaacLab 的 `TaskBase` 类，并实现核心的 RL 循环方法。

#### 3.3.1. 单一技能训练 (`train` 任务)
**路径:** `soccerLab/source/soccerTask/soccerTask/train/`

这些任务旨在训练 FSM 中的原子化技能，可以作为 PPO 等 RL 算法的独立训练环境。

* **基础 Locomotion (`locomotion`):**
    * **目标:** 学习稳定、高效的步态（例如，随机目标速度跟踪）。
    * **奖励:** 最小化本体速度误差，惩罚关节力矩和摇晃。
* **跟球/追球 (`balls`):**
    * **目标:** 快速、准确地将机器人本体移动到球的位置。
    * **奖励:** 基于机器人末端或中心与球中心距离的负值。
* **射门 (`shooting`):**
    * **目标:** 学习用特定的肢体部位接触球，使球进入球门。
    * **奖励:** 对球的最终速度和方向给予奖励，特别是进球奖励。

#### 3.3.2. 多智能体竞技 (`battle` 任务)
**路径:** `soccerLab/source/soccerTask/soccerTask/battle/`

* **目标:** 实现一个完整的足球比赛场景，用于训练协调策略。
* **多智能体支持:** 利用 IsaacLab 的多智能体 API，将每台机器人的观测和动作空间独立或共享处理。
* **奖励:** 团队得分、控球时间、阻止对手得分等。

---

## 4. 开发流程与部署 🚀

1.  **资产准备:** 在 `assetslib` 中定义机器人的 USD 模型和物理参数。
2.  **配置定义:** 在 `robotlib` 中定义机器人的控制、观测和动作配置。
3.  **任务实现 (Train/Battle):**
    * 继承 `TaskBase`，实现 **`_setup_scene()`**、**`_get_observations()`**、**`_compute_reward()`** 和 **`_is_truncated()`**。
    * 为每个任务创建相应的配置类 (`<Task>Cfg`)。
4.  **FSM 集成:** 在 `fsmLab` 中定义高层策略的 FSM 结构，将训练好的策略 (Checkpoints in `data/ckpts`) 封装为 FSM 的状态。
5.  **运行与测试:** 使用 IsaacLab 的命令行工具加载特定的任务或 FSM 驱动的策略进行训练或测试。

---

## 5. 待办事项与未来方向 💡

* **运动学/动力学库：** 集成自定义的 IK/FK 库以支持更高级的控制。
* **感知模块：** 为多智能体任务添加视觉/激光雷达等感知输入和处理。
* **策略部署:** 优化从 RL 策略到 FSM 状态的集成和切换平滑性。
