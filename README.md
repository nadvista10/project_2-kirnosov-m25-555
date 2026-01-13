# Primitive DB (учебная файловая СУБД)

Учебная «СУБД» на Python: хранит таблицы в JSON-файлах и предоставляет команды для работы с таблицами.

## Детали

- Таблицы и строки хранятся в папке `data/` в формате JSON
- Метаданные (схема таблиц) в `data/metadata.json`
- Типы столбцов: `int`, `str`, `bool`
- CLI-команды: создание таблиц, вставка, выборка с фильтрами, обновление, удаление

## Установка

Требуется Python 3.12+ и Poetry.

Через Makefile:

```bash
make install
```

Или напрямую:

```bash
poetry install
```

## Запуск

Через Makefile:

```bash
make project
```

Или напрямую:

```bash
poetry run project
```

## Команды

Ниже описан текущий синтаксис всех команд. Команды вводятся в интерактивном режиме.

### create_table

Создать таблицу:

```text
create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ...
```

Пример:

```text
create_table users age:int name:str active:bool
```

### list_tables

Показать список всех таблиц из `metadata.json`:

```text
list_tables
```

### insert

Вставить строку в таблицу:

```text
insert into <имя_таблицы> values (<значение1>, <значение2>, ...)
```

Пример:

```text
insert into users values (50, "some string value", True)
```

### select

Выбрать все строки:

```text
select from <имя_таблицы>
```

Выбрать строки с фильтрацией (можно указывать несколько `where`):

```text
select from <имя_таблицы> where <столбец>=<значение> where <столбец>=<значение> ...
```

Примеры:

```text
select from users
select from users where __ID=1
select from users where age=50 where working=True
select from users where name="some string value" where active=True
```

### update

Обновить строки по условиям (можно указывать несколько `set` и несколько `where`):

```text
update <имя_таблицы> set <столбец>=<новое_значение> set <столбец>=<новое_значение> ... where <столбец>=<значение> where <столбец>=<значение> ...
```

Пример:

```text
update users set age=21 set name="Some str" where __ID=3 where age=210
```

Ограничение: столбец `__ID` обновлять нельзя.

### delete

Удалить строки по условиям (условия задаются через `where`, можно задать несколько условий):

```text
delete from <имя_таблицы> where <столбец>=<значение> where <столбец>=<значение> ...
```

Пример:

```text
delete from users where active=False
```

### drop_table

Удалить таблицу целиком (метаданные + файл данных):

```text
drop_table <имя_таблицы>
```

### help

Показать справку по командам:

```text
help
```

### exit

Выйти из программы:

```text
exit
```

## Значения и кавычки

- Строковые значения с пробелами указывайте в кавычках: `"some string value"`
- Булевы значения: `True/False` (также поддерживаются `1/0`)
- Целые числа: `123`

## Обработка ошибок

- Некорректный синтаксис команд приводит к сообщению об ошибке, программа продолжает работу
- Некорректные типы значений приводятся/проверяются по схеме таблицы

## Структура проекта

- `src/primitive_db/engine.py` — CLI и разбор команд
- `src/primitive_db/core.py` — логика CRUD
- `src/primitive_db/utils.py` — чтение/запись JSON
- `src/primitive_db/main.py` — точка входа
