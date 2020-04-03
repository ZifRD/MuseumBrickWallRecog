from os.path import join  
from google.colab import drive

ROOT = "/content/drive"  
drive.mount(ROOT) 

PROJECT_PATH = "/content/drive/My Drive/projects/MuseumBrickWallRecog/MuseumBrickWallRecog"

%cd {PROJECT_PATH}