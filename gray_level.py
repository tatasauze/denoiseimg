import numpy as np
import matplotlib
import matplotlib.pyplot as plt
img = plt.imread('filtered_img/coin_1.png')
gray_channel_img = np.mean(img,axis=2)

# save to png
plt.imsave('filtered_img/coin_graylevel.png',gray_channel_img,cmap='gray')

#