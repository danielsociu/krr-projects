from copy import deepcopy
FILE_NAME='ex1_input.txt'
DEBUG=False

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

def is_negation(atom):
    return '¬' in atom

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


def find_clauses(clauses, resolver):
    for clause in clauses:
        for x in resolver:
            resolve_attempt = resolve(resolver, clause, x)
            if resolve_attempt is not None and resolve_attempt not in clauses:
                return resolve_attempt
    return None



def resolution_backward(clauses, resolver):
    if resolver == []:
        return False

    new_clause = find_clauses(clauses, resolver)
    if DEBUG:
        print(new_clause)
    if new_clause is None:
        return True
    return resolution_backward(clauses, new_clause)

def find_positive_atom(atoms, kb):
    for clause in kb:
        found = True
        for x in clause:
            if is_negation(x):
                if [negation(x)] not in atoms:
                    found = False
        if found:
            for x in clause:
                if not is_negation(x):
                    return [x]



def resolution_forward(atoms, kb, question):
    if question in atoms:
        return False
    
    new_atom = find_positive_atom(atoms, kb)
    if new_atom is None:
        return True

    return resolution_forward([new_atom, *atoms], kb, question)

def execute_test(kb, atoms, question, type):
    print("===================")
    print(f'Test: {kb + atoms}')
    print(f'The question is: {question}')
    if type == 'backward_chain':
        status = resolution_backward(kb + atoms, question)
    else:
        status = resolution_forward(atoms, kb, question)
    print(f'Status: {status}')
    if status == False:
        print('Unsatisfiable')
        print("Therefore the answer to the question is logically entailed")
    else:
        print('Satisfiable')
        print("Therefore the answer to the question is NOT logically entailed")
    print("===================")

questions = {
    'studied':'How many hours did the student study? (number of hours)',
    'participation' :'How many courses did the student participate to? (number of courses)',
    'wakesup' :'How early does the student wake up everyday? (xx:xx)',
    'dedication': 'Was the student dedicated for this exam? (yes/no)',
}

processing_answers = {
    'studied': lambda x: int(x) >= 20,
    'participation' : lambda x: int(x) >= 5 ,
    'wakesup' : lambda x: int(x.split(':')[0]) < 8,
    'dedication': lambda x: (True if x == 'yes' else False),
}

def get_answer_atoms(answers):
    atoms = []
    for key, answer in answers.items():
        if answer:
            atoms.append([key])
        else:
            atoms.append([negation(key)])
    return atoms

def main():
    horn_kb = []
    with open(FILE_NAME, 'r') as f:
        for line in f.readlines():
            line = line.rstrip()
            horn_kb = line_parser(line)
    print('The horn KB is:')
    for rule in horn_kb:
        print(rule)
    
    while True:
        print('Do you want to continue (type exit otherwise)')
        response = input()
        if response == 'exit':
            break
        answers = {}
        for key, question in questions.items():
            print(question)
            response = input(key + ":")
            answers[key] = response
        processed_answers = {key: processing_answers[key](value) for key, value in answers.items()}
        question_atoms = get_answer_atoms(processed_answers)
        combined_kb = deepcopy(question_atoms + horn_kb)
        if DEBUG:
            print(combined_kb)

        print("Output using backward chain:")
        execute_test(
            deepcopy(horn_kb), 
            deepcopy(question_atoms), 
            [negation("pass")]
            algo_type='backward_chain'
        )
        print("Output using forward chain:")
        execute_test(
            deepcopy(horn_kb), 
            deepcopy(question_atoms), 
            [negation("pass")]
            algo_type='forward_chain'
        )
    

if __name__ == '__main__':
    main()
