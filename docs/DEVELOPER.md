# Developer Guide

## Table of Contents <!-- omit in toc -->
- [Developer Guide](#developer-guide)
  - [Preparing for Development](#preparing-for-development)
    - [Getting the Source Code](#getting-the-source-code)
  - [Running the Code for Testing](#running-the-code-for-testing)
  - [Linting and Formatting](#linting-and-formatting)

## Preparing for Development
### Getting the Source Code
```shell
$ git clone https://github.com/Roykesydon/Hacker-Rank-Discord-Bot.git
$ cd Hacker-Rank-Discord-Bot
```

## Running the Code for Testing
> pending

## Linting and Formatting
To remain consistent coding style and statically analyze the correctness of our source code, we use linters and formatters to help developers. The installation commands are listed below.

For the project developed in Python, we choose [Pyright](https://github.com/microsoft/pyright) from Microsoft as the linter and [black](https://github.com/psf/black) as the formatter. [isort](https://github.com/PyCQA/isort) is also used to sort the import statements. 

```shell
$ cd Hacker-Rank-Discord-Bot
$ python format.py
```
