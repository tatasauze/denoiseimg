import random
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
import matplotlib
from HW1 import *

def normal_gaussina_noise(seed=np.random.default_rng(64)):
    '''
    method by box muller
    Returns:
        1 gaussian var.
    '''
    seed = seed
    U1 = random.random()
    U2 = random.random()
    Z1 = np.sqrt(-2*np.log(U1))*np.cos(2*np.pi*U2)
    Z2 = np.sqrt(-2*np.log(U1))*np.sin(2*np.pi*U2)
    return Z1


def add_noise(img:np.ndarray, mean:int, sigma:int):
    '''
    Args:
        img: np.ndarray (grayscale or RGB)
        mean: int  mean of gaussian noise
        sigma: int  standard deviation of gaussian noise
    Returns:
        noise_img: np.ndarray dtype=np.float32
    '''
    img = img.astype(np.float32)
    mean = float(mean)
    sigma = float(sigma)
    
    # gen. noise for each pixel and channel
    noise = np.zeros_like(img, dtype=np.float32)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if len(img.shape) == 3:  # RGB
                for k in range(img.shape[2]):
                    noise[i, j, k] = mean + normal_gaussina_noise() * sigma
            else:  # grayscale
                noise[i, j] = mean + normal_gaussina_noise() * sigma
    
    noise_img = img + noise
    return noise_img.astype(np.float32)


