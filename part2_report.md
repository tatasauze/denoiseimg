邊緣檢測


圖像選擇：
three channles coin.png average_denoise

處理方式：
derived_vertical
與水平檢測不同的是，垂直檢測出的圖像外圍輪廓在影像上是呈現凸出來的樣子，而水平檢測是呈現凹下去的模樣，且影像色階也是變成黑白，也是只有外圍輪廓掃描出來，物件內部的細節沒有偵測

derived_horizental
在彩色圖像上，硬幣的外圍輪廓都有檢測出來，但細部上的紋路就沒有刻畫出來，且有趣的是影像掃出來後變成灰白色階。

差分檢測只能測外圍輪廓我覺得應該是因為物件內部色差不大，相減值太小，看不出來。影像整體呈現灰白色應該是兩個像素相差不大，所0整體只在 256的小數字區域

sobel
不像是前兩者在輪廓與物件內部一樣平滑模糊，雖然整體物件還是不太看得出來細節，但是能隱約分辨出上面圖案，且在線條與輪廓上有比較明顯的抖動（不平滑）的感覺，圖像有一種像是浮雕的感覺

prewitt
我不太了解為什麼prewitt會是全白的，代碼我看了幾次是沒有問題的，不知道是不是因為彩色的關係，而且就連gaussian , bilateral , meduin, sobel都是一樣，可能要看看是不是合併通道後會不一樣

圖像選擇：
single channel coin.png

處理方式：
derived_vertical

derived_horizental

sobel

prewitt
