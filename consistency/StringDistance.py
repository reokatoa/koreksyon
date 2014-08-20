import numpy
from difflib import SequenceMatcher

# Implementation from http://en.wikipedia.org/wiki/Levenshtein_distance
def levenshtein(s1, s2, path=False):
    if len(s1) < len(s2):
        return levenshtein(s2, s1, path)

    # len(s1) >= len(s2)
    if len(s2) == 0 and path is not True:
        return len(s1)
 
    previous_row = range(len(s2) + 1)
    matrix = [previous_row]
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1     # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
        matrix.append(current_row)

    if path is True:
        return _levenshteinPath(s1, s2, numpy.matrix(matrix))
    else:
        return previous_row[-1]

def _levenshteinPath(s1, s2, matrix):
    i, j = matrix.shape
    i, j = i-1, j-1

    intermediate = s2
    path = []
    sequence = [intermediate]
    while i > 0 and j > 0:
        start = matrix[i, j]
        up = matrix[i-1, j]
        left = matrix[i, j-1]
        diag = matrix[i-1, j-1]

        if (diag <= up and diag <= left and (diag == start or diag == start-1)):
            if s1[i-1] != s2[j-1]:
                path.append("/".join(sorted([s2[j-1], s1[i-1]])))
                intermediate = intermediate[:j-1]+s1[i-1]+intermediate[j:]
                sequence.append(intermediate)
            i, j = i-1, j-1
        elif (up <= left and (diag == start or up == start-1)):
            path.append("+"+s1[i-1])
            intermediate = intermediate[:j]+s1[i-1]+intermediate[j:]
            sequence.append(intermediate)
            i = i-1
        elif (left == start or left == start-1):
            path.append("-"+s2[j-1])
            intermediate = intermediate[:i-1]+intermediate[i:]
            sequence.append(intermediate)
            j = j-1
        else:
            raise Exception("Illegal path in matrix "+path)
    while i > 0:
        path.append("+"+s1[i-1])
        intermediate = intermediate[:j]+s1[i-1]+intermediate[j:]
        sequence.append(intermediate)
        i = i-1
    while j > 0:
        path.append("-"+s2[j-1])
        intermediate = intermediate[j:]
        sequence.append(intermediate)
        j = j-1

    return path, sequence

def pythonDiff(s1, s2, path=False):
    sm = SequenceMatcher(a=s1, b=s2)
    
    changes = []
    opcodes = sm.get_opcodes()
    for opcode in opcodes:
        if opcode[0] == 'replace':
            changes.append(sm.a[opcode[1]:opcode[2]]+">"+sm.b[opcode[3]:opcode[4]])
        elif opcode[0] == 'delete':
            changes.append("-"+sm.a[opcode[1]:opcode[2]])
        elif opcode[0] == 'insert':
            changes.append("+"+sm.b[opcode[3]:opcode[4]])
        else:
            continue
        
    if path:
        return changes
    else:
        return len(changes)

def soundex(s1, s2, soundex):
    return (0 if soundex.encode(s1) == soundex.encode(s2) else 1)
