@echo off
choice /c:YN  /M:"�Ƿ�����ϴμ�����ȡ��"
if %errorlevel%==2 goto no
if %errorlevel%==1 goto yes
:yes
scrapy crawl video -s JOBDIR=crawls/video_spider_temp -s LOG_FILE=scrapy.log
goto end
:no
choice /c:YN  /M:"��Ҫɾ��ԭ�ȵ���Ϣ�ļ����Ƿ�ȷ�ϣ�"
if %errorlevel%==2 goto end
if %errorlevel%==1 goto ok
:ok
del /f /s /q /a ".\crawls\video_spider_temp\*"
DEL "scrapy.log"
set /p url=������url��ַ:
choice /c:YN  /M:"�Ƿ���ȡͬһ��ϵ�ж����Ƶ��"
if %errorlevel%==2 goto myno
if %errorlevel%==1 goto myyes
:myyes
choice /c:YN  /M:"�Ƿ���ȡȫ����"
if %errorlevel%==2 goto myyes2
if %errorlevel%==1 goto myyes1
:myyes1
scrapy crawl video -a my_url=%url% -a my_playlist=True -s JOBDIR=crawls/video_spider_temp -s LOG_FILE=scrapy.log
goto end
:myyes2
set /p start=�����뿪ʼ����:
set /p end=�������������:
scrapy crawl video -a my_url=%url% -a my_playlist=True -a start_num=%start% -a end_num=%end% -s JOBDIR=crawls/video_spider_temp -s LOG_FILE=scrapy.log
goto end
:myno
scrapy crawl video -a my_url=%url% -a my_playlist=False -s JOBDIR=crawls/video_spider_temp -s LOG_FILE=scrapy.log
goto end
:end
echo good bye��
pause