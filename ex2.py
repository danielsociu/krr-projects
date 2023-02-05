import numpy as np
import matplotlib.pyplot as plt

FILE_NAME='ex2_input.txt'
PLOTTING=True
SHOW=True
DEBUG=False

def real_score(key, value):
    if key == "outside":
        return value - 20
    else:
        return value + 10

def line_parser(line):
    rules = []
    line = line[1:-1]
    length = len(line)
    index = 0
    cur_str = ''
    while index < length:
        if line[index] == '[':
            rules.append([])
        elif line[index] ==  ']' or line[index] == ',':
            if cur_str != '':
                if len(rules):
                    rules[-1].append(cur_str)
                else:
                    rules.append(cur_str)
            cur_str = ''
        else:
            cur_str = cur_str + line[index]
        index += 1

    return rules

def my_linspace(start, end, elements):
    if elements == 1:
        return np.array([max(start,end)])
    return np.linspace(start, end, elements)

def plot_all(predicate, show=False):
    for key, curve in predicate.items():
        curve.plot_curve(show)

class Antecedent():
    def __init__(self, x, start_low, end_low, start_high, end_high, name='default'):
        self.start_low = start_low
        self.end_low = end_low
        self.start_high = start_high
        self.end_high = end_high
        self.name=name
        self.x = x
        self.curve = np.concatenate([
            np.zeros(start_low),
            my_linspace(0, 1, end_low - start_low + 1),
            np.ones(max(start_high - end_low - 1, 0)),
            my_linspace(1, 0, end_high - start_high + 1),
            np.zeros(max(len(x) - end_high - 1, 0))
        ])
        if (start_high - end_low) == 0:
            self.curve = np.delete(self.curve, [end_low + 1])
    
    def get_curve_value(self, score):
        value = 0
        if int(score) != score:  
            prior = int(score)
            next = prior + 1
            v1 = self.curve[prior]
            v2 = self.curve[next]
            if v1 < v2:
                x_dist = abs(prior - score)
            else:
                x_dist = abs(next - score)
            value = abs(v1 - v2) * x_dist + min(v1, v2)
        else:
            value = self.curve[int(score)]

        return value

    def calculate_antecedent(self, score):
        value = self.get_curve_value(score)
        antecedent = np.zeros(len(self.curve))
        for i in range(len(self.curve)):
            antecedent[i] = min(self.curve[i], value)

        return np.array(antecedent)

    def calculate_consequent(self, value):
        antecedent = np.zeros(len(self.curve))
        for i in range(len(self.curve)):
            antecedent[i] = min(self.curve[i], value)

        return antecedent

    
    def plot_curve(self, show=False):
        plt.plot(self.x, self.curve, label=self.name)
        title = self.name.replace("/", "_")
        plt.title(title)
        plt.savefig('plots/' + title + '.png')
        if show:
            plt.show()
        plt.close()
    
    def plot_antecedent(self, score, show=False):
        antecedent = self.calculate_antecedent(score)
        base = np.zeros_like(antecedent)
        plt.fill_between(self.x, base, antecedent)
        plt.plot(self.x, self.curve, label=self.name)
        title = self.name.replace("/", "_") + "antecedent_" + str(score) 
        plt.title(title)
        plt.savefig(
            'plots/' + 
            title +
            '.png'
        )
        if show:
            plt.show()
        plt.close()


    
outside = {
    "cold": Antecedent(np.arange(0, 61, 1), 0, 0, 0, 30, 'outside/cold'),
    "average": Antecedent(np.arange(0, 61, 1), 0, 30, 30, 60, 'outside/average'),
    "hot": Antecedent(np.arange(0, 61, 1), 30, 60, 60, 60, 'outside/hot'),
}

desired = {
    "low": Antecedent(np.arange(0, 21, 1), 0, 0, 0, 10, 'desired/low'),
    "medium": Antecedent(np.arange(0, 21, 1), 0, 10, 10, 20, 'desired/medium'),
    "high": Antecedent(np.arange(0, 21, 1), 10, 20, 20, 20, 'desired/high'),
}

