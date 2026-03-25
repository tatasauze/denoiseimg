直接看加入噪音的圖像會發現當sigma愈大，圖像愈糊，但如果將加噪圖像減去原圖像來看，不管sigma多大，其實噪音本身都還滿像的
不知道是我眼睛糊糊的還是真的是這樣，當sigma接近1的時候噪音本身看起來最薄，越往0跟4跑，看起來越厚
其實很難看出來，如果要說有差異的話，比較大的地方是在淺色大面積的地方，當 sigma越大，圖像白色的地方會比較黑，不過邊緣模糊的情況倒是看不太出差異在哪
因為看不太出來差異在哪裏，所以直接將噪音變異數提示到40，結果很明顯就是圖片顆粒感變重很多，且邊緣肉眼可見的模糊，白色大面積的地方也很明顯的變成灰色，整體色彩度下降

降噪的圖片選擇：
Lena: mean=0, sigma=4 選擇原因，看看噪音變異大的降起來反差是否比較大

設置參數
bilateral：
    spacial_sigmas = [i for i in range(1,6)]
    range_sigmas = [i for i in range(1,6)]
average_img: kernel 3x3
median_img : kernel 3x3
gaussian_img : kernel 3x3 sigma=4  

觀察結果：高斯與平均filter肉眼可見的將邊界變得模糊，median 較這兩個方式更保有sharp（銳利嗎，反正就是邊界色彩度差異更大）邊界，但bilateral filter 才是這幾個中保真度最高的，邊界最清晰，空間與色彩範圍從1~5共產生25張降噪圖像，我看不太出來這兩個參數在這區間造成的具體視覺變化，但肉眼可分辨的是當空間與色彩變異數都是1的時候，最能保有lena帽子上的紋理。整體來說，gaussian, average, median這三種方式造成復原影像上模糊的感覺，bilateral 在復原上除了一些些高斯噪音無法移除外，最最大的不同是對比度提升，且空間與色彩變異數為1時的對比度比變異數設定5來的更明顯。四種降噪方法來看，我覺得的bilateral效果最好


coin: mean=0, sigma=0.01 選擇原因，當前肉眼看起來還算清楚且也看得出明顯的噪音

設置參數
bilateral：
    spacial_sigmas = [i for i in range(1,6)]
    range_sigmas = [i for i in range(1,6)]
average_img: kernel 3x3
median_img : kernel 3x3
gaussian_img : kernel 3x3 sigma=0.01

不知道高斯降噪的sigma 設成0.01會不會造成計算時候數值爆炸

觀察結果：gaussian 與 average 相比，average 看起來像是失焦的鏡頭拍出來的影像，medain 與 average 相比在邊緣上沒有那麼模糊，但跟 gaussian 完全無法比較，太模糊了， gaussian 與 bilateral相比，有別於 lena 的結果，在彩色的圖像復原上gaussian比較沒那麼模糊，邊緣與細節保真。調整bilateral空間與色彩上的變異數看不太出什麼差異，我猜是因為3 channels的關係，有點將差異去平均導致視覺上看不太出來。四個降噪方法來看，我覺得average的效果最好