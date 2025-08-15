import os
import sys
import inspect

sys.path.append('src')
from clicker import Clicker

# 打印clicker.py文件的修改时间
print(f"clicker.py修改时间: {os.path.getmtime('src/clicker.py')}")

# 打印Clicker类的代码
print("\nClicker类代码:")
print(inspect.getsource(Clicker))