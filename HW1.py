from matplotlib import pyplot as plt
import numpy as np
import os
import re

'''
lena.bmp 是灰階圖像，bibitcount=8
pixel Ram 的佔用量： pixel * (bibitcount/8)，因為pixel由bits儲存
'''

# 建立bmp檔頭
class BmpHead:
    def __init__(self):
        self.bfType = 0x4D42  # 'BM'
        self.bfSize = 0 
        self.bfReserved1 = 0
        self.bfReserved2 = 0
        self.bfOffBits = 1078 # 實際讀到的是1162
        self.biSize = 40 # 實際讀到的是124
        self.biWidth = 0
        self.biHeight = 0
        self.biPlanes = 1
        self.biBitCount = 8
        self.biCompression = 0
        self.biSizeImage = 0
        self.biXPelsPerMeter = 0
        self.biYpelsPerMeter = 0
        self.biClrUsed = 0
        self.biClrImportant = 0
    
    def __repr__(self):
        return (
            f"BmpHead(\n"
            f"  bfType={self.bfType}, bfSize={self.bfSize}, bfOffBits={self.bfOffBits},\n"
            f"  biWidth={self.biWidth}, biHeight={self.biHeight}, biBitCount={self.biBitCount}\n"
            f")"
        )

# 讀取Bmp與取得基本內容
class BmpParser:
    def __init__(self,filename:str):
        self.filename = filename
        self.header = BmpHead()
        self.color_map= None
        self.img = None
        self.cleaned_pixel = None # 2-D np.ndarray() of cleaned data
        self._parse()
    
    def _parse(self):
        try:
            with open(self.filename,'rb') as f:
                self._read_header(f)
                self._read_color_map(f)
                self._read_img(f)
                self._decompress_rle8()
        except FileNotFoundError as FE:
            print(FE)
        except Exception as e:
            print(e)            
    
    def _read_header(self,f):
        '''
        bitmap_file_header ( 54 byte )
        小端序 little-endian
        使用int.from_bytes(bytes,byteorder:"little" or "big",signed:bool)
        Args: Bmp file
        Return: BmpHead type(int)
        '''
        try:
            # 1."BM"
            byType = int.from_bytes(f.read(2),byteorder="little")
            if byType != self.header.bfType:
                raise ValueError("not a bmp file")
            # 2.file size
            self.header.bfSize = int.from_bytes(f.read(4),byteorder="little") # 找到問題了，因為是壓縮檔，所以是1162
            # print("debug for BmpWriter bfSize:",self.header.bfSize)
            # 3. reserve
            self.header.bfReserved1 = int.from_bytes(f.read(2),byteorder="little")
            self.header.bfReserved2 = int.from_bytes(f.read(2),byteorder="little")
            # 4. starting of raw img data
            self.header.bfOffBits = int.from_bytes(f.read(4),byteorder="little")
            # print("debug for BmpWriter bfOffBits:",self.header.bfOffBits)
            # 5. info header size
            self.header.biSize = int.from_bytes(f.read(4),byteorder="little")
            # print("debug for BmpWriter biSize:",self.header.biSize)
            # 6. width
            self.header.biWidth = int.from_bytes(f.read(4),byteorder="little")
            # 7. height
            self.header.biHeight = int.from_bytes(f.read(4),byteorder="little")
            # 8. plane
            self.header.biPlanes = int.from_bytes(f.read(2),byteorder="little")
            # 9. bit count
            self.header.biBitCount = int.from_bytes(f.read(2),byteorder="little")
            # 10. compression
            self.header.biCompression = int.from_bytes(f.read(4),byteorder="little")
            # 11 image size
            self.header.biSizeImage = int.from_bytes(f.read(4),byteorder="little")
            # 12. pixel per meter(x)
            self.header.biXPelsPerMeter = int.from_bytes(f.read(4),byteorder="little")
            # 13. pixel per meter(y)
            self.header.biYpelsPerMeter = int.from_bytes(f.read(4),byteorder="little")
            # 14 color used
            self.header.biClrUsed = int.from_bytes(f.read(4),byteorder="little")
            # 15 color important
            self.header.biClrImportant = int.from_bytes(f.read(4),byteorder="little")
        except ValueError as e:
            print(e)
            exit(0)

    def _read_color_map(self,f):
        '''
        After 124 byte
        Args: Bmp file
        Return: byte format
        '''
        color_map_size = self.header.bfOffBits - (14+self.header.biSize) # (color map size + header size) - header size
        # print(color_map_size) 1024 正確
        if color_map_size>0:
            f.seek(124+14)
        self.color_map = f.read(color_map_size)
    
    def _read_img(self,f):
        '''
        Args: Bmp file
        Return: None
        '''
        f.seek(self.header.bfOffBits)
        self.img = f.read(self.header.biSizeImage)
    
    def _decompress_rle8(self):
        '''
        Args: self.img
        Return: np.ndarray, nest value of img in 1-dim.
        ---
        指令邏輯
        1. 重複模式
        [count value]: 如果count大於0，就代表value接下來要重複的次數
        2. 指令模式
            [count value]:如果count等於0，則依照value的不同，執行不同內容
            value = 00 換行
                Y 加一，移動到下一行

            value = 01 結束繪圖
                整張圖畫完，可以直接結束工作

            value = 02 index 跳躍
                再往後多讀取兩個byte[xx yy]，xx代表向右移動、yy向左移動
            value => 03 原樣複製
                看value是多少，就往後讀取幾個byte，之後直接將讀取的內容寫入，但是如果該value是奇數，[value+1]的值會是00，此時就必須要忽略

        Decodeing:

        1. empty canvas
        2. init index (0,0)
        3. while loop: 
            count, value = [idx idx+1]
            idx += 2
        4. if else for count, value
        5. Repeat        
        '''

        if self.img is None:
            return np.array([])

        #1. empty canvas
        height = self.header.biHeight
        width = self.header.biWidth
        canvas = np.zeros((height,width),dtype=np.uint8)

        #2. init index (0,0) and data img
        # index 與 canvas(current_x,current_y)都必須要隨著寫入與讀取去移動
        current_x = 0
        current_y = 0
        idx =0
        encoded_img = np.frombuffer(self.img,dtype=np.uint8)

        data_len = len(encoded_img)

        #3 while loop
        while idx < data_len-1: # 確保有兩個 byte 可讀
            count = encoded_img[idx]
            value = encoded_img[idx+1]
            idx += 2 # 使用了兩個byte

            if count > 0:
                for _ in range(count):
                    if current_y >=height:
                        break

                    if current_x>=width:
                        current_x = 0
                        current_y += 1 
                        #要再檢查一次看是否超出
                        if current_y >=height:
                            break                       
                    
                    # 因為沒有換行所以就只有增加向右方向而已
                    canvas[current_y,current_x] = value
                    current_x += 1

            elif count == 0:

                if value == 0:
                    #換行
                    current_y += 1
                    current_x = 0
                
                elif value == 1:
                    #結束
                    break 

                elif value == 2:
                    #跳躍
                    if idx+3 > data_len:
                        # 確保有跳躍指示
                        break

                    jump_x = encoded_img[idx]
                    jump_y = encoded_img[idx+1]
                    current_y += jump_y
                    current_x += jump_x
                    idx += 2
            else:
                for i in range(value):
                    if current_y>=height:
                        break
                    if idx+i >= data_len:
                        break
                    if current_x>=width:
                        current_x = 0
                        current_y += 1
                        if current_y >=height:
                            break
                    
                    canvas[current_y,current_x] = encoded_img[idx+i]
                    current_x += 1
                
                idx+=value
                
                if value%2 != 0:
                    idx += 1
        self.cleaned_pixel = canvas # 2-D
        # return canvas.ravel()
        
    def get_cleaned_img(self) -> np.ndarray:
        '''
        直接用上面的 method 取代掉好了
        remove padding: 
            row_padding = ( 4 - ( width % 4 )) % 4
            row_effective_byte = width
            row_bytes_total = row_effective_byte + row_padding
            totla_index = width * heigh
        Args: 2-D np.ndarray from _decompress_rle8()
        Return: np.ndarray, nest value of img in 1-dim.
        '''
        raw_data = self._decompress_rle8()
        width = self.header.biWidth
        heigh = self.header.biHeight

        row_byte = width
        padding = ( 4 - ( width % 4 )) % 4
        
        # check whether padding
        # if true
        #if padding ==0:
         #   return np.frombuffer(self.img,dtype=np.uint8)
        # else
        cleaned_byte = bytearray()
        row_padding = width + padding
        for y in range(heigh):
            start_idx = y*row_padding
            end_idx = start_idx + row_byte
            cleaned_byte.extend(raw_data[start_idx:end_idx])

        return np.frombuffer(cleaned_byte,dtype=np.uint8)


