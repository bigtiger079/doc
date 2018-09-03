# Android

### zygote注入器实现

#### 1.关闭SELinux

获取SELinux的配置目录  
获取SELinux配置文件中SELinux功能的开关状态("/sys/fs/selinux", "/proc/mounts");  
关闭selinux

#### 2.附加到zygote进程，阻塞进程，保存寄存器现场

ptrace附加，waitpid， 获取寄存器值，保存zygote进程注入前的寄存器环境

#### 3.获取zygote进程中关键函数的地址

	mprotect/dlopen/dlsym/mmap/munmap

zygote进程中函数地址=zygote进程模块基址+zygote进程内存偏移地址  
zygote进程偏移地址=辅助进程内存偏移地址（进程中包含相同模块）  
辅助进程内存偏移地址 =   辅助进程中函数地址-辅助进程模块基址

#### 4.远程调用mmap函数分配内存空间

设置堆栈布局

#### 5.配置shellcode

调用dlopen函数加载指定模块
调用dlsym函数获取模块中关键函数地址
调用已获取的关键函数

#### 6.远程调用shellcode

lr置0， pc置0

#### 7.远程调用munmap释放内存

#### 8. 恢复进程， 恢复寄存器环境， 释放附加


## 其他

`__attribute__((constructor))`属性。使用这个constructor属性编译的普通ELF文件被加载入内存后，最先执行的不是main函数，而是具有该属性的函数。同样，本项目中利用此属性编译出来的so文件被加载后，尽管so里没有main函数，但是依然能优先执行，且其执行甚至在`JniOnload`之前。于是逆向分析了一下编译出来的so库文件。发现具有constructor属性的函数会被登记在`.init_array`中。（相对应的destructor属性会在ELF卸载时被自动调用，这些函数会被登记入`.fini_array`）