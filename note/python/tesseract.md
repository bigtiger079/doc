# Python3.x：pytesseract识别率提高（样本训练）

1，下载并安装3.05版本的tesseract

　地址：https://sourceforge.net/projects/tesseract-ocr/

2，如果你的训练素材是很多张非tif格式的图片，首先要做的事情就是将这么图片合并（个人觉得素材越多，基本每个字母和数字都覆盖了训练出来的识别率比较好）

　下载这个工具：VietOCR.NET-3.3.zip

　地址：http://sourceforge.net/projects/vietocr/files/latest/download?source=files

　首先进行jpg,gif,bmp到tif的转换，这个用自带的画图就可以。然后使用VietOCR.NET-3.3进行多张 tif的merge。

3，Make Box Files。在orderNo.tif所在的目录下打开一个命令行，输入

　C:\Program Files\Tesseract-OCR>tesseract.exe lang.jhy.exp8.TIF lang.jhy.exp8 batch.nochop makebox

4， 使用jTessBoxEditor打开orderNo.tif文件，需要记住的是第2步生成的orderNo.box要和这个orderNo.tif文件同在一个目录下。逐个校正文字，后保存。

　下载jTessBoxEditor工具进行每个自的纠正（注意有nextpage逐页进行纠正）

　地址：http://sourceforge.net/projects/vietocr/files/

5，Run Tesseract for Training。输入命令：

　C:\Program Files\Tesseract-OCR>tesseract.exe lang.jhy.exp8.TIF lang.jhy.exp8 nob

　atch box.train

6，Compute the Character Set。输入命令：

　C:\Program Files\Tesseract-OCR>unicharset_extractor.exe lang.jhy.exp8.box

　Extracting unicharset from lang.jhy.exp8.box

　Wrote unicharset file ./unicharset.

7，新建文件“font_properties”。如果是3.01版本，那么需要在目录下新建一个名字为“font_properties”的文件，并且输入文本:（这里的jhy就是lang.jhy.exp8的中间字段）

　jhy   1 0 0 1 0

8，Clustering。输入命令：

　C:\Program Files\Tesseract-OCR>cntraining.exe lang.jhy.exp8.tr

　Reading lang.jhy.exp8.tr ...

　Clustering ...

　Writing normproto ...

9， 此时，在目录下应该生成若干个文件了，把unicharset, inttemp, normproto, pfftable这几个文件加上前缀“selfverify.”。然后输入命令：

必须确定的是1、3、4、5、13行的数据不是-1，那么一个新的字典就算生成了。

此时目录下“selfverify.traineddata”的文件拷贝到tesseract程序目录下的“tessdata”目录。

以后就可以使用该该字典来识别了，例如：

tesseract.exe test.jpg out –l selfverify
