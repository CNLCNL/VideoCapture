import cv2, os, numpy as np  # OpenCV
from tqdm import tqdm
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

class VideoProcess():
    def __init__(self):
        pass

    def ImageWaterCancel(self, mask: np.array, image: np.array, mask_ranges = None):
        """
            除水印函数:  
            mask: 水印图片对象  
            image: 原图片对象  
            mask_ranges: 三维数组, 多个水印对应范围, 加速用, 若不传入则全图扫描  
        """
        new_image = image # 创建一张一样的图像用于保存
        cur_ele = np.array([255, 255, 255]) # 初始默认用空白元素填充
        if mask_ranges is None:
            mask_range = [[[0, image.shape[0]], [0, image.shape[1]]]]
        for mask_range in mask_ranges:
            cur_ele = np.array([255, 255, 255])
            for row in range(mask_range[0][0], mask_range[0][1]):
                for col in range(mask_range[1][0], mask_range[1][1]):
                    if not (mask[row, col] == np.array([255, 255, 255])).all():
                        new_image[row, col] = cur_ele # 用最近非水印的元素填充
                    else:
                        new_image[row, col] = image[row, col]
                        cur_ele = image[row, col]
        return new_image

    def CaptureVideo(self, filedir, savedir, cut_time = None, resolution = None, maskdir = None, mask_ranges = None, blur = None, ksize = 5):
        """ 
            剪辑视频函数:  
            filedir: 视频原文件路径  
            savedir: 剪辑视频文件保存路径   
            cut_time: 剪辑视频起始、结束时间    
            resolution: 自定义分辨率[width, height]  
            maskdir: 水印图片位置   
            mask_ranges: 三维数组, 水印对应范围, 加速用, 若不传入则全图扫描  
            blur: 滤波函数, 若不传入则不进行图片平滑处理  
            ksize: 卷积核的大小, 默认为5   
            注: 该函数生成的视频无音频, 需要再拼接音频, 此处cut_time剪切视频只是为了测试用, 建议不要在这里剪视频片段然后用moviepy合并音频(因为有一些视频帧率不为整数, 
            在剪切视频和合并音频可能会对不上), 直接用moviepy剪切视频然后合并音频最合适
        """
        cap = cv2.VideoCapture(filedir) # 读取视频文件
        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)  # 获得视频文件的帧数
        fps = cap.get(cv2.CAP_PROP_FPS)  # 获得视频文件的帧率
        if resolution is None: # 自定义分辨率
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # 获得视频文件的帧宽
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # 获得视频文件的帧高
        else:
            width = resolution[0]
            height = resolution[1]
        if maskdir is not None: # 去除水印
            mask = cv2.imread(maskdir)

        # 创建保存视频文件类对象
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') # 定义视频文件类型
        out = cv2.VideoWriter(savedir, fourcc, fps, (int(width), int(height))) # 剪辑视频对象
        if cut_time is None:
            start = 0
            end = int(frames)
        else:
            start = int(cut_time[0] * fps)
            end = int(cut_time[1] * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start * fps)
        for pos in tqdm(range(start, end)):
            ret, frame = cap.read()  # 捕获一帧图像
            if maskdir is not None: # 除水印
                frame = self.ImageWaterCancel(mask, frame, mask_ranges) 
                if blur is not None:
                    frame = self.ImageBlur(frame, mask_ranges, blur, ksize)
            if resolution is not None:
                frame = cv2.resize(frame, resolution) # 改变分辨率
            out.write(frame)  # 保存帧

        cap.release() # 释放视频对象
        out.release()

    def ImageBlur(self, image: np.array, mask_ranges = None, blur = "median", ksize = 5, sigmax = 0):
        """
            滤波函数: 支持均值滤波、中值滤波、高斯滤波  
            image: 图片, np.array  
            mask_ranges: 三维数组, 水印对应范围, 加速用, 若不传入则全图滤波  
            ksize: 卷积核的大小, 默认为5  
            sigmax: 只在高斯滤波用, 表示X方向方差  
        """  
        if mask_ranges is None:
            mask_ranges = [[[0, image.shape[0]], [0, image.shape[1]]]]
        for mask_range in mask_ranges:
            row_s, row_e, col_s, col_e = mask_range[0][0], mask_range[0][1], mask_range[1][0], mask_range[1][1]
            if blur == "median":
                image[row_s: row_e, col_s: col_e, :] = cv2.medianBlur(image[row_s: row_e, col_s: col_e, :], ksize) # 中值滤波
            elif blur == "gauss":
                image[row_s: row_e, col_s: col_e, :] = cv2.GaussianBlur(image[row_s: row_e, col_s: col_e, :], (ksize, ksize), sigmax) # 高斯滤波
            else:
                image[row_s: row_e, col_s: col_e, :] = cv2.medianBlur(image[row_s: row_e, col_s: col_e, :], (ksize, ksize)) # 均值滤波
        return image

    def MergeVideos(self, filedirs: list, cut_time = None):
        """
            视频拼接函数:  
            filedirs: 视频原文件路径, list  
            cut_time: 二维数组, 剪辑音频起始、结束时间  
        """    
        all_vedios = []
        for i in range(len(filedirs)):
            filedir = filedirs[i]
            if cut_time is None or cut_time[i] is None: # 如果不传入此参数或者改视频不剪切, 则直接加入
                all_vedios.append(VideoFileClip(filedir))
            else:
                all_vedios.append(VideoFileClip(filedir).subclip(cut_time[i][0], cut_time[i][1]))
        return concatenate_videoclips(all_vedios)
    
    def MergeAudios(self, filedirs: list, cut_time = None):
        """
            音频拼接函数:  
            filedirs: 音频原文件路径, list  
            cut_time: 二维数组, 剪辑音频起始、结束时间
        """    
        all_audios = []
        for i in range(len(filedirs)):
            filedir = filedirs[i]
            if cut_time is None or cut_time[i] is None: # 如果不传入此参数或者该视频不剪切, 则直接加入
                all_audios.append(AudioFileClip(filedir))
            else:
                all_audios.append(AudioFileClip(filedir).subclip(cut_time[i][0], cut_time[i][1]))
        return concatenate_audioclips(all_audios)

