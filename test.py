def transpose(matrix):
    size = len(min(matrix, key=len))
    return [[row[i] for row in matrix]
            for i in range(size)]


def remove_empty_columns(matrix):
    transpose(matrix)
    matrix = [row for row in matrix if any(row)]
    transpose(matrix)


def split_one_of_the_columns(matrix):
    m = []
    for i in range(len(matrix)):
        m.append([])
        for j in range(len(min(matrix, key=len))):
            if("&" not in matrix[i][j]):
                m[i].append(matrix[i][j])
            else:
                s = matrix[i][j].split("&")
                m[i].append(s[0])
                m[i].append(s[1])
    return m


def transform_cell_contents(matrix):


def main(matrix):
    remove_empty_columns(matrix)
    matrix = split_one_of_the_columns(matrix)





matrix = [[None, "tamerlan70@yandex.ru", None, "0&2003/01/21", "Тамерлан Б. Лодикук"],
          [None, "vsevolod46@mail.ru", None, "0&2000/03/19", "Всеволод Ф. Гошисли"],
          [None, "anatolij89@rambler.ru", None, "1&2004/05/25", "Анатолий Г. Чицли"],
          [None, "facidi50@gmail.com", None, "0&2001/10/20", "Иван Ш. Фачиди"]]