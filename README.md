# 新闻搜索引擎

![home](images/home.png)

# 使用方法

1. 安装python 3.4+环境

2. 安装依赖包：

```
pip install xlrd
pip install jieba
pip install Flask
pip install requests
pip install sklearn
pip install pandas
```

5. 进入web文件夹，运行main.py文件
6. 打开浏览器，访问http://127.0.0.1:5000/ 输入关键词开始测试

如果想抓取最新新闻数据，那么运行下面的命令：

```
cd code
python spider.py
```

每次更新数据之后需要构建索引，那么进入code文件夹，然后运行setup.py，再按上面的方法测试。

# 功能

- 匹配任意关键词：默认使用该选项
- 匹配全部关键词：将关键词用`()`括住，即可搜索包含括号内的所有关键词的页面。
- 条件搜索：目前支持选择球类和范围
- 推荐系统
