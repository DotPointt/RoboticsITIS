import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

try:
    import tkinter
    print("Tkinter установлен")
except ImportError:
    print("Tkinter не установлен")


def show_images(original, blurred, edges, sharpened, combined): 
    plt.figure(figsize=(12, 10)) 
    plt.subplot(2, 3, 1) 
    plt.title('Оригинальное изображение') 
    plt.imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB)) 
    plt.axis('off') 
    plt.subplot(2, 3, 2) 
    plt.title('Размытие по Гауссу)') 
    plt.imshow(cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB)) 
    plt.axis('off') 
    plt.subplot(2, 3, 3) 
    plt.title('Выделение границ') 
    plt.imshow(cv2.cvtColor(edges, cv2.COLOR_BGR2RGB)) 
    plt.axis('off') 
    plt.subplot(2, 3, 4) 
    plt.title('Повышение резкости') 
    plt.imshow(cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB)) 
    plt.axis('off') 
    plt.subplot(2, 3, 5) 
    plt.title('Комбинация изображений') 
    plt.imshow(cv2.cvtColor(combined, cv2.COLOR_BGR2RGB)) 
    plt.axis('off') 
    plt.tight_layout() 
    plt.show() 

matplotlib.use('TkAgg')

image = cv2.imread('items.JPG')

blurred_image = cv2.GaussianBlur(image, (27, 27), 0)

kernel = np.array([[0, -1, 0], 
[-1, 5, -1], 
[0, -1, 0]]) 
sharpened = cv2.filter2D(image, -1, kernel) 

# альтернативный вариант:
# blurred = cv2.GaussianBlur(image, (5, 5), 0)  
# sharpened = cv2.addWeighted(image, 1.5, blurred, -0.5, 0)

edges = cv2.Sobel(image, cv2.CV_16S, 1, 0, ksize=3, scale=1, delta=0, 
borderType=cv2.BORDER_DEFAULT) 
edges = cv2.convertScaleAbs(edges)

combined = cv2.addWeighted(blurred_image, 0.2, edges, 0.8, 0)   
combined = cv2.addWeighted(combined, 0.5, sharpened, 0.5, 0)

screen_width, screen_height = 500, 500  
image = cv2.resize(combined, (screen_width, screen_height), interpolation=cv2.INTER_AREA)


show_images(image, blurred_image, edges, sharpened, combined)
# cv2.imshow('orig_image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

