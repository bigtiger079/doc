# Frida 简介和 Hook实战

### 1.Frida是什么？

Frida是一款基于python + javascript 的hook框架， 通杀android\ios\linux\win\osx等各平台， 主要使用动态二进制插桩技术。

#### 插桩技术

插桩技术是将额外的代码注入程序中以收集运行时的信息，可分为两种：

（1）源代码插桩（Source Code Instrumentation(SCI)）：额外代码注入到程序源代码中。

（2）二进制插桩（Binary Instrumentation(BI)）：额外代码注入到二进制可执行文件中。

- 静态二进制插桩：在程序执行前插入额外的代码和数据，生成一个永久改变的可执行文件。  
- 动态二进制插桩：在程序运行时实时地插入额外代码和数据，对可执行文件没有任何永久改变。

> 动态二进制插桩（DBI）将外部代码注入到现有的（正在运行的）二进制文件中，使它们能够做一些以前没有做过的事情。这个过程不是利用了漏洞，因为代码注入并不是通过你之前必须搞清楚的一些漏洞所导致的。它也不是调试，因为你没有将调试器附加到二进制文件上，尽管你可以做类似调试的一些事情。

### 2.你能用DBI做些什么呢？

- 访问进程的内存  
- 在应用程序运行时覆盖一些功能  
- 从导入的类中调用函数  
- 在堆上查找对象实例并使用这些对象实例  
- Hook，跟踪和拦截函数等等


### 3.Frida的网址

[官网: https://www.frida.re/](https://www.frida.re/)  
[github: https://github.com/frida/frida](https://github.com/frida/frida)

### 4.Frida的安装

**环境要求：**     

- 系统环境 - Windows, macOS, or GNU/Linux   
- Python – 最新的3.x版本

**通过 pip 安装frida**


```
pip install frida
```

**frida server**  

在 frida的 [github: https://github.com/frida/frida/releases](https://github.com/frida/frida/releases)  上可以直接下载对应系统已经编译好的 `frida server`

我们需要下载的文件名的格式是： `frida-server-(version)-(platform)-(cpu).xz`  
比如： `frida-server-11.0.12-android-x86_64.xz`

将下载后的压缩包解压得到 `frida-server`, 然后将该文件推送到Android设备上

	adb push frida-server /data/local/tmp/ 

将android设备上的`frida-server`添加执行权, 并运行该程序(需要root权限)

	adb shell
	su
	cd /data/local/tmp
	chmod +x frida-server
	./frida-server &
	


### 5.frida tools

（1） frida CLI: 是一个交互式解释器（REPL）模仿了IPython的一些很不错的功能   
（2） frida-ps: 用于列出进程的一个命令行工具，当我们需要跟远程系统进行交互的时候，这个是非常有用的   


	# 连接frida到一个一个USB设备上,同时列出该设备上运行中的进程
	$ frida-ps -U
	
	# 列出运行中的程序
	$ frida-ps -Ua
	
	# 列出安装的程序
	$ frida-ps -Uai
	
	# 连接frida到一个指定的设备上
	$ frida-ps -D 0216027d1d6d3a03



（3） frida-trace: 是用来动态追踪方法调用的一个工具


	# Trace recv* and send* APIs in Safari
	$ frida-trace -i "recv*" -i "send*" Safari
	
	# Trace ObjC method calls in Safari
	$ frida-trace -m "-[NSView drawRect:]" Safari
	
	# Launch SnapChat on your iPhone and trace crypto API calls
	$ frida-trace -U -f com.toyopagroup.picaboo -I "libcommonCrypto*"

(4) frida-discover: 用于探测一些程序的内部方法的一个工具， 然后再通过frida-trace来进行跟踪， 对于没有逆向经验的来说是好东西  


	$ frida-discover -n name
	$ frida-discover -p pid

(5) frida-ls-devices: 是一个可以列出连接了的设备， 当我们需要同时操作多个设备的时候时非常有用的。

	# Connect Frida to an iPad over USB and list running processes
	$ frida-ls-devices

(6) frida-kill: 用于杀死进程的工具

	frida-kill -D <DEVICE-ID> <PID>


### 6.Java Api简介

	Java.available
	
	Java.enumerateLoadedClasses(function(){
		onMatch: function (className)
	
		onComplete: function ()
	})
	
	
	Java.enumerateLoadedClassesSync()
	
	Java.perform(fn)
	
	Java.use(className)  
		$new() 
		$dispose() 

	Java.scheduleOnMainThread(fn)

	Java.choose(className, callbacks)

	Java.cast(handle, klass)


### 7.实战 CrackMe1


### 8.实战 CrackMe2

