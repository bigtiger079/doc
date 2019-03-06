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


## boot.img 解压和打包

1. 工具： [unpackbootimg, mkbootimg](https://code.google.com/archive/p/android-serialport-api/downloads)，[mkbootfs](https://code.google.com/archive/p/zen-droid/downloads)

### 系统 boot.img 的备份

1. 在 `/dev/block/platform/....../byname/` 目录下可以查看所有分区目录的挂载名称信息

2. 使用 `dd if=/dev/block/*** of=/path/to/backup.img` 即可备份 

### 拆包

1. 使用 `unpackbootimg -i boot.img -o outdir` 命令即可将 boot.img 拆分出 kernel 文件和 ramdisk.gz 文件
2. ramdisk.gz压缩文件中是一个 boot.img-ramdisk 文件， 通过 `file boot.img-ramdisk` 命令可以查看改文件的类型为： ASCII cpio archive 
3. 使用 `gzip -dc ramdisk.gz | cpio -i ` 可以直接将 ramdisk.gz 里面的 boot.img-ramdisk 解压出来

#### 打包

1. `mkbootfs ramdisk | gzip -n -f -c > boot.img-ramdisk.cpio.gz` 其中，ramdisk即为将要被打包的ramdisk目录。
2. 使用mkbooting工具，将所有文件打包成boot.img。


```
	mkbootimg  --cmdline "androidboot.hardware=qcom loglevel=1" --kernel boot.img-kernel  --ramdisk boot.img-ramdisk.cpio.gz --base 0x60400000 --pagesize 4069 -o new_boot.img
```
> 其中 base,pagesize, cmdline, 信息可以通过拆包的时候得到的 *-base, *-pagesize, *-cmdline 这三个文件查看得到

#### fastboot刷机

1. 通过 `adb reboot bootloader` 命令让手机进入 bootloader 模式
2. 进入bootloader模式之后通过 `fastboot flash boot new_boot.img` 将new_boot.img 刷入手机
> fastboot 工具位于 sdk/platform-tools 目录下

bootloader 其他命令：

	fastboot  flashing  unlock    # 设备解锁，开始刷机
	
	fastboot  flash  boot  boot.img    # 刷入 boot 分区。如果修改了 kernel 代码，则应该刷入此分区以生效
	
	fastboot  flash  recovery  recovery.img    # 刷入 recovery 分区
	
	fastboot  flash  country  country.img    # 刷入 country 分区。这个分区是开发组自己划分的，别的 Android 设备上不一定有
	
	fastboot  flash  system  system.img    # 刷入 system 分区。如果修改的代码会影响 out/system/ 路径下生成的文件，则应该刷入此分区以生效 
	
	fastboot  flash  bootloader  bootloader    # 刷入 bootloader
	
	fastboot  erase  frp    # 擦除 frp 分区，frp 即 Factory Reset Protection，用于防止用户信息在手机丢失后外泄
	
	fastboot  format  data    # 格式化 data 分区
	
	fastboot  flashing lock    # 设备上锁，刷机完毕
	
	fastboot  continue    # 自动重启设备