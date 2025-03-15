# Peace: Towards Efficient Project-Level Performance Optimization via Hybrid Code Editing
Source code for Peace



### Description

This repository contains the project-level PEACExec, training and evaluation code for the paper "*Peace: Towards Efficient Project-Level Performance Optimization via Hybrid Code Editing*".



![image-20250315152714098](framework.png)

​									  **Fig.1** The overall framework of PEACE

**Fig. 1** shows the overall framework of PEACE, which aims to opti-mize a target function and ensure the correctness and integrity of the overall project at the same time. To achieve this goal, PEACE first analyzes code contexts to construct an optimizing function se-quence to edit, and then identify valid associated edits. After that, it leverages valid associate edits along with both internal and externalhigh-performance functions to iteratively optimize the functionsin the optimizing function sequence. Specifically, PEACE containsthree main phases: Dependency-Aware Optimizing Function Se-quence Construction (Phase I),Valid Associated Edits Identification(Phase II), and Performance Editing Iteration (Phase III).

## Dependency

Python == 3.10.14

C++17

GCC 9.4.0

Linux

Run the following command in the root directory of this repo:

```shell
pip install -r requirements.txt
```



## 

## Logging

2025-3-14: source code,experiment results, data will be prepared and upload in few days.

2025-3-15: upload PEACE, ValidAssociatedEdit

