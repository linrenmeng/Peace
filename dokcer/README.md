#### repo_python 

每个文件夹储存github的python仓库，以reponame命名



#### venv_python

每个文件夹储存每个python仓库的虚拟环境，以owner_reponame命名



#### test/testdemo.py

初步测试pytest运行每个仓库，并且抓取cpu指令与空间等结果，储存在/results中



#### results

储存一些结果



#### llmchange.py

替换LLM优化后的代码或还原原始提取代码



#### findsave.py, output.py,outputsave.py

find是测试，output是完整

提取目标函数函数体，并保存



#### copy_conftest.py

将data/conftest.py复制到每一个仓库根目录下



#### opt_venv_python.py

为所有虚拟环境安装包或统一操作









