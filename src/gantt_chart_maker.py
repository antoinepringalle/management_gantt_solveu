import csv


class bcolors:
    HEADER = '\033[94m'
    OKGREEN = '\033[92m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'


class task:
    def __init__(self, name, dependencies, time):
        self.name = name
        self.dependencies = []
        for item in dependencies:
            if item != " " and item != ",":
                self.dependencies += [item]
        self.time = int(time)
        self.start = -1
        self.stop = -1
        self.next = []
        self.sooner_num = -1
        self.latter_num = -1
        self.sooner_date = -1
        self.latter_date = -1

    def set_time(self, start, stop):
        self.start = start
        self.stop = stop

    def add_next(self, task):
        self.next += [task]

    def planification(self, end_date, time_needed):
        months = ["jan", "fev", "mars", "avr", "mai", "juin", "juil", "août", "sept", "oct", "nov", "dec"]

        def convert_to_date(date, end_date):
            end_month, end_year = end_date
            end_months = end_month + end_year * 12
            return (months[(end_months - (time_needed - date)) % 12], (end_months - (time_needed - date)) // 12)

        latter = time_needed
        if not self.next:
            latter = time_needed
        else:
            for d in self.next:
                dep = find_task_by_name(d, tasks)
                latter = min(latter, dep.sooner_num)
        self.latter_num = latter - 1
        self.sooner_num = latter - self.time
        self.latter_date = convert_to_date(self.latter_num, end_date)
        self.sooner_date = convert_to_date(self.sooner_num, end_date)


def reading_csv_file(file):
    """
    Lit un fichier csv et retourne un tableau des tâches lues
    :param file: le fichier csv
    :return: une liste de tâches
    """
    print(bcolors.HEADER + "Ouverture du fichier csv..." + bcolors.ENDC)
    tasks = []
    with open(file=file, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:  # On ne lit pas la première ligne du fichier
            if line_count == 0:
                line_count += 1
            else:
                tasks += [task(name=row[0], dependencies=row[1], time=row[2])]
                print(
                    f"\tLa tâche {row[0]} ({row[3]}) doit être réalisée après les tâches {row[1]}. Son temps d'exécution est de {row[2]} mois.")
                line_count += 1
    print(bcolors.OKGREEN + "Lecture du fichier terminée." + bcolors.ENDC, end=" ")
    print("Il y a {lines} tâches.".format(lines=line_count - 1), end="\n\n")
    return tasks


def print_tasks(tasks):
    for task in tasks:
        # name
        print("{name} :".format(name=task.name), end=" ")

        if task.start == -1 or task.stop == -1:
            print("this task is undefined", end=" ")
        else:
            # goes to the start
            print(" " * task.start, end=" ")

            # prints the task
            print("X" * task.time, end=" ")

        # goes to the next row
        print("")


def basic_print_tasks(tasks):
    def basic_print_task(task):
        print("{name}, dep:{dep}, start:{start}, stop:{stop}, time:{time}".format(name=task.name, dep=task.dependencies,
                                                                                  start=task.start, stop=task.stop,
                                                                                  time=task.time))

    for task in tasks:
        basic_print_task(task)


def find_task_by_name(name, tasks):
    for task in tasks:
        if task.name == name:
            return task
    print("task not found")
    return ReferenceError


def process_tasks(tasks):
    """
    Définit les temps de départ et de fin des tâches d'une liste triée
    :param tasks: une liste de tâches triées par sort_tasks_dependencies
    :return: la liste mise à jour, le temps nécéssaire pour réaliser le projet
    """
    print(bcolors.HEADER + "Traitement des tâches..." + bcolors.ENDC, end=" ")
    time_needed = 0
    task_ind = 0
    while task_ind < len(tasks):
        dependencies = tasks[task_ind].dependencies
        if not dependencies:  # first task
            tasks[task_ind].set_time(start=0, stop=tasks[task_ind].time)
            time_needed = max(time_needed, tasks[task_ind].time)
        else:  # autres tâches
            # trouve la dépendance avec le temps de fin le plus élevé
            latest = 0
            for i in range(len(dependencies)):
                dep_task = find_task_by_name(dependencies[i], tasks)
                latest = max(latest, dep_task.stop)
            # définit le start et le stop de la tâche
            tasks[task_ind].set_time(start=latest, stop=latest + tasks[task_ind].time)
            time_needed = max(time_needed, dep_task.stop + tasks[task_ind].time)
        task_ind += 1
    print(bcolors.OKGREEN + "DONE" + bcolors.ENDC)
    return tasks, time_needed


def sort_tasks_dependencies(tasks):
    """
    Trie la liste de tâches de façon à ce que les tâches y1 à yn qu'il faut réaliser avant Y se trouvent devant Y dans la liste.
    :param tasks: une liste (non-triée)
    :return: une liste triée
    """
    print(bcolors.HEADER + "Tri des tâches en fonction de leurs dépendances..." + bcolors.ENDC, end=" ")
    length = len(tasks)
    sorted, sorted_names = [], []

    # fonction qui ne sert qu'à factoriser un peu le code
    def add_task(task_ind, sorted, sorted_names):
        sorted += [tasks[task_ind]]
        sorted_names += [tasks[task_ind].name]
        tasks.pop(task_ind)

    # init : les tâches qui n'ont aucune dépendance
    for task_ind in range(len(tasks) - 1):
        if not tasks[task_ind].dependencies:
            add_task(task_ind, sorted, sorted_names)

    # processing : les autres tâches
    task_ind = 0
    while len(sorted_names) < length:
        if task_ind >= len(tasks):
            task_ind = 0
        dep_names = tasks[task_ind].dependencies
        if all(elem in sorted_names for elem in dep_names):
            add_task(task_ind, sorted, sorted_names)
        task_ind += 1
    print(bcolors.OKGREEN + "DONE" + bcolors.ENDC)
    return sorted


def sort_tasks_alphabetically(tasks):
    """
    Permet de trier alphabétiquement les tâches pour l'affichage de fin.
    C'est un tri par insertion.
    :param tasks: une liste de tâches
    :return: la liste de tâches triées
    """
    print(bcolors.HEADER + "Tri des tâches alphabétiquement..." + bcolors.ENDC, end=" ")
    for i in range(1, len(tasks)):
        key_task = tasks[i]
        j = i - 1
        while j >= 0 and key_task.name < tasks[j].name:
            tasks[j + 1] = tasks[j]
            j -= 1
        tasks[j + 1] = key_task
    print(bcolors.OKGREEN + "DONE" + bcolors.ENDC)
    return tasks


def plot_tasks(tasks, time_needed):
    """
    Crée un plot du graph de Gantt correspondant au projet étudié
    :param tasks: la liste des tâches complétées
    :param time_needed: le temps pour réaliser le projet (affiché en titre de graph)
    """
    print(bcolors.HEADER + "Affichage du graph de Gantt..." + bcolors.ENDC, end=" ")
    import matplotlib.pyplot as plt
    length = len(tasks)
    fig, gnt = plt.subplots()
    gnt.set_xlabel('Mois')
    gnt.set_ylabel('Tâches')
    plt.title('Temps nécéssaire = {time} mois'.format(time=time_needed))
    gnt.set_yticks([length * 10 + 5 - i * 10 for i in range(length)])
    gnt.grid(True)
    this_task = 0
    labels = []
    for task in tasks:
        gnt.broken_barh([(task.start, task.time)], (length * 10 - this_task * 10, 9), facecolors=('tab:blue'))
        labels += [task.name]
        this_task += 1
    gnt.set_yticklabels(labels)
    print(bcolors.OKGREEN + "DONE" + bcolors.ENDC)
    plt.savefig("figure.png")
    plt.show()


def planification_au_plus_tard(tasks, end_date, time_needed):
    """
    Calcule la planification au plus tard d'un projet
    :param tasks: les tâches
    :param end_date: la date de fin du projet : 07/2020 pour juillet 2020
    :param time_needed: le temps nécéssaire pour réaliser le projet (calculé précédemment)
    :return: un beau tableau
    """
    print(bcolors.HEADER + "Planification au plus tard" + bcolors.ENDC)

    def definir_suivantes(tasks):
        for task in tasks:
            dependencies = task.dependencies
            for d in dependencies:
                dep = find_task_by_name(d, tasks)
                dep.add_next(task.name)

    definir_suivantes(tasks)
    tasks.reverse()
    for task in tasks:
        task.planification(end_date, time_needed)
    planification = []
    for task in tasks:
        planification += [[task.name, task.next, task.time, task.sooner_date, task.latter_date]]
    from tabulate import tabulate
    print(tabulate(planification, headers=['Tâche', 'Suivantes', 'Durée', 'Début au plus tard', 'Fin au plus tard']))
    print(bcolors.OKGREEN + "DONE" + bcolors.ENDC)


if __name__ == "__main__":
    tasks = reading_csv_file("../data_tasks.csv")

    # GANTT
    tasks = sort_tasks_dependencies(tasks)
    tasks, time_needed = process_tasks(tasks)
    tasks = sort_tasks_alphabetically(tasks)
    plot_tasks(tasks, time_needed)

    # PLANIFICATION AU PLUS TARD
    end_date = (7, 2017)  # juillet 2017
    planification_au_plus_tard(tasks, end_date, time_needed)
