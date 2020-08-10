# MuseumBrickWallRecog

Инициативный (некоммерческий) проект для Культурно-выставочного центра Русского музея в Мурманске (подразделение Мурманского областного художественного музея).

На одной из площадок посетители собирают пазл из кубов. Имеется 20 кубов, каждая грань соответствует фрагменту одной из 6 картин. Сами картины-пазлы имеют размеры 5 на 4 куба. , а программа на планшете должна проверять результат. Необходимо обучить модель распознавателя и реализовать Android-приложение. Обучающий датасет генерируется по 6 базовым картинам.

Постановка задачи: посетитель музея собирает картину в виде набора приставленных друг к другу кубов. Каждый куб имеет ребро 20 см. Готовая картина является прямоугольником из граней 5 на 4 = 20 кубов. Всего 6 картин (по числу граней куба). Требуется создать программу, которая будет проверять правильность сборки мозайки (указания по сборке не учитываются, считается, что посетитель имеет достаточно информации для того, чтобы однозначным образом собрать картину), каждая картина проверяется отдельно. Набор кубов сего один - чтобы собрать другую картину, нужно разобрать ранее сложенную мозайку. Проверяется только результат: на полу нарисован прямоугольник 1 на 5 кубов - основание стены кубов для удобства последующей проверки мозайки. Мобильное приложение на планшете, закреплённом на подставке, делает снимок стены кубов и выдаёт ответ "да" или "нет" на вопрос о правильности сборки каждой картины. Предполается, что задания также даются этим приложением, поэтому номер эталонной картины известен программе.

Каковы варианты собрать картину неверно: (1) повернуть хотя бы один куб так, чтобы грань в плоскости собираемой картины (эталона) оказалась частью другой картины; (2) хотя бы одну грань, присутствующую как фрагмент в эталоне, поместить на неверную позицию в решётке 5 на 4 фрагментов эталона; (3) повернуть хотя бы одну грань, верно выбранный фрагмент эталона, в плоскости эталона на 90, 180, 270 градусов относительно позиции в нём и т.д

Для удобства дальнейшего решения предполагается, что нет дефектов выставления кубов (зазоров, несовпадение плоскости одной из граней с плоскостью всей картины и т.д.). В экспериментах использованы 6 изображений (200 на 160 пикселов) той же тематики и стиля исполнения, что и 3D-мозаика в музее. Каждый фрагмент имеет размеры 40 на 40 пикселов. 

Рассматриваются 2 варината: (1) идентификация всего собранного изображения как эталонного (модель VGG), (2) идентиикация каждого из 20 фрагментов в отдельности (модель YoLo, экспериментальное исследование проводит Всеволод Колоколов, Мурм. аркт. гос. ун-т).

Далее по варианту с VGG. Реализованы два варианта порождения обучающей выборки и тестов. Первый: генерируются 40% absolutely random assemblies of 20 out of 4*6*20 parts (4 - rotation is considered) to train model answer as False and 60 % random selected (1 out of 6 each time) entire original images (for True). It has come to huge False Positive.

The second version. 50 % for True (random original images)  and 50% for False, but no absolutely random assemblies, instead the following procedure applied:

1)      original image selected randomly (acceptor),

2)      3 blocks positions (out of 20 total) are selected to be modified in acceptor,

3)      3 random rotation angles selected (out of 4 variants, i.e. 0,90, 180, 270 , zero is permitted),

4)      3 donor original images and its blocks (bricks) are randomly selected,

5)      rotation is applied to each donor block and assembled in selected positions in acceptor image (it has been guaranteed to be 17 blocks of original image and not more than 3 erratic bricks). Code permits to use acceptor as donor either.

The second training generator shows increased quality, but some False Positive are found (some correction still needed).  

There are functions of training set generation, model construction and loss calculation in attached file.

My main question is whether it appropriate to use 50 % of training set repeated multiple times 6 original images as True and 50 % cases with low variability (as 1-3 out of 20 original parts) as False. Or is it possible to improve model by changing of output and/or loss function?

В обоих случаях использовалась следующая функция потерь и структура сети:

```python
from tensorflow.keras.layers import Flatten, Dense, Concatenate
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam, SGD
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.losses import binary_crossentropy, categorical_crossentropy

def custom_loss(y_true, y_pred):
  # target is a 7-tuple
  # (fox,dck,bay,chu,alx,mrm, object_appeared)

  cce = categorical_crossentropy(y_true[:, :-1], y_pred[:, :-1]) # object class
  bce = binary_crossentropy(y_true[:, -1], y_pred[:, -1]) # object appeared
  return cce * y_true[:, -1] + 0.5 * bce

def make_model():
  vgg = tf.keras.applications.VGG16(
    input_shape=[H, W, 3],
    include_top=False,
    weights='imagenet')
  x = Flatten()(vgg.output)
  x0 = Dense(6, activation='softmax')(x) # object class
  x1 = Dense(1, activation='sigmoid')(x) # object appeared
  x = Concatenate()([x0, x1])
  model = Model(vgg.input, x)
  model.compile(loss=custom_loss, optimizer=Adam(lr=0.0001))
  return model
```



