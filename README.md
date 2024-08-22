# Graded Jupyter Notebook Integration

## Overview

Это форк репозитория [jupyter-edx-grader-xblock](https://github.com/iblai/jupyter-edx-grader-xblock) адаптированный для tutor. 
Здесь исправлены многие ошибки, связанные с установкой этого xblock на платформе tutor. Детальное описание библиотеки и принцип работы 
можно прочитать в документации к оригинальному репозиторию.

## Настройка и установка

### XBlock
* Добавить в переменную окружения `OPENEDX_EXTRA_PIP_REQUIREMENTS` ссылку не репозиторий
```bash
tutor config save --append OPENEDX_EXTRA_PIP_REQUIREMENTS='git+https://github.com/Ezereul/jupyter-edx-grader-xblock.git'
```
* Скопировать файл jupyter_grader.yml в папку tutor-plugins. Перед этим изменить в этом файле 
значение для `JUPYTER_GRADER_HOST_ROOT` на необходимое
* Затем активировать плагин jupyter_grader
```bash
tutor plugins enable jupyter_grader
```
* Пересобрать образы и запустить платформу

После установки xblock необходимо дать контейнеру cms доступ к docker.sock, а также создать папку, через 
которую будут передаваться файлы в контейнерах. Изначально контейнер cms/lms запускал контейнер для ноутбуков и пробрасывал
туда volumes на свои папки. Но с tutor это решение не работает, поэтому нужно использовать локальную папку.

* Доступ к docker.sock
```bash
tutor mounts add cms:/var/run/docker.sock:/var/run/docker.sock
tutor mounts add lms:/var/run/docker.sock:/var/run/docker.sock
```
* Монтирование локальной папки, у lms и cms это должны быть одна и та же папка на локальной машине.
```bash
tutor mounts add cms:[путь к локальной папке]:/var/www/nbgrader 
tutor mounts add lms:[путь к локальной папке]:/var/www/nbgrader 
```
* Затем нужно зайти в контейнер cms и выдать доступ к docker.sock группе docker
```bash
docker exec -it --user root tutor_local-cms-1 /bin/bash 
chown root:docker /var/run/docker.sock
```

### Добавление xblock на платформе
1. Зайти в studio
2. Раскрыть `Настройки` в шапке страницы и выбрать `Расширенные настройки`
3. Найти `Advanced Module List`/`Список дополнительных модулей` и добавить туда `"xblock_jupyter_graded"`
4. После этого блок станет доступен во вкладке `Дополнительно` при редактировании курса

### Применение миграций
Run the following as a root user to create the necessary database models:
```bash
tutor local run cms ./manage.py cms migrate xblock_jupyter_graded
```

### Nginx Setup
Currently, this XBlock makes some long running Ajax calls which can exceed the default nginx timeout of 60s on some machines. We will temporarily increase this timeout until the architecture can be updated to make this a background task that can be polled for state.

In the followingfile:
- `/etc/nginx/nginx.conf`

Add the following line in the `http` section under `# Basic Settings`:
- `proxy_read_timeout 300;`

Restart nginx via: `service nginx restart`

## Организация XBlock
### Представление автора в Studio
На главном экране автора в Studio есть три основные секции, связанные с инструктором:
- Виртуальная среда Python
- Загрузка ноутбука инструктора
- Детали загруженного ноутбука

#### Виртуальная среда Python
  - Позволяет выбрать и загрузить файл `requirements.txt` для этого курса.
    - Вам **нужно** добавить только те пакеты, которые импортируются внутри ноутбука.
    - Вам **не нужно** включать nbgrader, jupyter, ipykernel или любые другие пакеты, связанные с jupyter. 
    - `ipykernel` включен по умолчанию, так как он необходим для установки виртуальной среды студента в качестве среды выполнения.
  - **Эта среда Python будет общей для всех ноутбуков в этом курсе**
  - Список установленных пакетов отображается в разделе **Установленные пакеты**.
  - `requirements.txt` должен быть отформатирован как обычный файл `requirements.txt`, но поддерживает только следующие форматы:
    - `package_name==package_version` - фиксированная версия пакета
    - `package_name` - нефиксированная версия - устанавливает самую новую версию пакета
  - Docker-контейнер будет создаваться каждый раз, когда загружается новая среда, которая еще не существует.

#### Загрузка ноутбука инструктора
- Позволяет выбрать и загрузить исходный ноутбук, который будет использоваться для создания версии для студентов.

#### Детали загруженного ноутбука
- Отображает детали о загруженном ноутбуке и позволяет инструктору скачать текущую прикрепленную версию.

### Настройки XBlock
- _Отображаемое имя_: Название этого XBlock, которое будет видеть студент.
- _Инструкции для студентов_: Набор инструкций, которые будут показаны студенту.
- _Разрешенные попытки (по умолчанию: 0)_: Максимальное количество попыток, которые может сделать студент. Если установлено значение `0`, допускается бесконечное количество попыток.
- _Разрешена сеть (по умолчанию: False)_: Если True, позволяет доступ к сети изнутри контейнера.
  - **ПРЕДОСТЕРЕЖЕНИЕ**: **Так как Jupyter Notebooks позволяет выполнять произвольный код, лучше оставить это значение `False`, иначе студент может совершать несанкционированные веб-запросы с точки зрения сервера.**
  - Здесь нужно провести дополнительные работы для создания более детальной изоляции сети.
- _Тайм-аут ячейки (по умолчанию: 15с)_: Максимальное время, в течение которого разрешается выполнение одной ячейки, прежде чем будет вызвано исключение `KeyboardInterrupt` для попытки остановить ячейку.
- _Разрешить скачивание оцененного NB (по умолчанию: False)_: Если `True`, позволяет студенту скачать автосгенерированный файл `.html`, созданный при запуске `nbgrader feedback`.
  - **Примечание**: Это покажет все `### HIDDEN TESTS` из ноутбука инструктора, так как они включены в автосгенерированный отзыв.
- _Максимальный размер файла (Б)_: Максимальный размер файла, который студент может загрузить (в байтах).
  - По умолчанию на 10 кБ больше размера версии ноутбука инструктора, если это поле не установлено при загрузке версии инструктора. В противном случае его можно изменить по вашему усмотрению, но его необходимо установить.

## Рабочий процесс инструктора
- Добавьте `Оценочный Jupyter Notebook` с помощью кнопки `Advanced` в Studio курса.
- При необходимости загрузите файл `requirements.txt`, содержащий все пакеты, необходимые для этого курса.
- Создайте исходный Jupyter Notebook с помощью локальной установки jupyter и nbgrader, а затем сохраните/экспортируйте его на вашу систему.
  - Рекомендуется установить значение `ID` ячейки для каждой ячейки с тестами Autograder на что-то значимое для студента.
  - Например, если ваш ноутбук имеет два раздела и два оценочных упражнения в каждом разделе:
    - Раздел 1
      - Упражнение 1
      - Упражнение 2
    - Раздел 2
      - Упражнение 1
      - Упражнение 2
  - Название тестовых ячеек, например:
    - `section1_excercise1` поможет студенту связать оценочное значение с тестом или разделом в ноутбуке, когда он увидит свои результаты.
- Загрузите исходный ноутбук в разделе `Загрузка ноутбука инструктора`.
  - Максимальный балл и детали ноутбука отразятся в разделе `Детали загруженного ноутбука`.
  - Ошибка будет выдана, если текст `BEGIN SOLUTION` не найден в ноутбуке, так как это, вероятно, указывает на то, что была загружена неправильная версия.
- Версия для студентов будет сгенерирована и может быть загружена в разделе для студентов.
- Обновите настройки для этого XBlock по мере необходимости.
- Опубликуйте модуль.

## Рабочий процесс студента
- Выберите ссылку `Скачать студенческий ноутбук`, чтобы загрузить версию для студентов.
- Выполните задание в ноутбуке через локальную установку jupyter.
- Загрузите завершенную версию студенческого ноутбука.
  - Имя ноутбука должно совпадать с тем, что указано в метке `Имя ноутбука:`.
- Ноутбук будет оценен, и результаты отобразятся в разделе `Результаты`.
  - Если у студента больше нет попыток, он больше не сможет загрузить новый ноутбук.
  - Последняя загруженная версия фиксируется для оценки.

## Usage notes

### Watch the demo!

[![demo](https://github.com/ibleducation/jupyter-viewer-xblock/blob/master/demo-thumbnail.png)](http://www.youtube.com/watch?v=SwRAs8_FIdo)


## Copyright and License
(c) 2017 IBL Studios and Lorena A. Barba, [code is under BSD-3 clause](https://github.com/engineersCode/EngComp/blob/master/LICENSE). 

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