# plot histogram
class PlotHist:
    # 1. 型態轉換：bytes -> ndarray
    # 2. padding 移除
    # 3. 統計次數
    def __init__(self, pixel_bytes, title: str = "Histogram"):
        '''
        Args: 
            pixel_bytes: img 1-D np.ndarray
            width:Bmp width
            height:Bmp height
            title:plot title
        Return: None
        '''
        self.pixel_bytes = pixel_bytes
        self.title = title
        self.hist = None
    
    def _compute_hisogram(self) -> np.ndarray:
        '''
        建立0-255 array，計算每個gray level 出現的次數 for all cleaned_pixel
        Return: 
            np.ndarray: shape(256,), h[i] = gray level i's times 
        '''

        hist = np.zeros(256,dtype=np.int64)

        for i in self.pixel_bytes:
            hist[i] += 1

        self.hist = hist
        return hist
    
    def plot(self,show:bool=True):
        '''
        Args: 
            save_path: save path
            title: plot title
            show: show or not
        Return: plt object
        '''
        # 1. get pixel statistics
        if self.hist is None:
            self._compute_hisogram()
        # 2. fig
        fig, ax = plt.subplots(figsize=(10, 5))
        # 3. plot
        x_axis = np.arange(256)
        ax.bar(x_axis, self.hist, width=1, color='gray', edgecolor='black', alpha=0.8)
        # 4. title
        ax.set_title(self.title, fontsize=14, fontweight='bold')
        ax.set_xlabel("Gray Level (0 = Black, 255 = White)", fontsize=10)
        ax.set_ylabel("Frq. (Num of Pixels)", fontsize=10)
        ax.set_xlim(-0.5, 255.5)
        ax.grid(axis='y', linestyle='--', alpha=0.5)

        plt.tight_layout()

        # 5. save
        fig.savefig(self.title, dpi=300, bbox_inches='tight')
        if show:
            plt.show()

        return fig
        

