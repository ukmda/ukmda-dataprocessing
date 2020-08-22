md c:\temp\files
set mmdd=%1\2019%1%2%
 
move d:\meteorcamdata\tc\2019\2019%mmdd%\*.xml c:\temp\files
move d:\meteorcamdata\tc\2019\2019%mmdd%\*P.jpg c:\temp\files
move c:\temp\files\*  d:\meteorcamdata\tc\2019\2019%mmdd%