PATH = "C:/Users/10790/Desktop/bilibili_video"
INPUT_DIR1, OUTPUT_DIR1 = os.path.join(PATH, "疏远.mp4"), os.path.join(PATH, "疏远_剪辑.mp4")
MASK_DIR1 = os.path.join(PATH, "mask1.jpg") # 只含有水印的图片
INPUT_DIR2, OUTPUT_DIR2 = os.path.join(PATH, "敢杀我的马.mp4"), os.path.join(PATH, "敢杀我的马_剪辑.mp4")
MASK_DIR2 = os.path.join(PATH, "mask2.jpg") # 只含有水印的图片
# 视频剪辑、除水印、拼接
video_process = VideoProcess()
video_process.CaptureVideo(INPUT_DIR1, OUTPUT_DIR1, resolution = [1280, 720], maskdir = MASK_DIR1, 
                           mask_ranges = [[[24, 65], [975, 1264]]], blur = "median", ksize = 11)
video_process.CaptureVideo(INPUT_DIR2, OUTPUT_DIR2, resolution = [1280, 720], maskdir = MASK_DIR2, 
                           mask_ranges = [[[115, 178], [135, 369]], [[25, 91], [1676, 1902]]], blur = "median", ksize = 11)
# 视频拼接
final_video = video_process.MergeVideos([OUTPUT_DIR1, OUTPUT_DIR2]) # 有声音的视频拼接完还是有声音, 无声音的视频拼完得拼接音频
# 音频拼接
final_audio = video_process.MergeAudios([INPUT_DIR1, INPUT_DIR2])
# 将音频剪辑与视频同步
synced_audio = final_audio.set_duration(final_video.duration)
# 合并视频和音频
final_clip = concatenate_videoclips([final_video.set_audio(synced_audio)])
# 输出合并后的视频
final_clip.write_videofile(os.path.join(PATH, "combined_video.mp4"))
# final_clip.write_videofile(os.path.join(PATH, "combined_video.wmv"), codec = "mpeg4") # 其它格式需要指定codec
