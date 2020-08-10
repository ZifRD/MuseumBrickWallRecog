# MuseumBrickWallRecog

Инициативный (некоммерческий) проект для Культурно-выставочного центра Русского музея в Мурманске (подразделение Мурманского областного художественного музея).

Старт: март 2020 г.
Пройденные этапы: (1) созданы генераторы датасетов 2-мя способами, (2) выполнено обучение моделей, (3) реализовано тестовое Android-приложение для взаимодействия с моделями.
Текущий этап: тюнинг моделей (на базе VGG и YoLo).

Постановка задачи: посетитель музея собирает картину в виде набора приставленных друг к другу кубов. Каждый куб имеет ребро 20 см. Готовая картина является прямоугольником из граней 5 на 4 = 20 кубов. Всего 6 картин (по числу граней куба). Требуется создать программу, которая будет проверять правильность сборки мозайки (указания по сборке не учитываются, считается, что посетитель имеет достаточно информации для того, чтобы однозначным образом собрать картину), каждая картина проверяется отдельно. Набор кубов сего один - чтобы собрать другую картину, нужно разобрать ранее сложенную мозайку. Проверяется только результат: на полу нарисован прямоугольник 1 на 5 кубов - основание стены кубов для удобства последующей проверки мозайки. Мобильное приложение на планшете, закреплённом на подставке, делает снимок стены кубов и выдаёт ответ "да" или "нет" на вопрос о правильности сборки каждой картины. Предполается, что задания также даются этим приложением, поэтому номер эталонной картины известен программе.

Каковы варианты собрать картину неверно: (1) повернуть хотя бы один куб так, чтобы грань в плоскости собираемой картины (эталона) оказалась частью другой картины; (2) хотя бы одну грань, присутствующую как фрагмент в эталоне, поместить на неверную позицию в решётке 5 на 4 фрагментов эталона; (3) повернуть хотя бы одну грань, верно выбранный фрагмент эталона, в плоскости эталона на 90, 180, 270 градусов относительно позиции в нём и т.д

Для удобства дальнейшего решения предполагается, что нет дефектов выставления кубов (зазоров, несовпадение плоскости одной из граней с плоскостью всей картины и т.д.). В экспериментах использованы 6 изображений (200 на 160 пикселов) той же тематики и стиля исполнения, что и 3D-мозаика в музее. Каждый фрагмент имеет размеры 40 на 40 пикселов. 

Рассматриваются 2 варината: (1) идентификация всего собранного изображения как эталонного (модель VGG), (2) идентиикация каждого из 20 фрагментов в отдельности (модель YoLo, экспериментальное исследование проводит Всеволод Колоколов, Мурм. аркт. гос. ун-т).

Далее по варианту с VGG. Реализованы два варианта порождения обучающей выборки и тестов. 

Первый: генерируются 40% соверешенно случайных пазлов (каждый пазл - это 20 упорядоченных фрагментов из 4*6*20 возможных (4 - кол-во вариантов поворота грани в одной плоскости) класса "нет" и 60% случайно выбранных (1 из 6) эталонных изображений класса "да". По итогам были получены высокие False Positive.

Второй: 50% для класса "да" (случайно выбранные эталоны) и 50% класса "нет", но полностью случайные варианты исключены. Алгоритм генерации для "нет":

1. Случайно выбирается эталон (акцептор).
2. Случайно выбираются 3 различные позиции фрагменов (в решётке 5 на 4) для модификации в акцепторе.
3. Случайно выбираются углы поворота независимо для каждой позиции из пред. пункта (4 варианта, то есть 0, 90, 180, 270).
4. Случайно выбираются 3 эталонных изображения (из 6) и 3 позиции фрагментов в них (это доноры, повторы возможны).
5. К каждому фрагменты донора применяется соответствующий поворот, после чего фрагмент занимает соответствующую позицию в акцепторе (с учётом порядка). 

Таким образом, второй варинт гарантирует 17 правильно выставленных фрагментов и не более 3 ошибочных (акцептор сам моет быть донором). По итогам второго варианта удалось существенно понизить False Positive.

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



