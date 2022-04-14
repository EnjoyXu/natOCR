# natOCR
本人所在的大学的学生正在周期性做核酸，奈何学校信息系统不完善，需要每轮核酸周期结束后搜集同学们的核酸检测报告结果，并判断是否在本轮内做过核酸。我应辅导员请求，利用了百度的paddleOCR项目开发了自动识别检测的代码，仅供大家参考。
>用途：OCR核酸报告结果，并查询是否在一轮核酸检测周期内做过核酸，读取姓名-学号对应表，生成相应统计表格。

# 1.安装环境

## 1.1创建虚拟环境（强烈建议，若不想可直接跳过）

	**!!!!!!!!!把工作目录切换到该文件夹!!!!!!!**

复制以下语句到cmd

1. 有conda

```bash
conda -n ocr python=3.7

conda activate ocr
```

2. 无conda，使用`virtualenv`

```bash
python -m pip install --upgrade pip

pip install virtualenv
```

```bash
virtualenv venv

.\venv\Scripts\activate.bat
```



## 1.2 安装依赖

```bash
pip install paddlepaddle==2.2.2 -i https://mirror.baidu.com/pypi/simple

pip install -r requirements.txt
```



# 2.使用

将核酸检测截图放入`pictures`文件夹，把姓名-学号的excel表格`(.xlsx)`放入该文件夹下，再将`.time`文件的文件名重命名为本轮核酸开始的时间(默认周期为5天，可在`ocr.py`中修改period参数) ，运行`ocr.py`文件即可（记得在虚拟环境下运行）

