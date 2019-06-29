# IDApro

## 1. 导入jni.h

1. IDAPro 设置 compiler

![](../art/ida_compiler_options.png)

(1) 选择Visual C++
(2) Include directories 填入NDK中包含jni.h 的路径和VS2008中VC的include路径，两个路径间用”;”分隔。
(3) Predefined macros 加入 __lint__ 宏定义。

2. 修改 jni.h

![](../art/jni_modify.png)

(1) 注释掉 #include<stdarg.h>
(2) 注释掉

    typedef enum jobjectRefType {
        JNIInvalidRefType = 0,
        JNILocalRefType = 1,
        JNIGlobalRefType = 2,
        JNIWeakGlobalRefType = 3
    } jobjectRefType;

以及与之有关的引用

(3) 修改 `#define JNIEXPORT  __attribute__ ((visibility ("default"))) ` 为 `#define JNIEXPORT`

3. 选择菜单 File -> Load file -> Parse C header file(Ctrl+F9) 导入刚才修改好的jni.h文件即可

如果还有其他错误，则根据错误提示进行修改

4. 切换到 Structures 窗口， 按insert键开始插入结构


## 2. IDA 动态调试

### 对于没有反调试的步骤：
1. adb push d:\android_server(IDA的dbgsrv目录下) /data/local/tmp/android_server

2. adb shell

3. su #一定要有root权限

4. cd /data/local/tmp

5. chmod 777 android_server (给android_server可执行权限)
./android_server对本地设备端口进行监听

6. 再开一个cmd:
adb forward tcp:23946 tcp:23946（端口转发，调试手机上的某个进程要有协议支持通信）让远程调试端IDA可以连接到被调试端

7. 使用IDA连接上转发的端口，查看设备的所有进程，找到需要调试的进程。具体步骤方法为：在Debugger选项卡中选择Attach，选择android debugger，点击Ok。

8. 动静结合方式（基地址+相对地址）确定函数地址进行调试。

### 对于有反调试的步骤：

1. 启动android_server

2. 端口转发adb forward tcp:23946 tcp:23946

3. adb shell am start -D -n 包名/类名；出现Debugger的等待状态
（说明：以启动模式启动，是停在加载so文件之前，包名可以在androidmanifest文件中找到）

4. 打开IDA，附加上对应的进程之后，设置IDA中的load so时机，即在debug options中设置；

5. 运行命令：jdb -connect com.sun.jdi.SocketAttach:hostname=localhost, port=8700

6. 点击IDA运行按钮，或者F9快捷键。
