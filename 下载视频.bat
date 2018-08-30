@echo off
choice /c:YN  /M:"是否接着上次继续爬取？"
if %errorlevel%==2 goto no
if %errorlevel%==1 goto yes
:yes
scrapy crawl video -s JOBDIR=crawls/video_spider_temp -s LOG_FILE=scrapy.log
goto end
:no
choice /c:YN  /M:"需要删除原先的信息文件，是否确认？"
if %errorlevel%==2 goto end
if %errorlevel%==1 goto ok
:ok
del /f /s /q /a ".\crawls\video_spider_temp\*"
DEL "scrapy.log"
set /p url=请输入url地址:
choice /c:YN  /M:"是否爬取同一个系列多个视频？"
if %errorlevel%==2 goto myno
if %errorlevel%==1 goto myyes
:myyes
choice /c:YN  /M:"是否爬取全部？"
if %errorlevel%==2 goto myyes2
if %errorlevel%==1 goto myyes1
:myyes1
scrapy crawl video -a my_url=%url% -a my_playlist=True -s JOBDIR=crawls/video_spider_temp -s LOG_FILE=scrapy.log
goto end
:myyes2
set /p start=请输入开始集数:
set /p end=请输入结束集数:
scrapy crawl video -a my_url=%url% -a my_playlist=True -a start_num=%start% -a end_num=%end% -s JOBDIR=crawls/video_spider_temp -s LOG_FILE=scrapy.log
goto end
:myno
scrapy crawl video -a my_url=%url% -a my_playlist=False -s JOBDIR=crawls/video_spider_temp -s LOG_FILE=scrapy.log
goto end
:end
echo good bye！
pause