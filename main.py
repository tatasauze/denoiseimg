#%%
import random
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
import matplotlib
from HW1 import *

def normal_gaussina_noise():
    '''
    method by box muller
    Returns:
        2 normal Gaussian var.
    '''
    U1 = random.random()
    U2 = random.random()
    Z1 = np.sqrt(-2*np.log(U1))*np.cos(2*np.pi*U2)
    Z2 = np.sqrt(-2*np.log(U1))*np.sin(2*np.pi*U2)
    return Z1


def add_noise(img:np.ndarray,mean:int,sigma:int):
    '''
    Args:
        img: np.ndarray
        noise_type: str
        mean: int
        sigma: int
    Returns:
        img: np.ndarray dtype=np.float32
    '''
    img.astype(np.float32)
    mean = float(mean)
    sigma = float(sigma)
    func = np.vectorize(lambda x:x+(mean+normal_gaussina_noise()*sigma))
    noise_img = func(img)
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
        kernel = np.ones((kernel_size,kernel_size))
        average_scale = kernel_size**2
        out_img = np.zeros(img.shape)

        # padding with 0 on marginal
        width = img.shape[1]
        stride = 1
        padding = (kernel_size-1)//2

        pad_img = np.pad(img,pad_width=padding,mode='constant',constant_values=0)
        out_img = np.zeros(img.shape)
        
        kernel = kernel/average_scale
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                window = pad_img[i:i+kernel_size,j:j+kernel_size]
                out_img[i,j] = np.sum(window*kernel)
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
        kernel = np.array([[-1,0,1],[-2,0,2],[-1,0,1]])
        kernel_size = kernel.shape[0]
        pad = (kernel_size-1)//2
        out_img = np.zeros(img.shape)
        pad_img = np.pad(img,pad_width=pad,mode="constant",constant_values=0)
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                window = pad_img[i:i+kernel_size,j:j+kernel_size]
                out_img[i,j] = np.sum(window*kernel)
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
        kernel = np.ones((kernel_size,kernel_size))
        padding = (kernel_size-1)//2
        out_img = np.zeros(img.shape)
        # replication padding
        pad_img = np.pad(img,pad_width=padding,mode='edge')
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                window = pad_img[i:i+kernel_size,j:j+kernel_size]
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

        #1 1-D 
        ax = np.arange(-kernel_size//2+1,kernel_size//2+1)
        #2 2-D
        xx,yy = np.meshgrid(ax,ax)
        #3 gaussian
        kernel = np.exp(-0.5*(np.square(xx)+np.square(yy))/np.square(sigma))
        kernel = kernel/np.sum(kernel)

        pad_img = (kernel_size-1)//2
        out_img = np.zeros(img.shape)
        pad_img = np.pad(img,pad_width=pad_img,mode='reflect')
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                window = pad_img[i:i+kernel_size,j:j+kernel_size]
                out_img[i,j] = np.sum(window*kernel)
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
        
        # gaussian filter
        ax = np.arange(-kernel_size//2+1,kernel_size//2+1)
        xx,yy = np.meshgrid(ax,ax)
        spacial_kernel = np.exp(-0.5*(np.square(xx)+np.square(yy))/np.square(distance_sigma))
        spacial_kernel = spacial_kernel/np.sum(spacial_kernel)

        # pag img reflect
        padding = (kernel_size-1)//2
        pad_img = np.pad(img,pad_width=padding,mode='reflect')
        
        # outimg
        out_img = np.zeros(img.shape)
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                
                window = pad_img[i:i+kernel_size,j:j+kernel_size]
                
                # centeral coordinate 每個位置減去中心像素平方
                center_pixel = window[padding,padding]
                range_diff = np.square(window-center_pixel)

                range_kernel = np.exp(-0.5*range_diff/np.square(range_sigma))

                combined_kernel = spacial_kernel*range_kernel
                combined_kernel = combined_kernel/np.sum(combined_kernel)
                out_img[i,j] = np.sum(window*combined_kernel)
            
        return out_img

if __name__ == "__main__":

    # load bmp img
    lena = BmpParser("filtered_img/lena.bmp")
    img = np.flipud(lena.cleaned_pixel)

    # add noise
    noised_img = add_noise(img,mean=0,sigma=10)

    # setup imgprocessor object
    img_procssor = Image_filter(noised_img)
    out_dir = 'filtered_img'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # basic plot function
    def plot_img(dir:str,file_name:str,img:np.ndarray):
        if not os.path.exists(dir):
            os.mkdir(dir)
        fig = plt.figure(figsize=(8, 8), dpi=500)
        plt.imshow(img, cmap='gray')
        plt.title(file_name, fontsize=16)
        plt.axis('off')
        file_path = os.path.join(dir,file_name+'.png')
        plt.savefig(file_path, bbox_inches='tight', pad_inches=0.1)
        plt.show()
        plt.close(fig)

    # all kinds of processsor

    # average_img = img_procssor.mean_val_filter(3)
    # sobel_img = img_procssor.sobel_filter()
    # median_img = img_procssor.median_filter(3)
    # gaussian_img = img_procssor.gaussian_filter(kernel_size=3,sigma=5)
    # PNG
    # images_to_save = {
    #     "noised": noised_img,
    #     "average_filter": average_img,
    #     "sobel_filter": sobel_img,
    #     "median_filter": median_img,
    #     "gaussian_filter": gaussian_img,
    #     "bilateral_filter": bilateral_img
    # }    

    def plot_bilateral():
        out_dir = "filtered_img/bilateral"
        spacial_sigmas = [i for i in range(5,51,5)]
        range_sigmas = [i for i in range(5,51,5)]
        for spacial_sigma in spacial_sigmas:
            for range_sigma in range_sigmas:
                bilateral_img = img_procssor.bilateral_filter(kernel_size=3,
                                                            distance_sigma=spacial_sigma,
                                                            range_sigma=range_sigma)    
                plot_img(dir=out_dir,file_name=f"bilateral_G{spacial_sigma}_R_{range_sigma}",img=bilateral_img)
    plot_bilateral()