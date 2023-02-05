from collections import defaultdict
FILE_NAME='exercise1.txt'

def line_parser(line):
    clauses = []
    line = line[1:-1]
    length = len(line)
    index = 0
    cur_str = ''
    while index < length:
        if line[index] == '[':
            clauses.append([])
        elif line[index] ==  ']' or line[index] == ',':
            if cur_str != '':
                clauses[-1].append(cur_str)
            cur_str = ''
        else:
            cur_str = cur_str + line[index]
        index += 1

    return clauses


def negation(atom):
    if '¬' in atom:
        return atom[1:]
    else:
        return '¬' + atom

def check_inclusion(list1, list2):
    return all([item in list2 for item in list1])


def resolve(clause1, clause2, p):
    if p in clause1 and negation(p) in clause1:
        return None
    if p in clause2 and negation(p) in clause2:
        return None
    if p in clause1 and negation(p) in clause2:
        items = [x for x in clause1 if x != p]
        for x in clause2:
            if negation(p) != x:
                items.append(x)
        return items
    if p in clause2 and negation(p) in clause1:
        items = [x for x in clause2 if x != p]
        for x in clause1:
            if negation(p) != x:
                items.append(x)
        return items
    return None


def find_clauses(clauses):
    for index, clause in enumerate(clauses):
        for index_combine, clause_combine in enumerate(clauses):
            if index != index_combine:
                for x in clause:
                    resolve_attempt = resolve(clause, clause_combine, x)
                    if resolve_attempt is not None and resolve_attempt not in clauses:
                        return resolve_attempt
    return None



def resolution(clauses):
    if ([] in clauses):
        return False

    new_clause = find_clauses(clauses)
    # print(new_clause)
    if new_clause is None:
        return True
    return resolution([*clauses, new_clause])

def execute_test(test):
    print("===================")
    print(f'Test: {test}')
    status = resolution(test)
    print(f'Status: {status}')
    if status == False:
        print('Unsatisfiable')
    else:
        print('Satisfiable')
    print("===================")

questions = {
    'studied':'How many hours did the student study? (number of hours)',
    'participation' :'How many courses did the student participate to? (number of courses)',
    'wakesup' :'How early does the student wake up everyday? (xx:xx)',
    'dedication': 'Was the student dedicated for this exam? (yes/no)',
}

def main():
    tests = []
    with open(FILE_NAME, 'r') as f:
        for line in f.readlines():
            line = line[:-1]
            clauses = line_parser(line)
            tests.append(clauses)
    print('Tests are:')
    for clauses in tests:
        print(clauses)
    
    stopped = False
    while True:
        print('Answer questions or type exit to stop:')
        answers = {}
        for key, question in questions.items():
            print(question)
            response = input(key + ":")
            answers[key] = response
            if response == "exit":
                stopped = True
                break
        if stopped:
            break
    

if __name__ == '__main__':
    main()
