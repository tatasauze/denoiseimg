均值：補零
中間值：重複（重複最外邊）
高斯：反折
雙邊濾波：反折


[Part-1] Denoise via spatial filtering
Step-0: 
Please program a "Gaussian" random noise generator, which is able to generate a 0-mean Gaussian noise with an arbitrary user-specified sigma (standard variation).
Step-1:
Add the generated N-by-N 2D noise pattern (of several, different sigma value, such as sigma=4, 2, 1, 0.5, 0.1, 0.01) to the "lena.bmp" released in Hw#1 and any one of the attached  images to obtain some noisy images. 
Step-2: 
Try to implement a convolution procedure or a filtering procedure. And then, implement some low-pass filter (gaussian filter, average filter, etc), median filter, or bilateral filter to remove the noise on your images via spatial filtering.
Step-3:
Output your denoising result (image), observe the detail parts of your image, and then write a report to discuss what you observe in this experiment set. 

[Part-2]  Edge detection via spatial filtering
Step-0: 
Read any of the attached image file, and covert the raw RGB data to grayscale via Gray=(R+B+G)/3.
Step-1: 
Try to use high-pass filters, such as Sobel operator or Prewitt operator or first-order difference, to detect the edges via the sptial filtering procedure you programmed in Part-1.
Step-2:  
Output each of your edge detection results as one single image, observe the edge detials, and then write a report. 

[第1部分] 透過空間濾波進行去雜訊  
步驟0：  
請撰寫一個「高斯（Gaussian）」隨機雜訊產生器，能夠產生平均值為0，且使用者可自行指定 sigma（標準差）的高斯雜訊。  

步驟1：  
將產生的 N×N 二維雜訊圖樣（使用多種不同的 sigma 值，例如 sigma=4、2、1、0.5、0.1、0.01）加入在 Hw#1 提供的「lena.bmp」以及任一張附加影像上，以產生一些含雜訊的影像。  

步驟2：  
嘗試實作一個卷積（convolution）或濾波（filtering）程序。接著，實作一些低通濾波器（如高斯濾波器、平均濾波器等）、中值濾波器（median filter），或雙邊濾波器（bilateral filter），透過空間濾波來去除影像中的雜訊。  

步驟3：  
輸出你的去雜訊結果（影像），觀察影像中的細節部分，並撰寫一份報告說明你在此實驗中觀察到的現象。  


[第2部分] 透過空間濾波進行邊緣偵測  
步驟0：  
讀取任一張附加影像檔，並將原始 RGB 資料轉換為灰階影像，使用公式 Gray = (R + B + G) / 3。  

步驟1：  
嘗試使用高通濾波器，例如 Sobel 運算子、Prewitt 運算子或一階差分，透過你在第1部分所撰寫的空間濾波程序來偵測邊緣。  

步驟2：  
將每一種邊緣偵測結果各自輸出為單一影像，觀察邊緣細節，並撰寫一份報告。