import re
import os

def generate_study_plan(jd_path, plan_path):
    # Read the job description
    try:
        with open(jd_path, 'r', encoding='utf-8') as f:
            jd_content = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find {jd_path}")
        return

    # Extract keywords (simple matching for this example)
    keywords_to_check = ['API', 'Python', 'MLOps', 'Machine Learning', 'Data', 'SQL', 'Docker', 'Kubernetes', 'Cloud', 'AWS', 'GCP', 'Azure']
    found_keywords = [kw for kw in keywords_to_check if re.search(r'\b' + re.escape(kw) + r'\b', jd_content, re.IGNORECASE)]
    
    if not found_keywords:
        found_keywords = ['API', 'Python', 'MLOps'] # Default fallback
        
    print(f"Keywords found: {', '.join(found_keywords)}")

    # Generate the study plan content
    study_plan = f"""# 学习清单 (Study Plan)

## 关键技能 (Key Skills from JD)
- {chr(10)+'- '.join(found_keywords)}

## 高频面试题及参考答案 (Top Interview Questions)

1. **Python: 请解释 Python 中的生成器 (Generator) 及其与迭代器 (Iterator) 的区别？**
   - **参考答案:** 生成器是一种特殊的迭代器，使用 `yield` 关键字返回值。与返回整个列表的普通函数不同，生成器每次产生一个值，并在产生值后暂停执行，保留其状态。这使得生成器在处理大数据集时非常节省内存，因为它们一次只把一个元素加载到内存中。所有的生成器都是迭代器，但不是所有的迭代器都是生成器。

2. **API: 什么是 RESTful API？它的主要原则是什么？**
   - **参考答案:** REST (Representational State Transfer) 是一种软件架构风格。RESTful API 主要原则包括：
     - **无状态性 (Statelessness):** 客户端到服务器的每个请求必须包含理解和完成该请求所需的所有信息。
     - **统一接口 (Uniform Interface):** 使用标准的 HTTP 方法（GET, POST, PUT, DELETE）。
     - **客户端-服务器分离 (Client-Server):** 职责分离，提高系统的可移植性和可扩展性。
     - **可缓存性 (Cacheability):** 响应应被隐式或显式地标记为可缓存或不可缓存。

3. **MLOps: 简述 MLOps 的生命周期，以及它与传统 DevOps 的区别？**
   - **参考答案:** MLOps 生命周期通常包括：数据收集与准备、模型训练与评估、模型部署、模型监控与重训练。
   - **与 DevOps 的区别:** 传统 DevOps 主要关注代码的版本控制、持续集成 (CI) 和持续交付 (CD)。而 MLOps 不仅涉及代码，还需要管理**数据**版本和**模型**版本。此外，由于模型性能会随时间衰减（概念漂移/数据漂移），MLOps 需要持续的**模型监控 (CT - Continuous Training)**，并在必要时自动触发重训练，这是传统软件开发中没有的。

## 下一步行动 (Next Steps)
- [ ] 复习上述核心概念
- [ ] 针对 JD 中的其他技能点进行针对性练习
"""

    with open(plan_path, 'w', encoding='utf-8') as f:
        f.write(study_plan)
        
    print(f"Study plan successfully generated at: {plan_path}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    jd_file = os.path.join(current_dir, "jd.txt")
    plan_file = os.path.join(current_dir, "study_plan.md")
    
    generate_study_plan(jd_file, plan_file)
