# MuseumBrickWallRecog

Инициативный (некоммерческий) проект для Культурно-выставочного центра Русского музея в Мурманске (подразделение Мурманского областного художественного музея).

На одной из площадок посетители собирают пазл из кубов. Имеется 20 кубов, каждая грань соответствует фрагменту одной из 6 картин. Сами картины-пазлы имеют размеры 5 на 4 куба. , а программа на планшете должна проверять результат. Необходимо обучить модель распознавателя и реализовать Android-приложение. Обучающий датасет генерируется по 6 базовым картинам.

Постановка задачи: посетитель музея собирает картину в виде набора приставленных друг к другу кубов. Каждый куб имеет ребро 20 см. Готовая картина является прямоугольником из граней 5 на 4 = 20 кубов. Всего 6 картин (по числу граней куба). Требуется создать программу, которая будет проверять правильность сборки этой мозайки (указания по сборке не учитываются, считается, что посетитель имеет достаточно информации для того, чтобы одного)  

Task: Visitor in museum tries to assemble a painting as a brick set (real 3D bricks, not computer model). Bricks are of 20 cm for a side. Brick wall as painting contains 5 by 4 = 20 bricks. There are 6 paintings (original images) to be assembled and program will check it. Bad assembly means that one or more (1) rotated bricks (90, 180, 270 degrees), (2) bricks on wrong places, (3) brick faces from other paintings appeared. Model will answer whether original image assembled and its number (out of 6) if true. Model will be supplied with images from phone camera, shots of brick wall. For experiments  I use 40 by 40 pixel parts for brick faces (200 by 160 pixels total for each image assembly).

The first attempt was to generate 40% absolutely random assemblies of 20 out of 4*6*20 parts (4 - rotation is considered) to train model answer as False and 60 % random selected (1 out of 6 each time) entire original images (for True). It has come to huge False Positive.

The second version. 50 % for True (random original images)  and 50% for False, but no absolutely random assemblies, instead the following procedure applied:

1)      original image selected randomly (acceptor),

2)      3 blocks positions (out of 20 total) are selected to be modified in acceptor,

3)      3 random rotation angles selected (out of 4 variants, i.e. 0,90, 180, 270 , zero is permitted),

4)      3 donor original images and its blocks (bricks) are randomly selected,

5)      rotation is applied to each donor block and assembled in selected positions in acceptor image (it has been guaranteed to be 17 blocks of original image and not more than 3 erratic bricks). Code permits to use acceptor as donor either.

The second training generator shows increased quality, but some False Positive are found (some correction still needed).  

There are functions of training set generation, model construction and loss calculation in attached file.

My main question is whether it appropriate to use 50 % of training set repeated multiple times 6 original images as True and 50 % cases with low variability (as 1-3 out of 20 original parts) as False. Or is it possible to improve model by changing of output and/or loss function?
