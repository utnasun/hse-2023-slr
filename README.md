# Перевод жествого языка в текст/речь

## Описание проекта

В рамках данного проекта будет реализован сервис для распознавания русского жестового языка (РЖЯ) для слабослышащих из видео в текст/речь с помощью методов глубинного обучения .

## Команда
* Свистунов Александр
* Муниев Утнасун

Куратор: **Кофанова Мария**

## План работы
1. Анализ датасета
    * Изучение содержимого датасета
    * Поиск инструментов для извлечения признаков с видео
2. Предобработка данных и разведочный анализ данных
    * Исследовать основные характеристики видео
    * Рассмотреть подходы для извлечения доп. признаков из датасета
4. Применение предобученных моделей
    * Использование предобученной модели Easy Sign для распознавания РЖЯ в качестве начального решения
    * Использование MediaPipe моделей Hand Landmarker и Pose Landmarker для извлечения позиций тела и рук
5. Дообучение DL модели
    * Анализ существующих SOTA моделей для распознавания жестов/жестового языка
    * Выбор и дообучение одной из моделей на датасете Slovo 
6. Деплой моделей
    * Разработка Телеграм-бота для конечных пользователей
    * Покрытие функционала тестами
7. Настройка CI/CD

## Данные 
Для нашего проекта мы будем использовать готовый датасет [Slovo](https://github.com/hukenovs/slovo). Он состоит из 20.000 *видео* - по 20 видео на один из 1000 *классов* (жестов). В датасете присутствуют дополнительные 400 видео, на которых не происходит жестовых событий, чтобы ввести понятие класса "не жест". \
Данные можно скачать по [ссылке](https://disk.yandex.ru/d/MaC0HtdRFmKtJg).

## Сервис

[Описание сервиса.](https://github.com/utnasun/hse-2023-slr/blob/2fc294a142a45578e35b941c064ad2e1972dfa59/slr_bot/README.md)