class Image_processer():
    '''
    *之後使用的時候要注意，因為bmp存檔是從尾，可能要反轉
    Only handle pixel processing logics
    '''
    @staticmethod
    def reduce_gray_level(pixels:np.ndarray,steps:int) -> np.array:
        '''
        Args: pixels 1-D or 2-D
        Return: np.ndarray dtype = np.unit8 , dimension same with input
        '''
        if steps == 1:
            return pixels.copy()
        
        quantization =  (pixels.astype(int) // steps) * steps
        quantization = quantization.astype(np.uint8)
        return quantization
    
    @staticmethod
    def reduce_spacial_level(pixels:np.ndarray,
                             in_width:int,
                             in_height:int,
                             out_width:int,
                             out_height:int) -> np.array:
        '''
        1. 使用affine transfer的方式，用新座標對應舊座標去取value,避免null
        2. 使用pooling的方式，取平均值
        512*512 -> 256*256(2), 128*128(4), 64*64(8), 32*32(16), 16*16(32)

        Args:
            pixels: np.ndarray dtype=np.unit8 2-D
            in_width: original width
            in_height: original height
            out_width: new width
            out_height: new height
        Return: 
            np.ndarray dtype = np.unit8 2-D
        '''
        # 轉2-dim，用新idx去對舊idx後取range
        src_img = np.reshape(pixels.astype(int),(in_height,in_width))
        out_img = np.zeros((out_height,out_width))
        
        x_ratio = in_width / out_width
        y_ratio = in_height / out_height

        # 老師可能不要
        # for y in range(out_height):
        #     for x in range(out_width):
        #         out_img[y,x] = src_img[int(y*y_ratio),int(x*x_ratio)]
        # out_img = out_img.astype(np.uint8)
        # 改用average pooling

        # 2. 改用average pooling
        # 從原圖取框框來average
        for y in range(out_height):
            for x in range(out_width):
                y_start = int(y*y_ratio)
                y_end = int((y+1)*y_ratio)
                x_start = int(x*x_ratio)
                x_end = int((x+1)*x_ratio)

                value = src_img[y_start:y_end,x_start:x_end]
                out_img[y,x] = np.mean(value)
        out_img = out_img.astype(np.uint8)
        return out_img



class BmpWriter():
    '''
    麻煩的來了，有row padding, headerfile renew, bottom up 寫入
    1. padding 要用4 的倍數
    2. headerfile 更新[bfsize,biwidth, biheaght, bicompression, bisizeimage, bixpelspermeter, biypelspermeter]
    3. bottom up 寫入，這個之後再處理，應該是最麻煩的
    
    Args:
        BmpParser: 經過解析的物件
        reduce_gray_level: bool，檔案處理方式
        filename: 輸出檔名
    '''
    def __init__(self,BmpParser,reduce_gray_level:bool,filename:str):       
        '''
        Args: 
            BmpParser: 經過解析的物件
            reduce_gray_level: bool，檔案處理方式
            filename: 輸出檔
        Return: 
            self.cleaned_pixel
        '''
        self.bmpparser = BmpParser
        # 預設灰階模式，只有大小spacial res.需要調大小
        self.mode = reduce_gray_level

        # 新增處理後的clean_pixel 用來作圖 histogram
        self.cleaned_pixel = None

        # info header
        # 修改預設
        self.biCompression = int(0) #no compressed
        self.biXPelsPerMeter = int(0) # by default
        self.biYpelsPerMeter = int(0) # by default
        self.bfSize = None
        self.biSizeImage = None

        self.biWidth = self.bmpparser.header.biWidth
        self.biHeight = self.bmpparser.header.biHeight

        # 保留
        self.bfType = self.bmpparser.header.bfType  # 'BM'
        self.bfOffBits = 1078 # self.bmpparser.header.bfOffBits 理由同下
        self.bfReserved1 = self.bmpparser.header.bfReserved1
        self.bfReserved2 = self.bmpparser.header.bfReserved2
        self.biPlanes = self.bmpparser.header.biPlanes
        self.biBitCount = self.bmpparser.header.biBitCount
        self.biClrUsed = self.bmpparser.header.biClrUsed
        self.biClrImportant = self.bmpparser.header.biClrImportant
        self.biSize = 40 # self.bmpparser.header.biSize 因為原先是壓縮檔，所以大小為124，強制修改

        # color map
        self.color_map = self.bmpparser.color_map

        # img
        self.img = None

        # output file name
        self.filename = filename + ".bmp"

    def padding(self,raw_row_pixel:bytes):
        '''
        Args: 
            raw_row_pixel: 單行像素(byte form)
        Returns:
            padding_row_pixel: padded byte
        '''
        row_len = len(raw_row_pixel)
        padding = ( 4 - row_len % 4 ) % 4
        # 要回傳新的物件，用extend會變None
        return raw_row_pixel + (b'\x00'*padding)
    
    def gray_level_processor(self,Image_processer,steps:int):
        '''
        write to file with padding and calculate img size
        1. get cleaned pixel
        2. quantize pixel
        3. calculate padding
        4. self.header.img
        5. self.header.biSizeImage

        Args: 
            self: BmpParser().cleaned_pixel 2-D
            Image_processer: Image_processer()
            steps: gray level reduction steps
        Return: 
            out_padding_img: img(bytearray)
            img size: biSizeImage
            file size: bfSize
        '''
        out_padding_img = bytearray()

        cleaned_pixel = self.bmpparser.cleaned_pixel
        quantization = Image_processer.reduce_gray_level(cleaned_pixel,steps)
        # for histogram plotting
        self.cleaned_pixel = quantization

        for row in quantization:
            out_padding_img.extend(self.padding(row.tobytes()))
        

        # 因為是灰階處理，所以圖像大小不變
        width = self.biWidth
        height = self.biHeight

        padded_width = width + (4-width%4)%4
        
        self.biSizeImage = padded_width*height
        self.bfSize = self.bfOffBits + self.biSizeImage
        self.img = out_padding_img

        # debug for padding()
        # print(self.img)

    def spacial_level_processor(self,Image_processer,out_width,out_height):
        '''
        write to file with padding and calculate img size
        1. get cleaned pixel
        2. reduce spacial level
        3. calculate padding
        4. self.header.img
        5. self.header.biSizeImage

        Args: 
            BmpParser().cleaned_pixel 2-D
            Image_processer()
        Return: 
            out_padding_img: bytearray
            img size
        '''

        out_padding_img = bytearray()

        cleaned_pixel = self.bmpparser.cleaned_pixel
        quantization = Image_processer.reduce_spacial_level(cleaned_pixel,
                                                            self.biWidth,
                                                            self.biHeight,
                                                            out_width,
                                                            out_height)  
        # for histogram plotting
        self.cleaned_pixel = quantization

        for row in quantization:
            out_padding_img.extend(self.padding(row.tobytes()))
        
        # 更新圖像大小
        self.biWidth = out_width
        self.biHeight = out_height

        width = self.biWidth
        height = self.biHeight
        padded_width = width + (4-width%4)%4
        
        self.biSizeImage = padded_width*height
        self.bfSize = self.bfOffBits + self.biSizeImage
        self.img = out_padding_img
    
    def write_data(self):
        '''
        Functions:
            save bmp file
        Return: 
            None
        '''
        folder_gray = 'gray_level'
        foleder_spacial = 'spacial_level'
        if not os.path.exists(folder_gray):
            os.mkdir(folder_gray)
        if not os.path.exists(foleder_spacial):
            os.mkdir(foleder_spacial)
        if self.mode:
            path = os.path.join(folder_gray,self.filename)
        else:
            path = os.path.join(foleder_spacial,self.filename)

        with open(path,'wb') as f:

            # header file
            # 1. BM
            f.write(self.bfType.to_bytes(2,byteorder='little'))
            # 2. file size
            f.write(self.bfSize.to_bytes(4,byteorder='little'))
            # 3. reserve
            f.write(self.bfReserved1.to_bytes(2,byteorder='little'))
            f.write(self.bfReserved2.to_bytes(2,byteorder='little'))
            # 4. offset
            f.write(self.bfOffBits.to_bytes(4,byteorder="little"))
            # 5. header size
            f.write(self.biSize.to_bytes(4,byteorder="little"))
            # 6. width
            f.write(self.biWidth.to_bytes(4,byteorder="little"))
            # 7. height
            f.write(self.biHeight.to_bytes(4,byteorder="little"))
            # 8. plane
            f.write(self.biPlanes.to_bytes(2,byteorder="little"))
            # 9. bit count
            f.write(self.biBitCount.to_bytes(2,byteorder="little"))
            # 10. compression
            f.write(self.biCompression.to_bytes(4,byteorder="little"))
            # 11 image size
            f.write(self.biSizeImage.to_bytes(4,byteorder="little"))          
            # 12. pixel per meter(x)
            f.write(self.biXPelsPerMeter.to_bytes(4,byteorder="little"))
            # 13. pixel per meter(y)
            f.write(self.biYpelsPerMeter.to_bytes(4,byteorder="little"))            
            # 14 color used
            f.write(self.biClrUsed.to_bytes(4,byteorder="little"))            
            # 15 color important
            f.write(self.biClrImportant.to_bytes(4,byteorder="little"))

            # coler map 不需要沿用原壓縮檔的位置，直接使用54就好
            f.seek(54)

            # self.new_color_map = bytearray(1024) # 創建一個 1024 bytes 的 bytearray
            # for i in range(256):
            #     self.new_color_map[i*4] = i      # Blue
            #     self.new_color_map[i*4+1] = i    # Green
            #     self.new_color_map[i*4+2] = i    # Red
            #     self.new_color_map[i*4+3] = 0    # Reserved
            # print(self.new_color_map == self.color_map)
            # color map 沒錯啊
            f.write(self.color_map)
            
            # img
            f.write(self.img)

            # print all header
            # print("bfType:",self.bfType.to_bytes(2,byteorder='little'),len(self.bfType.to_bytes(2,byteorder='little')))
            # print("bfSize:",self.bfSize.to_bytes(4,byteorder='little'),len(self.bfSize.to_bytes(4,byteorder='little')))
            # print("bfReserved1:",self.bfReserved1.to_bytes(2,byteorder='little'),len(self.bfReserved1.to_bytes(2,byteorder='little')))
            # print("bfReserved2:",self.bfReserved2.to_bytes(2,byteorder='little'),len(self.bfReserved2.to_bytes(2,byteorder='little')))
            # print("bfOffBits:",self.bfOffBits.to_bytes(4,byteorder="little"),len(self.bfOffBits.to_bytes(4,byteorder="little")))

            # print("biSize:",self.biSize.to_bytes(4,byteorder="little"),len(self.biSize.to_bytes(4,byteorder="little")))
            # print("biWidth:",self.biWidth.to_bytes(4,byteorder="little"),len(self.biWidth.to_bytes(4,byteorder="little")))
            # print("biHeight:",self.biHeight.to_bytes(4,byteorder="little"),len(self.biHeight.to_bytes(4,byteorder="little")))
            # print("biPlanes:",self.biPlanes.to_bytes(2,byteorder="little"),len(self.biPlanes.to_bytes(2,byteorder="little")))
            # print("biBitCount:",self.biBitCount.to_bytes(2,byteorder="little"),len(self.biBitCount.to_bytes(2,byteorder="little")))
            # print("biCompression",self.biCompression.to_bytes(4,byteorder="little"),len(self.biCompression.to_bytes(4,byteorder="little")))
            # print("biSizeImage:",self.biSizeImage.to_bytes(4,byteorder="little"),len(self.biSizeImage.to_bytes(4,byteorder="little")))
            # print("biXPelsPerMeter",self.biXPelsPerMeter.to_bytes(4,byteorder="little"),len(self.biXPelsPerMeter.to_bytes(4,byteorder="little")))
            # print("biYpelsPerMeter:",self.biYpelsPerMeter.to_bytes(4,byteorder="little"),len(self.biYpelsPerMeter.to_bytes(4,byteorder="little"))) 
            # print("biClrUsed:",self.biClrUsed.to_bytes(4,byteorder="little"),len(self.biClrUsed.to_bytes(4,byteorder="little")))            
            # print("biClrImportant:",self.biClrImportant.to_bytes(4,byteorder="little"),len(self.biClrImportant.to_bytes(4,byteorder="little")))
            # print(len(self.color_map))

        

# class main()

'''
Debug
1. histogram
2. gray level
3. spacial level
4. bmpwriter
    gray level
    spacial level
'''

# import matplotlib.pyplot as plt
# lena = BmpParser('data/lena.bmp')

# histogram
# plot = PlotHist(lena.cleaned_pixel.ravel(),title="lena")
# plot.plot(save_path='data/lena_hist.png')

# gray level
# parser = Image_processer()
# fig, axes = plt.subplots(2, 4, figsize=(16, 8))
# axes = axes.flat

# for i in range(1, 9):
#     steps = 2**i
#     new_img = parser.reduce_gray_level(lena.cleaned_pixel, steps=steps)
#     new_img = np.flipud(new_img)
#     num_levels = 256 // steps
#     ax = axes[i-1]
#     ax.imshow(new_img, cmap='gray', vmin=0, vmax=255)
#     ax.set_title(f'Gray Levels: {num_levels}')
#     ax.axis('off')
# plt.tight_layout()
# plt.savefig('lena_gray_levels.png', dpi=300, bbox_inches='tight')
# plt.show()


# spacial level $$256*256、128*128、64*64、32*32、16*16$
# parser = Image_processer()
# fig, axes = plt.subplots(2, 3, figsize=(16, 8))
# axes = axes.flat

# for i in range(1, 7):
#     size = 2**(i+3)
#     new_img = parser.reduce_spacial_level(lena.cleaned_pixel,
#                                             lena.header.biWidth,
#                                             lena.header.biHeight,
#                                             size,size)
#     new_img = np.flipud(new_img)
#     num_levels = size
#     ax = axes[i-1]
#     ax.imshow(new_img, cmap='gray', vmin=0, vmax=255)
#     ax.set_title(f'Gray Levels: {num_levels}')
#     ax.axis('off')
# plt.tight_layout()
# plt.savefig('lena_spacial_levels.png', dpi=300, bbox_inches='tight')
# plt.show()

# bmpwriter

# writer = BmpWriter(lena,reduce_gray_level=False,filename='spacial_64')
# parser = Image_processer()

# gray level
# writer.gray_level_processor(parser,steps=64)
# writer.write_data()

# 出事了，開出來全黑，看看padding()跟write_data()
# padding() 看起來沒事
# file header 也處理為壓縮檔的格式問題， 但還是黑畫面，再看看是不是color map的問題，很好也不是
# 最後原因是因為寫入color map的時候誤用bioffbits作為寫入位置，但其含義為strating of raw img data
# 不管steps設定多少，輸出的gray level似乎都沒有改變 要改2的指數次方

# writer.spacial_level_processor(parser,out_width=64,out_height=64)
# writer.write_data()

if __name__ == '__main__':
    '''
    先產生灰階圖像
    再產生縮放大小圖像
    只後把所有檔案放入plot histogram()中畫出
    '''
    lena = BmpParser('data/lena.bmp')
    parser = Image_processer()
    gray_hist = 'gray_level/hist'
    spacial_hist = 'spacial_level/hist'
    if not os.path.exists(gray_hist):
        os.mkdir(gray_hist)
    if not os.path.exists(spacial_hist):
        os.mkdir(spacial_hist)

    # gray level reduce from 512 to 1
    for i in range(0, 9):
        steps = 2**i
        filename = f'gray_level_steps{i}'
        writer = BmpWriter(lena,reduce_gray_level=True,filename=filename)
        writer.gray_level_processor(parser,steps=steps)
        writer.write_data()

        path = os.path.join(gray_hist,filename)
        pixel = writer.cleaned_pixel
        Plot = PlotHist(pixel.ravel(),path)
        Plot.plot()
        
    
    # spacial level reduce
    for i in range(1,10):
        size = 2**i
        filename = f'spacial_level_size{size}x{size}'
        writer = BmpWriter(lena,reduce_gray_level=False,filename=filename)
        writer.spacial_level_processor(parser,out_width=size,out_height=size)
        writer.write_data()

        path = os.path.join(spacial_hist,filename)
        pixel = writer.cleaned_pixel
        Plot = PlotHist(pixel.ravel(),path)
        Plot.plot()
    