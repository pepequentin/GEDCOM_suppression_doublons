import chardet
import argparse


class Individu:
    def __init__(self, id):
        self.id = id
        self.name = None
        self.data = []

def parse_degcom(file_path):
    individus = {}
    header = []
    current_individual = None
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith("0 @I"):
                if current_individual is not None:
                    individus[current_individual.id] = current_individual
                current_individual = Individu(line.split('@')[1])
            elif current_individual is not None:
                if current_individual.name is None and line.startswith("1 NAME"):
                    current_individual.name = line.split("1 NAME ")[1]
                current_individual.data.append(line)
            else:
                header.append(line)
    if current_individual is not None:  # Handle the last individual in the file
        individus[current_individual.id] = current_individual

    return header, individus


def generate_gedcom(header, individus, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for line in header:
            file.write(f"{line}\n")
        for id, individu in individus.items():
            file.write(f"0 @I{id}@ INDI\n")
            for data_line in individu.data:
                file.write(f"{data_line}\n")

def trouver_id_plus_de_data_par_nom(individus, ids):
    max_data_id = None
    max_data_length = 0
    for id in ids:
        if len(individus[id].data) > max_data_length:
            max_data_length = len(individus[id].data)
            max_data_id = id
    return max_data_id, max_data_length


def remplacer_id_dans_data(individus, id_a_supprimer, id_max_data):
    for individu in individus.values():
        for i in range(len(individu.data)):
            if f"@{id_a_supprimer}@" in individu.data[i]:
                individu.data[i] = individu.data[i].replace(f"@{id_a_supprimer}@", f"@{id_max_data}@")

def supprimer_individus_non_max_data_par_nom(individus):
    noms_ids = {}
    for id, individu in individus.items():
        if individu.name is not None:
            if individu.name in noms_ids:
                noms_ids[individu.name].append(individu.id)
            else:
                noms_ids[individu.name] = [individu.id]
    
    for nom, ids in noms_ids.items():
        if len(ids) > 1:
            id_max_data, max_data_length = trouver_id_plus_de_data_par_nom(individus, ids)
            for id in ids:
                if id != id_max_data:
                    remplacer_id_dans_data(individus, id, id_max_data)
                    del individus[id]
    return individus

def parse_args():
    parser = argparse.ArgumentParser(description="Programme de traitement de fichier GEDCOM")
    parser.add_argument("--input-file", dest="input_file", required=True, help="Chemin du fichier d'entrée GEDCOM")
    parser.add_argument("--output-file", dest="output_file", required=True, help="Chemin du fichier de sortie GEDCOM")
    return parser.parse_args()

def main():
    args = parse_args()
    input_file = args.input_file
    output_file = args.output_file
    
    header, individus = parse_degcom(input_file)

    individus = supprimer_individus_non_max_data_par_nom(individus)

    generate_gedcom(header, individus, output_file)

    print(f"Fichier d'entrée : {input_file}")
    print(f"Fichier de sortie : {output_file}")

if __name__ == "__main__":
    main()
