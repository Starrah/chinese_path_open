"""
### 概述
这是一个用于解决某些文件在**有中文路径**的情况下无法被正常打开的问题的脚本。
通常是由于把系统编码切换为UTF-8后，某些不适应编码切换的文件无法通过双击打开正常运行的情况。
例如经测试jdk11.0.6在切换为UTF-8编码的Windows10中文版上无法双击jar正确打开jar文件，但用本脚本可以解决问题。

### 本程序解决问题的适用范围：
- 按照下面的操作说明，可以解决**在资源管理器中无法双击打开**的问题。
- 当然根据本程序的原理，也可以用于解决其他的通过调用一定的shell命令，运行程序或打开文件的场合的所有问题。
  - 在这种情况下，只按照下面使用方法的第3点所述执行修改后的shell命令即可。
  - 本程序的原理是通过把带有中文的路径中的路径部分提取出来作为CWD（当前工作目录），然后在shell中只执行参数的文件名部分。
  - 从而使得文件可以被以CWD的方式直接找到，从而不用把中文的所在目录传进命令行了。

### 请注意该程序有使用限制：
0. 前提：需要安装了python3。
1. 要打开的文件的**文件名（不含路径）必须是全英文的**。
2. 用于打开程序的exe文件的路径和被打开的文件的路径两者之中，至多只能有一个含有中文路径。
3. **脚本文件chinese_path_open.py必须放置于一个全英文目录下**。

### 在资源管理器的双击打开的使用方法：
1. 查看注册表HKEY_CLASSES_ROOT/.xxx项（xxx是想要打开的文件的扩展名）的默认键的属性值字符串，记为s。
2. 查看注册表HKEY_CLASSES_ROOT/s/shell/Open/command项，它的默认键的属性值字符串就是程序运行实际执行的shell命令。通常为程序的exe+参数+"%1"，其中%1表示在Explorer中双击打开文件时，双击的文件的路径。
3. 修改HKEY_CLASSES_ROOT/s/shell/Open/command项的默认键的值为下面所述的命令。

### 用本脚本包装shell命令
这里有两种方法：
1. 在原有命令前面加入（包含双引号也要加入） "你的python.exe绝对路径" "本脚本绝对路径"
2. 在原有命令前面加入（包含双引号也要加入） cmd /c python "本脚本绝对路径"

### 例如
.jar文件的打开命令（也就是HKEY_CLASSES_ROOT/jarfile/shell/Open/command的默认键的值）为"C:\Program Files\Java\jdk-11.0.6\bin\javaw.exe" -jar "%1"
第一种方法是将它改为"D:\ProgramData\Anaconda3\python.exe" "D:/Program Files/chinesepathrun.py" "C:\Program Files\Java\jdk-11.0.6\bin\javaw.exe" -jar "%1"
第二种方法是将它改为cmd /c python "D:/Program Files/chinesepathrun.py" "C:\Program Files\Java\jdk-11.0.6\bin\javaw.exe" -jar "%1"
请注意上面的"D:/Program Files/chinesepathrun.py"需要改为你实际放置本脚本文件的绝对路径。
在上面两种改法中任选其一替换原来的HKEY_CLASSES_ROOT/jarfile/shell/Open/command的默认键的值即可。
"""

import sys
import subprocess
import re
from os import path

regexp = re.compile(r'[^\x00-\x7f]')


def hasNonAsciiChar(a: str) -> bool:
    """判断一个字符串中是否含有非ASCII字符"""
    return not not regexp.search(a)


res = []
cwd = None
error = None

if hasNonAsciiChar(sys.argv[0]):
    error = "警告：本脚本文件位于非全英文目录下。请将本文件移动至全英文目录下才能使用，详见本文件的注释。"

for arg in sys.argv[1:]:
    if path.exists(arg) and hasNonAsciiChar(arg):
        # 找到含有中文字符、确实是路径（通过验证文件的确存在）的参数
        # 设置其路径部分为当前目录cwd，把命令行参数替换为只有文件名的部分
        # 从而规避中文字符出现在命令行参数里面
        dirname = path.dirname(arg)
        if cwd is None or cwd == dirname:
            cwd = dirname
            basename = path.basename(arg)
            if hasNonAsciiChar(basename):
                error = "警告：参数" + arg + "的文件名（不含路径）中含有中文，这超出了本脚本能解决问题的范围。"
            res.append(path.basename(arg))
        else:
            error = "警告：输入的参数中含有多个中文路径，因此无法通过单一的cwd来过滤掉这些路径。"
            res.append(arg)
    else:
        res.append(arg)

print("实际运行的命令行路径和参数为", end="")
print(res, end="")
print("。此为调试信息，可以忽略。")
if error is not None:
    print(error)
    print("因此程序运行可能不正确。如果仍要继续运行，请输入任意字符后继续。如果要取消，请直接关闭窗口。")
    input()
subprocess.Popen(res, cwd=cwd)
