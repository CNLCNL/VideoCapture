import cv2, numpy as np  # OpenCV
from tqdm import tqdm

def ON_EVENT_LBUTTONDOWN(event, x, y, flags, param):
    img = param["image"] # 传进图片参数
    if event == cv2.EVENT_LBUTTONDOWN:
        xy = "%d,%d" % (x, y)
        print(x, y)
        cv2.circle(img, (x, y), 2, (0, 0, 255))
        cv2.putText(img, xy, (x, y), cv2.FONT_HERSHEY_PLAIN,1.0, (0,0,255)) # 把坐标画在图片上
        cv2.imshow("image", img)

def Get_Position(filedir):
    """
        获取图片位置函数:  
        filedir: 视频原文件路径 
    """
    img = cv2.imread(filedir)
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("image", ON_EVENT_LBUTTONDOWN, {"image": img})
    while(1):
        cv2.imshow("image", img)
        key = cv2.waitKey(2) & 0xFF
        if key == ord('q'): # 按q则退出图片展示
            break
    cv2.destroyAllWindows()

def Get_Video_Image(filedir, savedir = None, second = None):
    """
        截取视频一帧图片函数:  
        filedir: 视频原文件路径   
        savedir: 剪辑视频文件保存路径, 若不保存则返回图片  
        second: 截取第几秒的图片  
    """
    cap = cv2.VideoCapture(filedir)  # 打开视频文件
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)  # 获得视频文件的帧数
    fps = cap.get(cv2.CAP_PROP_FPS)  # 获得视频文件的帧率
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # 获得视频文件的帧宽
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # 获得视频文件的帧高
    second = 0 if second is None else second
    for pos in tqdm(range(int(second*fps))):
        ret, frame = cap.read()  # 捕获一帧图像

    cap.release()
    if savedir is not None:
        cv2.imwrite(savedir, frame)
    return frame

INPUT_DIR1 = "C:/Users/10790/Desktop/bilibili_video/疏远.mp4"
OUTPUT_DIR1 = "C:/Users/10790/Desktop/bilibili_video/capture1.jpg"
MASK_DIR1 = "C:/Users/10790/Desktop/bilibili_video/mask1.jpg"

INPUT_DIR2 = "C:/Users/10790/Desktop/bilibili_video/敢杀我的马.mp4"
OUTPUT_DIR2 = "C:/Users/10790/Desktop/bilibili_video/capture2.jpg"
MASK_DIR2 = "C:/Users/10790/Desktop/bilibili_video/mask2.jpg"

Get_Video_Image(INPUT_DIR1, OUTPUT_DIR1, 4) # 截取第4s的图片
Get_Position(OUTPUT_DIR1) # 得到水印的位置(行列)

Get_Video_Image(INPUT_DIR2, OUTPUT_DIR2, 8) # 截取第8s的图片
Get_Position(OUTPUT_DIR2) # 得到水印的位置(行列)

image = cv2.imread(OUTPUT_DIR1)
image_new = image.copy() # 复制一张相同规格的图片
image_new.fill(255) # 空白图片
for row in range(23, 70): # 水印行从23到70
    for col in range(974, 1259): # 水印列从974到1259
        if image[row][col][0] > 60: # 通过观察发现水印的R像素大于60, 水印位置多扩大点没事, 尽量覆盖
            image_new[row][col] = np.array([0, 0, 0])
cv2.imwrite(MASK_DIR1, image_new)

image = cv2.imread(OUTPUT_DIR2)
image_new = image.copy() # 复制一张相同规格的图片
image_new.fill(255) # 空白图片
for row in range(115, 178): # 水印行从115到178
    for col in range(135, 369): # 水印列从135到369
        if image[row][col][0] > 195 and image[row][col][1] > 195 and image[row][col][2] > 195: # 通过观察发现水印的RGB像素大于195, 水印位置多扩大点没事, 尽量覆盖
            image_new[row][col] = np.array([0, 0, 0])
for row in range(25, 91): # 水印行从25到91
    for col in range(1676, 1902): # 水印列从1676到1902
        if image[row][col][0] > 195 and image[row][col][1] > 195 and image[row][col][2] > 195: # 通过观察发现水印的RGB像素大于195, 水印位置多扩大点没事, 尽量覆盖
            image_new[row][col] = np.array([0, 0, 0])
cv2.imwrite(MASK_DIR2, image_new)
        