heating = {
    "low": Antecedent(np.arange(0, 11, 1), 0, 0, 0, 5, 'heating/low'),
    "medium": Antecedent(np.arange(0, 11, 1), 0, 5, 5, 10, 'heating/medium'),
    "high": Antecedent(np.arange(0, 11, 1), 5, 10, 10, 10, 'heating/high'),
}

def evaluate_antecedents(rule, scores, multiple_antecedents):
    antecedents = {}
    if multiple_antecedents:
        for ant_str in rule[1]:
            pred, pred_type = ant_str.split('/')
            pred_func = eval(pred)
            value = pred_func[pred_type].get_curve_value(scores[pred])
            antecedents[ant_str] = value
        if rule[0] == 'or':
            result = 0
            for key, antecedent in antecedents.items():
                result = max(result, antecedent)
        else:
            result = 1
            for key, antecedent in antecedents.items():
                result = min(result, antecedent)
    else:
        pred, pred_type = rule[0][0].split('/')
        pred_func = eval(pred)
        value = pred_func[pred_type].get_curve_value(scores[pred])
        antecedents[rule[0][0]] = value
        result = value
    return result, antecedents

def evaluate_rule(rule, scores):
    multiple_antecedents = type(rule[0]) is str
    
    antecedent_result, antecedents = evaluate_antecedents(rule, scores, multiple_antecedents)
    conseq_str, conseq_type = rule[-1][0].split('/')
    conseq_func = eval(conseq_str)
    consequent = conseq_func[conseq_type].calculate_consequent(antecedent_result)

    return {rule[-1][0]: consequent}, antecedents

def aggregate_consequents(consequents):
    aggregated_conseq = np.zeros(len(next(iter(consequents.values()))))
    for key, conseq in consequents.items():
        aggregated_conseq = np.fmax(aggregated_conseq, conseq)
    
    return aggregated_conseq

    
def plot_aggregated_conseq(aggregated_conseq, predicates, scores, show=False):
    for key, pred in predicates.items():
        plt.plot(pred.x, pred.curve, 'r', label=pred.name)
    
    zeros = np.zeros_like(pred.x)
    plt.fill_between(pred.x, zeros, aggregated_conseq, alpha=0.5)

    title = 'Aggregated conseq ' + ' '.join(f'{key}={real_score(key, score)}' for key, score in scores.items())
    plt.title(title)
    plt.savefig('plots/' + title.replace(" ", "_") + '.png')
    if show:
        plt.show()
    plt.close()


def defuse(aggregated_conseq, method='centroid'):
    numerator, denominator = 0, 0
    for x, f_x in enumerate(aggregated_conseq):
        numerator += x * f_x
        denominator += f_x
    return numerator / denominator


def main():
    if PLOTTING:
        plot_all(outside)
        plot_all(desired)
        plot_all(heating)

    rules = []
    with open(FILE_NAME, 'r') as f:
        for line in f.readlines():
            line = line.rstrip()
            rule = line_parser(line)
            rules.append(rule)

    print('rules are:')
    for rule in rules:
        print(rule)
    # service['good'].plot_antecedent(1.5, show=True)
    scores = {}
    while True:
        print('Insert scores or type exit to stop:')
        initial_input = input("Outside temp (-20 to 40):")
        if initial_input == 'exit':
            break
        scores['outside'] = float(initial_input) + 20.
        scores['desired'] = float(input("Desired temp (10 - 30):")) - 10
        consequents = {}
        for rule in rules:
            consequent, antecedents = evaluate_rule(rule, scores)
            consequents |= consequent
            if DEBUG:
                print(antecedents)
        aggregated_consequents = aggregate_consequents(consequents)
        if DEBUG:
            print(aggregated_consequents)
        if PLOTTING:
            plot_aggregated_conseq(aggregated_consequents, heating, scores, show=SHOW)
        defused_value = defuse(aggregated_consequents)
        print(f"The output is {defused_value}")

if __name__ == '__main__':
    main()