class Image_filter:
    def __init__(self,img:np.ndarray):
        self.img = img

    def mean_val_filter(self,kernel_size:int)-> np.ndarray:
        '''
        stride = 1 , same padding
        Args:
            kernel_size: int
            in_img: np.ndarray
        Returns:
            out_img: np.ndarray
        '''
        img = self.img
        
        # check if RGB (3 channels) or grayscale
        if len(img.shape) == 3:  # RGB
            out_img = np.zeros_like(img)
            for c in range(img.shape[2]):  # process each channel
                out_img[:,:,c] = self._apply_mean_filter(img[:,:,c], kernel_size)
            return out_img
        else:  # grayscale
            return self._apply_mean_filter(img, kernel_size)
    
    def _apply_mean_filter(self, img_2d:np.ndarray, kernel_size:int) -> np.ndarray:
        '''apply mean filter on 2D grayscale image'''
        kernel = np.ones((kernel_size,kernel_size))
        average_scale = kernel_size**2
        padding = (kernel_size-1)//2
        
        pad_img = np.pad(img_2d, pad_width=padding, mode='constant', constant_values=0)
        out_img = np.zeros_like(img_2d)
        
        kernel = kernel / average_scale
        for i in range(img_2d.shape[0]):
            for j in range(img_2d.shape[1]):
                window = pad_img[i:i+kernel_size, j:j+kernel_size]
                out_img[i,j] = np.sum(window * kernel)
        return out_img

    def sobel_filter(self):
        '''
        stride = 1 , same padding
        Args:
            img: np.ndarray
        Returns:
            img: np.ndarray
        '''
        img = self.img
        
        # check if RGB (3 channels) or grayscale
        if len(img.shape) == 3:  # RGB
            out_img = np.zeros_like(img)
            for c in range(img.shape[2]):  # process each channel
                out_img[:,:,c] = self._apply_sobel(img[:,:,c])
            return out_img
        else:  # grayscale
            return self._apply_sobel(img)
    
    def _apply_sobel(self, img_2d:np.ndarray) -> np.ndarray:
        '''apply sobel filter on 2D grayscale image'''
        kernel = np.array([[-1,0,1],[-2,0,2],[-1,0,1]])
        kernel_size = kernel.shape[0]
        pad = (kernel_size-1)//2
        
        out_img = np.zeros_like(img_2d)
        pad_img = np.pad(img_2d, pad_width=pad, mode="constant", constant_values=0)
        for i in range(img_2d.shape[0]):
            for j in range(img_2d.shape[1]):
                window = pad_img[i:i+kernel_size, j:j+kernel_size]
                out_img[i,j] = np.sum(window * kernel)
        return out_img
    def prewitt(self):
        '''
        stride = 1 , same padding
        Args:
            img: np.ndarray
        Returns:
            img: np.ndarray
        '''
        img = self.img
        
        # check if RGB (3 channels) or grayscale
        if len(img.shape) == 3:  # RGB
            out_img = np.zeros_like(img)
            for c in range(img.shape[2]):  # process each channel
                out_img[:,:,c] = self._apply_prewitt(img[:,:,c])
            return out_img
        else:  # grayscale
            return self._apply_prewitt(img)
        
    def _apply_prewitt(self, img_2d:np.ndarray):
        '''apply prewitt filter on 2D grayscale image'''
        kernel_x = np.array([[-1,0,1],[-1,0,1],[-1,0,1]])
        kernel_y = np.array([[1,1,1],[0,0,0],[-1,-1,-1]])
        kernel_size = kernel.shape[0]
        pad = (kernel_size-1)//2
        
        out_img_x = np.zeros_like(img_2d)
        out_img_y = np.zeros_like(img_2d)
        
        pad_img = np.pad(img_2d, pad_width=pad, mode="constant", constant_values=0)
        for i in range(img_2d.shape[0]):
            for j in range(img_2d.shape[1]):
                window = pad_img[i:i+kernel_size, j:j+kernel_size]
                out_img_y[i,j] = np.sum(window * kernel_y)
                out_img_x[i,j] = np.sum(window * kernel_x)
        
        out_img = np.sqrt(np.square(out_img_x) + np.square(out_img_y))
        return out_img
    
    def derived_vertical(self):
        '''
        stride = 1 , same padding
        Args:
            img: np.ndarray
        Returns:
            img: np.ndarray
        '''
        img = self.img
        
        # check if RGB (3 channels) or grayscale
        if len(img.shape) == 3:  # RGB
            out_img = np.zeros_like(img)
            for c in range(img.shape[2]):  # process each channel
                out_img[:,:,c] = self._apply_derived_vertical(img[:,:,c])
            return out_img
        else:  # grayscale
            return self._apply_derived_vertical(img)
    
    def _apply_derived_vertical(self, img_2d:np.ndarray) -> np.ndarray:
        '''apply sobel filter on 2D grayscale image'''
        kernel = np.array([[0,0,0],[-1,1,0],[0,0,0]])
        kernel_size = kernel.shape[0]
        pad = (kernel_size-1)//2
        
        out_img = np.zeros_like(img_2d)
        pad_img = np.pad(img_2d, pad_width=pad, mode="constant", constant_values=0)
        for i in range(img_2d.shape[0]):
            for j in range(img_2d.shape[1]):
                window = pad_img[i:i+kernel_size, j:j+kernel_size]
                out_img[i,j] = np.sum(window * kernel)
        return out_img

    def derived_horizental(self):
        '''
        stride = 1 , same padding
        Args:
            img: np.ndarray
        Returns:
            img: np.ndarray
        '''
        img = self.img
        
        # check if RGB (3 channels) or grayscale
        if len(img.shape) == 3:  # RGB
            out_img = np.zeros_like(img)
            for c in range(img.shape[2]):  # process each channel
                out_img[:,:,c] = self._apply_derived_horizental(img[:,:,c])
            return out_img
        else:  # grayscale
            return self._apply_derived_horizental(img)
    
    def _apply_derived_horizental(self, img_2d:np.ndarray) -> np.ndarray:
        '''apply sobel filter on 2D grayscale image'''
        kernel = np.array([[0,1,0],[0,-1,0],[0,0,0]])
        kernel_size = kernel.shape[0]
        pad = (kernel_size-1)//2
        
        out_img = np.zeros_like(img_2d)
        pad_img = np.pad(img_2d, pad_width=pad, mode="constant", constant_values=0)
        for i in range(img_2d.shape[0]):
            for j in range(img_2d.shape[1]):
                window = pad_img[i:i+kernel_size, j:j+kernel_size]
                out_img[i,j] = np.sum(window * kernel)
        return out_img


    def median_filter(self,kernel_size:int):
        '''
        stride = 1 , same padding
        Args:
            kernel_size: int
            in_img: np.ndarray
        Returns:
            out_img: np.ndarray
        '''
        img = self.img
        
        # check if RGB (3 channels) or grayscale
        if len(img.shape) == 3:  # RGB
            out_img = np.zeros_like(img)
            for c in range(img.shape[2]):  # process each channel
                out_img[:,:,c] = self._apply_median(img[:,:,c], kernel_size)
            return out_img
        else:  # grayscale
            return self._apply_median(img, kernel_size)
    
    def _apply_median(self, img_2d:np.ndarray, kernel_size:int) -> np.ndarray:
        '''apply median filter on 2D grayscale image'''
        padding = (kernel_size-1)//2
        out_img = np.zeros_like(img_2d)
        # replication padding
        pad_img = np.pad(img_2d, pad_width=padding, mode='edge')
        for i in range(img_2d.shape[0]):
            for j in range(img_2d.shape[1]):
                window = pad_img[i:i+kernel_size, j:j+kernel_size]
                out_img[i,j] = np.median(window)
        return out_img

    def gaussian_filter(self,kernel_size:int,sigma:int):
        '''
        stride = 1 , same padding
        Args:
            kernel_size: 奇數大小
            in_img: np.ndarray
        Returns:
            out_img: np.ndarray
        '''
        img = self.img
        
        # check if RGB (3 channels) or grayscale
        if len(img.shape) == 3:  # RGB
            out_img = np.zeros_like(img)
            for c in range(img.shape[2]):  # process each channel
                out_img[:,:,c] = self._apply_gaussian(img[:,:,c], kernel_size, sigma)
            return out_img
        else:  # grayscale
            return self._apply_gaussian(img, kernel_size, sigma)
    
    def _apply_gaussian(self, img_2d:np.ndarray, kernel_size:int, sigma:int) -> np.ndarray:
        '''apply gaussian filter on 2D grayscale image'''
        # 1-D
        ax = np.arange(-kernel_size//2+1, kernel_size//2+1)
        # 2-D
        xx,yy = np.meshgrid(ax,ax)
        # 3 gaussian kernel
        kernel = np.exp(-0.5*(np.square(xx)+np.square(yy))/np.square(sigma))
        kernel = kernel/np.sum(kernel)
        
        pad_size = (kernel_size-1)//2
        out_img = np.zeros_like(img_2d)
        pad_img = np.pad(img_2d, pad_width=pad_size, mode='reflect')
        for i in range(img_2d.shape[0]):
            for j in range(img_2d.shape[1]):
                window = pad_img[i:i+kernel_size, j:j+kernel_size]
                out_img[i,j] = np.sum(window * kernel)
        return out_img

    def bilateral_filter(self,kernel_size:int,distance_sigma:int,range_sigma:int):
        '''
        stride 1 , same padding
        Args:
            kernel_size: int
            in_img: np.ndarray
            distance_sigma: 高斯濾波標準差
            range_sigma: 像素色差標準差
        Returns:
            out_img: np.ndarray
        '''
        img = self.img
        
        # check if RGB (3 channels) or grayscale
        if len(img.shape) == 3:  # RGB
            out_img = np.zeros_like(img)
            for c in range(img.shape[2]):  # process each channel
                out_img[:,:,c] = self._apply_bilateral(img[:,:,c], kernel_size, distance_sigma, range_sigma)
            return out_img
        else:  # grayscale
            return self._apply_bilateral(img, kernel_size, distance_sigma, range_sigma)
    
    def _apply_bilateral(self, img_2d:np.ndarray, kernel_size:int, distance_sigma:int, range_sigma:int) -> np.ndarray:
        '''apply bilateral filter on 2D grayscale image'''
        # gaussian filter
        ax = np.arange(-kernel_size//2+1, kernel_size//2+1)
        xx,yy = np.meshgrid(ax,ax)
        spacial_kernel = np.exp(-0.5*(np.square(xx)+np.square(yy))/np.square(distance_sigma))
        spacial_kernel = spacial_kernel/np.sum(spacial_kernel)
        
        # pad img reflect
        padding = (kernel_size-1)//2
        pad_img = np.pad(img_2d, pad_width=padding, mode='reflect')
        
        # outimg
        out_img = np.zeros_like(img_2d)
        for i in range(img_2d.shape[0]):
            for j in range(img_2d.shape[1]):
                window = pad_img[i:i+kernel_size, j:j+kernel_size]
                
                # centeral coordinate 每個位置減去中心像素平方
                center_pixel = window[padding,padding]
                range_diff = np.square(window - center_pixel)
                
                range_kernel = np.exp(-0.5*range_diff/np.square(range_sigma))
                
                combined_kernel = spacial_kernel * range_kernel
                combined_kernel = combined_kernel / np.sum(combined_kernel)
                out_img[i,j] = np.sum(window * combined_kernel)
        
        return out_img

# basic plot function
def plot_img(dir:str, file_name:str, img:np.ndarray):
    if not os.path.exists(dir):
        os.mkdir(dir)

    # normalize to 0-255 for display (preserve relative contrast)
    img_min = np.min(img)
    img_max = np.max(img)
    
    if img_max - img_min > 0:
        img_display = ((img - img_min) / (img_max - img_min) * 255).astype(np.uint8)
    else:
        img_display = np.zeros_like(img, dtype=np.uint8)
    
    fig = plt.figure(figsize=(8, 8), dpi=500)

    # check if RGB or grayscale
    if len(img_display.shape) == 3 and img_display.shape[2] in [3, 4]: # alpha
        plt.imshow(img_display)
    else:
        plt.imshow(img_display, cmap='gray')  # grayscale

    plt.title(file_name, fontsize=16)
    plt.axis('off')
    file_path = os.path.join(dir, file_name+'.png')
    plt.savefig(file_path, bbox_inches='tight', pad_inches=0.1)
    plt.show()
    plt.close(fig)

if __name__ == "__main__":

    # =======================================
    # load bmp img lena
    # lena = BmpParser("filtered_img/lena.bmp")
    # img = np.flipud(lena.cleaned_pixel)


    # add noise and save as png
    # noise = [4,2,1,0.5,0.1,0.01]
    # for i in range(len(noise)):
    #     noised_img = add_noise(img,0,noise[i])
    #     plot_img(dir="filtered_img/noised",file_name=f"noised_{noise[i]}",img=noised_img)
    #     np.save(f"filtered_img/noised/noised_{noise[i]}.npy",noised_img)
    
    # sigma set 40 to try extreme
    # noised_img = add_noise(img,0,40)
    # plot_img(dir="filtered_img/noised",file_name=f"noised_40",img=noised_img)
    # minus_img = img-noised_img
    # plot_img(dir="filtered_img/minus",file_name=f"minus_40",img=minus_img)
        

    # load noised img and minus original img
    # root_dir = 'filtered_img/noised'
    # files = os.listdir(root_dir)
    # files = [i for i in files if i.endswith('.npy')]
    # files.sort()

    # if not os.path.exists("filtered_img/minus"):
    #     os.mkdir("filtered_img/minus")
    # for i in files:
    #     noised_img = np.load(os.path.join(root_dir,i))
    #     minus_img = img-noised_img
    #     plot_img(dir="filtered_img/minus",file_name=f"minus_{i}",img=minus_img)
        
    # =====================================
    # coin img
    # add noise and save as png
    # img = plt.imread('coin_1.png')
    # noise = [4,2,1,0.5,0.1,0.01]
    # for i in range(len(noise)):
    #     noised_img = add_noise(img,0,noise[i])
    #     plot_img(dir="filtered_img/noised/coin",file_name=f"noised_{noise[i]}",img=noised_img)
    #     np.save(f"filtered_img/noised/coin/noised_{noise[i]}.npy",noised_img)

    # setup imgprocessor object
    lena_noise = np.load('filtered_img/noised/noised_4.npy')
    coin_noise = np.load('filtered_img/noised/coin/noised_0.01.npy')

    img_procssor_lena = Image_filter(lena_noise)
    img_procssor_coin = Image_filter(coin_noise)
    out_dir = 'filtered_img/denoise_lena'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # all kinds of processsor
    img_procssor = img_procssor_lena
    average_img = img_procssor.mean_val_filter(3)
    sobel_img = img_procssor.sobel_filter()
    median_img = img_procssor.median_filter(3)
    gaussian_img = img_procssor.gaussian_filter(kernel_size=3,sigma=0.01)
    
    # save as np
    np.save(f"{out_dir}/average_filter.npy",average_img)
    np.save(f"{out_dir}/sobel_filter.npy",sobel_img)
    np.save(f"{out_dir}/median_filter.npy",median_img)
    np.save(f"{out_dir}/gaussian_filter.npy",gaussian_img)


    # PNG
    # images_to_save = {
    #     "noised": noised_img,
    #     "average_filter": average_img,
    #     "sobel_filter": sobel_img,
    #     "median_filter": median_img,
    #     "gaussian_filter": gaussian_img,
    #     "bilateral_filter": bilateral_img
    # }    

    def plot_bilateral(dir,img_procssor):
        spacial_sigmas = [i for i in range(1,6,5)]
        range_sigmas = [i for i in range(1,6,5)]
        for spacial_sigma in spacial_sigmas:
            for range_sigma in range_sigmas:
                bilateral_img = img_procssor.bilateral_filter(kernel_size=3,
                                                            distance_sigma=spacial_sigma,
                                                            range_sigma=range_sigma)
                np.save(f"{dir}/bilateral_G{spacial_sigma}_R_{range_sigma}.npy",bilateral_img) 
                plot_img(dir=out_dir,file_name=f"bilateral_G{spacial_sigma}_R_{range_sigma}",img=bilateral_img)
    plot_img(dir=out_dir,file_name="average_filter",img=average_img)
    plot_img(dir=out_dir,file_name="median_filter",img=median_img)
    plot_img(dir=out_dir,file_name="gaussian_filter",img=gaussian_img)
    plot_bilateral(dir=out_dir,img_procssor=img_procssor_coin)