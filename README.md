# Pose2Carton 
EE228 课程大作业 利用3D骨架控制3D卡通人物 (https://github.com/yuzhenbo/pose2carton)

数据组别： 1

数据类型： 8组匹配 + 4组蒙皮

# Maya 环境配置

本项目配置maya环境主要经历了以下流程

- 下载安装maya2020
- 配置主机环境变量，以便通过命令行运行mayapy
- 在mayapy安装pip包，再通过pip包安装numpy包
- 在pycharm运行环境设置中将mayapy设置为运行py脚本的环境

完成以上步骤后便能成功运行fbx_parser.py脚本，即完成环境配置

# 匹配流程

匹配代码主要是transfer.py

- 先熟悉了transfer.py的主匹配接口函数，即transfer_one_sequence,该函数参数分别为预匹配模型riginfo文件地址，序列文件地址，以及是否使用网络模型（布尔变量），查看该函数了解到该函数在进行匹配时调用了主函数transfer_given_pose,我仔细阅读该代码了解了匹配流程，即建立关节到序号，序号到关节的双映射字典，然后读入匹配字典，读入pkl的旋转矩阵序列，通过FK方法得到各个关节的4*4变换矩阵G，旋转关节以及各vertices，最后保存匹配信息pkl文件。
- 此外我也注意到有clean_info这个函数，根据教程readme文件指导，了解该函数是去除名字空间，为了不覆盖去除前info文件，我修改了代码将清除后文件保存为xx_clean.txt。当然这需要修改transfer_given_pose的路径replace逻辑，正好有using_online_model这个布尔变量来区分。

熟悉这些函数便可成功进行模型匹配，然后运行vis代码进行可视化

对于vis脚本我有所改动，项目初期没有smpl模型，所以我将代码改成可以不显示human模型。

（ps：由于在初期本项目对transfer.py的小改动不少，后期原代码仓库对代码有更新但是merge比较困难，且该代码也能完成匹配，故而该代码与最新原仓库代码有所差异）



# 新增脚本说明

util_cat.py是我新增的工具函数脚本，里面最主要的新增函数便是print_joint2和read_match，这个两个函数将匹配模型关节和序号映射关系输出到一个txt文件，再自动读入这个txt文件存成匹配字典，极大地方便了匹配。

使用方法：

- print_joint2(infoname:info文件名称) 

    功能：输出txt文件到model/match_list/xx_joint.txt(x项目代码上传代码中没有这个路径，代码未自行创建文件夹，若使用该函数需要自行创建路径)

- read_match(path:关节配对txt文件名称)

    功能：读取关节配对信息存成字典返回



# 项目结果

本项目匹配的各模型通过vis.py脚本可视化得到的结果如下（8+4），均选择了obj_seq_5序列中某一smpl模型动作作为参照

![image](img/1222.png)
![image](img/2832.png)
![image](img/2965.png)
![image](img/5992.png)
![image](img/9750.png)
![image](img/10567.png)
![image](img/11656.png)
![image](img/15633.png)
![image](img/amy.png)
![image](img/jackie.png)
![image](img/girl.png)
![image](img/rocksana.png)

# 协议 
本项目在 Apache-2.0 协议下开源

所涉及代码及数据的所有权以及最终解释权归倪冰冰老师课题组所有.
