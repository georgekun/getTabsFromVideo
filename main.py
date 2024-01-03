import os

import cv2 
from PIL import Image
from pytube import YouTube

def prepare_screenshots(video_path:str, destination:str, period:int) -> None:
    
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval_frames = int(fps * period) #чтобы по секундам кадры делались
 
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % interval_frames == 0:
            screenshot_path = f'{destination}/screenshot_{frame_count}.png'
            cv2.imwrite(screenshot_path, frame)
        frame_count += 1
    cap.release()


def crop_screenshotes(directory:str, destination:str)->None:
    for root, dirs, files in os.walk(directory):
        for image in files:
            img = Image.open(os.path.join(directory,image))
            width, height = img.size
            cropped_img = img.crop((0, height - 210, width, height))# Обрезаем изображение, оставляя только верхние (height - 300) пикселей
            cropped_img.save(f'{destination}/cropped_' + image)# Сохраняем обрезанное изображение


def create_canvas(height:str, width:str) -> Image:
    dst = Image.new('RGB', (width , height))
    return dst


def create_notes(directory:str, destination:str)->None:
    canvas_list = list()
    for root, dirs, files in os.walk(directory):
        count_images = len(files)
        img = Image.open(os.path.join(directory, files[0]))
        files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
        
        while count_images >= 4:
            canvas = create_canvas( img.height * 4, img.width)
            for i in range(4):
                img_path = os.path.join(directory, files.pop(0))
                new_img = Image.open(img_path)
                canvas.paste(new_img, (0, i * new_img.height))

            canvas_list.append(canvas)
            count_images -= 4

        for i,canvas in enumerate(canvas_list):
            canvas.save(os.path.join(destination, f"note_list_{i}.jpg"))
        

def is_image_empty(image_path):
    img = Image.open(image_path)
    img_data = img.getdata()
    non_empty_pixels = sum(1 for pixel in img_data if pixel != (0, 0, 0)) 
    image_fill_percentage = (non_empty_pixels / (img.width * img.height)) * 100
    return image_fill_percentage < 1  


def clear_empty_photo(directory:str) -> None:
    for root, dirs, files in os.walk(directory):
        print(f"Изначально фотографий - ", len(files))
        for img in files:
            path =  os.path.join(directory, img)
            if is_image_empty(path):
                os.remove(path)
                
    for root, dirs, files in os.walk(directory):
        print(f"Количество оставшихся фотографий - ", len(files))

def download_video(url:str, save_path:str) -> str:
    yt = YouTube(url)
    video = yt.streams.get_highest_resolution()
    video.download(save_path)
    return save_path
    
    
def main():
    
    video_path = download_video("https://www.youtube.com/watch?v=tlgKGdT1dek&t=19s", "")
    print("\nСкаченное видео - ", video_path)
    print("Делаю скриншоты...")
    video_path = 'tabs-video.mp4'
    dest = 'images'
    period = 4
    prepare_screenshots(video_path, dest, period)
    print("Скриншоты готовы!")
    
   
    croped_dest = 'crop'
  
    print("Начинаю резать...")
    crop_screenshotes(directory=dest, destination=croped_dest)
    print(f"Вырезанные фотографии находяться в {croped_dest}")
    print("Удаление пустых скриншотов...")
    clear_empty_photo(croped_dest)
    print("Пустые скриншоты удалены!")
    create_notes(croped_dest, "notes")

if __name__ == "__main__":
    main()