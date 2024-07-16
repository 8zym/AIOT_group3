import cv2
import tensorflow
from tensorflow.keras.models import Sequential, Model
from tqdm import tqdm
import numpy as np
import pandas as pd
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization, GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing import image
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.applications.vgg16 import VGG16
import pymysql
import time
import base64

def create_model_v2():
    # Optimised Vanilla CNN model
    model = Sequential()

    ## CNN 1
    model.add(Conv2D(32,(3,3),activation='relu',input_shape=(img_rows, img_cols, color_type)))
    model.add(BatchNormalization())
    model.add(Conv2D(32,(3,3),activation='relu',padding='same'))
    model.add(BatchNormalization(axis = 3))
    model.add(MaxPooling2D(pool_size=(2,2),padding='same'))
    model.add(Dropout(0.3))

    ## CNN 2
    model.add(Conv2D(64,(3,3),activation='relu',padding='same'))
    model.add(BatchNormalization())
    model.add(Conv2D(64,(3,3),activation='relu',padding='same'))
    model.add(BatchNormalization(axis = 3))
    model.add(MaxPooling2D(pool_size=(2,2),padding='same'))
    model.add(Dropout(0.3))

    ## CNN 3
    model.add(Conv2D(128,(3,3),activation='relu',padding='same'))
    model.add(BatchNormalization())
    model.add(Conv2D(128,(3,3),activation='relu',padding='same'))
    model.add(BatchNormalization(axis = 3))
    model.add(MaxPooling2D(pool_size=(2,2),padding='same'))
    model.add(Dropout(0.5))

    ## Output
    model.add(Flatten())
    model.add(Dense(512,activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(128,activation='relu'))
    model.add(Dropout(0.25))
    model.add(Dense(10,activation='softmax'))

    return model

activity_map = {'c0': 'Safe driving', 
                'c1': 'Texting - right', 
                'c2': 'Talking on the phone - right', 
                'c3': 'Texting - left', 
                'c4': 'Talking on the phone - left', 
                'c5': 'Operating the radio', 
                'c6': 'Drinking', 
                'c7': 'Reaching behind', 
                'c8': 'Hair and makeup', 
                'c9': 'Talking to passenger'}

img_rows = 64
img_cols = 64
color_type = 1
nb_epoch = 10
batch_size = 40

# 连接到数据库
db = pymysql.connect(
    host='47.121.193.122',
    user='root',
    password='123456',
    database='emqx_data',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = db.cursor()  # 创建一个指针

model_v2 = create_model_v2()

# More details about the layers
model_v2.summary()

# Compiling the model
model_v2.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])

model_v2.load_weights('saved_models/weights_best_vanilla.keras')

# 查询获取Base64编码的图片数据
query = 'SELECT image_data FROM image_data ORDER BY id DESC LIMIT 1;'  # 根据需要调整查询语句
index = 0
while True:
    cursor.execute(query)
    result = cursor.fetchone()

    # 检查查询结果
    if result:
        image_base64 = result['image_data']
        
        # 解码Base64数据
        image_data = base64.b64decode(image_base64)
        nparr = np.frombuffer(image_data, np.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        filename = f'output_image_{index}.png'
        with open(filename, 'wb') as file:
            file.write(image_data)
    
        print("图片已成功解码")
    else:
        print("没有查询到图片数据")

    img_brute = cv2.resize(img_np,(img_rows,img_cols))

    new_img = img_brute.reshape(-1,img_rows,img_cols,color_type)

    y_prediction = model_v2.predict(new_img, batch_size=batch_size, verbose=1)

    print('Predicted: {}'.format(activity_map.get('c{}'.format(np.argmax(y_prediction)))))

    index = (index+1) % 5
    
    time.sleep(5)

# 关闭游标和数据库连接
cursor.close()
db.close()
