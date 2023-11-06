# Перевод жествого языка в текст/речь

## Описание проекта

В рамках данного проекта будет реализован сервис для распознавания русского жестового языка (РЖЯ) для слабослышащих из видео в текст/речь с помощью методов глубинного обучения .

## Команда
* Свистунов Александр
* Муниев Утнасун

Куратор: **Кофанова Мария**

## Примерный план работы
1. Анализ датасета 
    * Изучение содержимого датасета
    * Поиск инструментов для извлечения признаков с видео
2. Предобработка данных и разведочный анализ данных
    * Проведем предобработку видео для извлечения признаков
3. Применение ML
    * Убедимся, что ML методы не подходят для решения поставленной задачи
    * На извлеченных из видео признаках, построим классификатор для распознавания жестов
4. Применение DL
    * Построение бейзлайн модели для решения поставленной задачи
    * Построение решения, превосходящего существующие (MViTv2-small, Swin-large, ResNet-i3d)
5. Интеграция модели в веб-сервис
    * Разработка веб-сервиса на основе фреймворка FastAPI для конечных пользователей

## Данные 
Для нашего проекта мы будем использовать готовый датасет [Slovo](https://github.com/hukenovs/slovo). Он состоит из 20.000 *видео* - по 20 видео на один из 1000 *классов* (жестов). В датасете присутствуют дополнительные 400 видео, на которых не происходит жестовых событий, чтобы ввести понятие класса "не жест". \
Данные можно скачать по [ссылке](https://disk.yandex.ru/d/MaC0HtdRFmKtJg).
